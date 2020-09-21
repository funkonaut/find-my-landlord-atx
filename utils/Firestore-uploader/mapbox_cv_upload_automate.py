####################CODE VIOLATIONS DATA PIPELINE##############################
# MUST BE UTILS Firebase upload FOLDER TO WORK CORRECTLY 
# DOWNLOADS code data and uploads to mapbox and fire base for use
# Mapbox: crcorrell.code_map name: original
# has number of code complaints should I include more data?
# Firebase: code_complaint 
# has number of code complaints


import pandas as pd
import os
import json
import numpy as np

def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        feature['geometry']['coordinates'] = [float(row[lon]),float(row[lat])]
        for prop in properties:
            if row[prop] != np.nan:
                feature['properties'][prop] = row[prop]
            else:
                feature['properties'][prop] = 'Info Not Availble'
        geojson['features'].append(feature)
    return geojson


#Curl data from https://data.austintexas.gov/City-Government/Austin-Code-Complaint-Cases/6wtj-zbtb
#Read in file and the delete it 
url = 'https://data.austintexas.gov/api/views/6wtj-zbtb/rows.csv\?accessType\=DOWNLOAD'
fn = 'code.csv'
os.system('curl '+url+' -o '+ fn)
df_code = pd.read_csv(fn) 

#Clean up data and tally total complaint numbers
df_code['numbers'] = df_code.groupby(['LONGITUDE','LATITUDE'])['CASE_ID'].transform('count')
df_code.drop_duplicates(['LONGITUDE','LATITUDE'],inplace=True)
df_code2 = df_code[['ADDRESS_LONG','LONGITUDE','LATITUDE','numbers']]

#Drop nulls and replace missing addresses
df_code2.ADDRESS_LONG.replace(np.nan,'MISSING ADDRESS',inplace=True)
df_code2 = df_code2.loc[df_code2.numbers.notnull()]
df_code2['ADDRESS_LONG'] = df_code2.ADDRESS_LONG.apply(lambda x:  " ".join(w.capitalize() for w in x.split()))

#Output map (geojson file)
gdf = df_to_geojson(df_code2,['ADDRESS_LONG','numbers'],lat='LATITUDE',lon='LONGITUDE')
fn_o = 'outputmap_code.geojson'
with open(fn_o, 'w') as fp:
    json.dump(gdf,fp)

#upload to mapbox via curl https://docs.mapbox.com/help/tutorials/upload-curl/ check file using geojsonhint cmd tool?
#Stage file on AWS 
token = 'FILL ME IN'
user = 'FILL ME IN'
fn_aws =  'aws_output.json'
os.system('curl -X POST https://api.mapbox.com/uploads/v1/'+user+'/credentials?access_token='+token+' -o '+fn_aws)
with open(fn_aws) as f:
  data_aws = json.load(f)

os.environ['AWS_ACCESS_KEY_ID'] = data_aws['accessKeyId']
os.environ['AWS_SECRET_ACCESS_KEY'] = data_aws['secretAccessKey']
os.environ['AWS_SESSION_TOKEN'] = data_aws['sessionToken']
os.system('aws s3 cp ' + fn_o + ' s3://' + data_aws['bucket'] + '/' + data_aws['key'] + ' --region us-east-1')

#Upload staged file to mapbox
map_data = '\'{ \"url\": \"http://' + data_aws['bucket'] + '.s3.amazonaws.com/' + data_aws['key'] + '\", \"tileset\": \"' + user + '.code_map\"}\''
os.system('curl -X POST -H \"Content-Type: application/json\" -H \"Cache-Control: no-cache\" -d ' + map_data +  ' \'https://api.mapbox.com/uploads/v1/' + user + '?access_token=' + token + '\'')

#Upload file to firebase 
#create file from gdf and call it code
gdf_code = {"code_complaint":  gdf['features'] }
fn_fb = './features.json'
with open(fn_fb, 'w') as fp:
    json.dump(gdf_code,fp)

os.system('node ./import.js')

#Clean up
os.system('rm ' + fn)
os.system('rm ' + fn_o)
os.system('rm ' + fn_aws)
