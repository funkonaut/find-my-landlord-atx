import json

def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        feature['geometry']['coordinates'] = [row[lon],row[lat]]
        for prop in properties:
            feature['properties'][prop] = row[prop]
        geojson['features'].append(feature)
    return geojson

df_aff = pd.read_csv('../land_lord_locate/dedupe-examples/csv_example/trial4.csv')

#Mask out properties not in city ie council districts
gdfdist = geopandas.read_file('../data_laundry/districts/geo_export_74417697-1c4c-4575-bf46-90c0ce62509c.shp')
polys = gdfdist.geometry
coor_to_geometry(df_aff,['X_x','Y_x'])
df_aff = geopandas.GeoDataFrame(df_aff)
df_aff = df_aff.assign(**{str(key): df_aff.geometry.within(geom) for key, geom in polys.items()})
df_aff = df_aff.loc[df_aff['0']|df_aff['1']|df_aff['2']|df_aff['3']|df_aff['4']|df_aff['5']|df_aff['6']|df_aff['7']|df_aff['8']|df_aff['9']]
clean_up(df_aff,['0','1','2','3','4','5','6','7','8','9'],delete=True)

#Throw out lots
clean_up(gdf,['property_i','land_use'])
df_aff.prop_id = df_aff.prop_id.astype(str)
res_code = [np.nan,'100','113','150','160','210','220','230','240','330']
df_aff = df_aff.merge(gdf,left_on='prop_id',right_on='property_i',how='left').drop_duplicates('prop_id')

#Merge in more TCAD info
col_specs = [(0,12),(1675,1685),(1685,1695),(1139,1149)]
df_tcad = pd.read_fwf('../data_laundry/TCAD/PROP.TXT',col_specs)
df_tcad.columns = ['prop_id','sub_div','hood','zip']
df_aff.prop_id = df_aff.prop_id.astype(int)
df_aff = df_aff.merge(df_tcad,on='prop_id',how='left').drop_duplicates(subset='prop_id')

#Keep known units
clean_up(gdf_16,['units','prop_id'])
gdf_16['known']= np.where(gdf_16.units>0, True,False)
df_aff = df_aff.merge(gdf_16,on='prop_id',how='left').drop_duplicates(subset='prop_id')
df_aff.known.fillna(False,inplace=True)
df_aff.units_x_x = np.where((df_aff.known==False)&(df_aff.units_x_x==1),np.nan,df_aff.units_x_x) #take out estimations
#add in subdivision data
#df_aff.to_csv('./units.csv',columns=['value','units','units_x_x','sub_div','prop_id'],index=False)
#Calculate average price per unit in subdivision
df_aff_known = df_aff.loc[df_aff.units_x_x.notnull()]  
df_aff = pd.DataFrame(df_aff_known.groupby('sub_div').apply(lambda x: x.sum().value/x.sum().units_x_x)).merge(df_aff,right_on='sub_div',left_index=True, how='right')
df_aff.rename(columns={ df_aff.columns[0]: "unit_val_sub" }, inplace = True)
df_aff = pd.DataFrame(df_aff_known.groupby('hood').apply(lambda x: x.sum().value/x.sum().units_x_x)).merge(df_aff,right_on='hood',left_index=True, how='right')
df_aff.rename(columns={ df_aff.columns[0]: "unit_val_hood" }, inplace = True)
df_aff = pd.DataFrame(df_aff_known.groupby('zip').apply(lambda x: x.sum().value/x.sum().units_x_x)).merge(df_aff,right_on='zip',left_index=True, how='right')
df_aff.rename(columns={ df_aff.columns[0]: "unit_val_zip" }, inplace = True)

#Estimate unit size based on known sub division 
df_aff.units_x_x = np.where((df_aff.value>75000)&(df_aff.units_x_x.isnull()), round(df_aff.value/df_aff.unit_val_sub), df_aff.units_x_x)

df_aff.units_x_x.fillna(round(df_aff.value/df_aff.unit_val_hood),inplace=True)
df_aff.units_x_x.fillna(round(df_aff.value/df_aff.unit_val_zip),inplace=True)

#ALSO MAKE SURE TO CLEANUP ADDRESS TO LOOK GOOD IE STRIP WHITE SPACES
df_aff.address = df_aff.address.str.rstrip()
df_aff.address = df_aff.address.str.lstrip()
df_aff.address = df_aff.address.str.replace(' +',' ')
df_aff.owner_add = df_aff.owner_add.str.rstrip()
df_aff.owner_add = df_aff.owner_add.str.lstrip()
df_aff.owner_add = df_aff.owner_add.str.replace(' +',' ')

#MAYBE DROP NULL LOCATION IN DF_AFF!!!! AFTER DONE PROCESSING SINCE WE CANT DISPLAY THOSE ANYWAYS
#4.6k props lost :( 
df_aff.dropna(subset=['X_x','Y_x'], inplace=True)

clean_up(df_aff,['confidence_score','mail_add_1','mail_add_2','mail_add_3','value'],delete=True)
df_aff.columns = ["aff_id","Property Index Number","Taxpayer Match Code","Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','X','Y']
df_aff.columns = ["Taxpayer Match Code","Property Index Number","Taxpayer Match Code (TCAD)","Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','X','Y']
df_aff['Properties Held by Taxpayer Match Code'] = df_aff.groupby('aff_id')['aff_id'].transform('count')
df_aff['Additional Details']= ''

#Clean up from upper case to Title
df_aff['Taxpayer']         = df_aff['Taxpayer'].apply(lambda x: " ".join(w.capitalize() for w in x.split()))
df_aff['Property Address'] = df_aff['Property Address'].apply(lambda x: " ".join(w.capitalize() for w in x.split()))
df_aff['Affiliated With']  = df_aff['Affiliated With'].apply(lambda x: " ".join(w.capitalize() for w in x.split()))
df_aff['Property Address'] = df_aff['Property Address'].str.replace('00000','')

#Get rid of nans will not upload to firebase with nans
df_aff.dropna(inplace=True)
df_aff['Property Index Number']=df_aff['Property Index Number'].astype(str)
df_aff['Taxpayer Match Code'] = df_aff['Taxpayer Match Code'].astype(str)
df_aff['Property Address'] = df_aff['Property Address'].str.rstrip()

#dfs = np.array_split(df_aff, 20)

#Build search index CAN POSSIBLY JUST DO THIS FOR ALL? 
df_search = pd.DataFrame(df_aff, columns = ['Property Index Number','Property Address'])
df_search['Property Index Number'] = df_search['Property Index Number'].astype(str)  
df_search = df_search[['Property Address','Property Index Number']]
df_search.to_json('search_index.json',orient='records')

#Build map tiles and database 
gdf1 = df_to_geojson(df_aff,["Property Index Number","Taxpayer Match Code","Taxpayer","Property Address",'Affiliated With','Unit Count from Department of Buildings','Properties Held by Taxpayer Match Code', 'Additional Details'],lat='Y',lon='X')
with open('outputmap.geojson', 'w') as fp:
    json.dump(gdf1,fp)


