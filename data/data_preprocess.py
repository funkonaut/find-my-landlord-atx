import pandas as pd
import geopandas
import numpy as np
from shapely import wkt

#####################
###   CODE INFO   ###
######################
#This code compiles all the city data sets
#into one that has the following properties
# "Property Address"
# "Community Area"
# "Property Index Number"
# "Taxpayer"
# "Taxpayer Match Code"
# "Affiliated With"
# "Additional Details"
# "Properties Held by Taxpayer Match Code"
# "Unit Count from Department of Buildings"
# "Relative Size"

#######################
###    DATA SETS    ###
#######################
#df_tcad:   all appraisal data not geo located no unit numbers unique: prop_id, py_owner_i 
#df_units:  unit estimates based on improvement data (only includes properties that have been improved) unique: prop_id
#gdf:       location of all building and land coding from land use code (does not locate properties just parcels) uniqe:property_i (prop_id)
#gdf_16     complete data set from 2016 used to fill in missing unit info owner info of old properties unique(prop_id) 
#df_locs:   location data from city unique: PROP_ID
#df_code:   code violations unique: LATITUDE,LONGITUDE
#df_fill:   census scraped locations

def clean_up(df,cols=[] ,delete=False):
    if delete:
        for col in cols:
            del df[col]
    else:
        for col in df.columns:
            if col not in cols:
                del df[col] 

###TEST THAT UNKNOWN IS NAN ******
#extract year from float date (col) and create new column if property is newer then 2016
def extract_new_props(df,col):
    df[col]= df[col].astype(str).str[-4:-2]
    df[col].replace('n',21,inplace=True)    #assume nulls are new unit proven otherwise
    df[col] = df.loc[df[col].notnull()][col].astype(int)
    df['new'] = np.where((df[col]>16) , True, False)
    df['new'] = np.where((df[col]==21) , np.nan, df.new)
 
def extract_nums(df,col):
   if col !='type1':
       return df[col].str.extract('(\d+)').astype(float) 
   else:     
       df['units'] = df[col].str.extract('(\d+)').astype(float) 
       single = ['GARAGE APARTMENT','Accessory Dwelling Unit','Accessory Dwelling Unit (', 'MOHO SINGLE PP','TOWNHOMES','MOHO SINGLE REAL','']
       double = ['MOHO DOUBLE REAL', 'MOHO DOUBLE PP']
       triple = 'TRIPLEX'
       quad = 'FOURPLEX'
       for key in single: df['units'] = df_units.apply(lambda row: 1 if row.type1 == key else row['units'], axis=1)
   
       for key in double: df['units'] = df_units.apply(lambda row: 2 if row.type1 == key else row['units'], axis=1)
      
       df['units'] = df.apply(lambda row: 3 if row.type1 == triple else row['units'], axis=1)
       df['units'] = df.apply(lambda row: 4 if row.type1 == quad else row['units'], axis=1)

def replace_nan(df,cols=[],val=0,reverse=False):
    if not reverse:
        for col in cols:
            df[col].replace(np.nan,val,inplace=True)
    else:
        for col in cols:
            df[col].replace(val,np.nan,inplace=True)    

def convert_to_numeric(df, col):
    #extract first group of number in string maybe improve so it caputres all numbers
    num = extract_nums(df,col)
    replace_nan(num,num.columns)
    try:
       return num.astype(int)
    except ValueError:
       print(ValueError)

#concatenates string columns with empty values           
def combine_string_cols(df,cols=[],out='out'):
    replace_nan(df,cols,val='',reverse=False)        
    address = ''
    for col in cols:
        address += df[col].astype(str) + ' '
    df[out]=address#.apply(lambda x: pyap.parse(x, country='US'))

#extract coordinates from geopandas frame
def extract_coor(gdf,col='geometry',out=['X','Y']):
    try:
        gdf[out[0]]=gdf[col].centroid.x
        gdf[out[1]]=gdf[col].centroid.y
    except:
        gdf[out[0]]=gdf[col].x
        gdf[out[1]]=gdf[col].y

def coor_to_geometry(df,col=['X','Y'],out='geometry'):
    df[out]=geopandas.points_from_xy(df[col[0]],df[col[1]])

#merge on value (df2 + df3) + df1 (origin)
def merge_extraction(dfs=[],on='prop_id',val=['units']):
    df2_cp = dfs[1].copy()  #copy datasets so no info is lost
    df3_cp = dfs[2].copy()
    clean_up(df2_cp,[on]+val)  #cleanup all values out of datasets to extract info from
    clean_up(df3_cp,[on]+val)  #cleanup all values out of datasets to extract info from
    df3_cp = df3_cp.merge(df2_cp,on=on,how='outer')
    return dfs[0].merge(df3_cp,on=on,how='left') #keep all values from original data frame don't care about values not in org

def fill_in_locs(df):
    df2 = pd.DataFrame(columns=df.columns)
    df_add = df.groupby('address')
    for add,df in df_add:
        if df.X_x.notnull().any() and len(df.index)>1:
            df.sort_values(by='X_x',inplace=True)
            df.fillna(method='ffill',inplace=True)
            df2 = df2.append(df)
    return df2

def find_missing(df,col):
    return df.loc[df[col].isnull()]


########################
### Data pre-process ###
########################
#Clean up gdfs
clean_up(gdf,['parcel_id_','created_by','date_creat','time_creat','general_la','modified_b','date_modif','time_modif','objectid','land_use_i'],True)
clean_up(gdf_16,['py_owner_i','shape_area','lotsize','units','dba','owner','prop_id','situs','geometry'])

combine_string_cols(df_tcad,['st_number','prefix','st_name','suffix'],'ADDRESS_LONG')
combine_string_cols(df_tcad,['st_number','prefix','st_name','suffix','city','zip'],'address')
combine_string_cols(df_tcad,['mail_add_1','mail_add_2','mail_add_3','mail_city','mail_state','mail_zip'],'owner_add')
replace_nan(df_tcad,['address','owner_add'],val='      ',reverse=True)

df_tcad.ADDRESS_LONG = df_tcad.ADDRESS_LONG.str.replace(' ','')
df_code.ADDRESS_LONG = df_code.ADDRESS_LONG.str.replace(' ','')

#Convert numberic data to ints st_number will lose some unit info or fraction info 
df_tcad['st_number_int'] = convert_to_numeric(df_tcad,'st_number')
df_tcad['zip']       = convert_to_numeric(df_tcad,'zip')
df_tcad['mail_zip']  = convert_to_numeric(df_tcad,'mail_zip')
df_tcad['geo_id']    = convert_to_numeric(df_tcad,'geo_id')
gdf_16['prop_id']    = gdf_16['prop_id'].astype(int) 
gdf['prop_id']       = convert_to_numeric(gdf,'property_i')

#****MAYBE CAN GET RID OF MORE**** Get rid of rows with no useful info
gdf_16 = gdf_16.loc[gdf_16.prop_id!=0]
gdf    = gdf.loc[gdf.property_i!=0]

########################
###Feature extraction###
########################
extract_nums(df_units,'type1')
#modularize this better for later***
df_units.replace(np.nan,0,inplace=True)
df_sum = pd.DataFrame(df_units.groupby(by='prop_id').sum())
df_units = df_units.merge(df_sum,left_on='prop_id',right_index=True,how='outer') #did this drop any? or add any changed to outer 
df_units.drop_duplicates('prop_id',inplace=True)
del df_units['units_y']
df_units.columns=['type1','prop_id','units']
df_units.replace(0,np.nan,inplace=True)
extract_new_props(df_tcad,'deed')

#Residential properties
res = ['A1','A2','A3','A4','A5','B1','B2','B3','B4','F4','O1']
df_tcad['res'] = df_tcad.code.isin(res)|df_tcad.code2.isin(res)|df_tcad.code3.isin(res)
extract_coor(gdf)
extract_coor(gdf_16)
coor_to_geometry(df_locs)
coor_to_geometry(df_code,['LONGITUDE','LATITUDE'])

########################
### Feature combine  ###
########################
#Combine Units:
df_tcad = merge_extraction(dfs=[df_tcad,df_units,gdf_16])
replace_nan(df_tcad,['units_x','units_y'],val=0,reverse=True)
df_tcad.units_x.fillna(df_tcad.units_y,inplace=True)
#Fill in missing 2016 data with estimates and fill in outdated 2016 estimates with larger numbers
df_tcad.units_x = np.where(df_tcad.units_x < df_tcad.units_y, df_tcad.units_y, df_tcad.units_x)
del df_tcad['units_y']

#Combine Locations:
df_tcad = merge_extraction(dfs=[df_tcad,gdf,df_locs],on='prop_id',val=['X','Y'])
df_tcad.X_y.fillna(df_tcad.X_x,inplace=True)
df_tcad.Y_y.fillna(df_tcad.Y_x,inplace=True)
df_tcad.Y_x.fillna(df_tcad.Y_y,inplace=True)
df_tcad.X_x.fillna(df_tcad.X_y,inplace=True)
del df_tcad['X_y']
del df_tcad['Y_y']


########################
###  HANDLE MISSING  ###
########################
#Fill in based on data set
#TRY AND FIX THIS????
#df_miss = find_missing(df_tcad,'X_x') 
#df = df_tcad.loc[df_tcad.address.isin(df_miss.address)]
##df2 = fill_in_locs(df)
#df_tcad.X_x.fillna(df2.X_x,inplace=True)
#df_tcad.Y_x.fillna(df2.Y_x,inplace=True)

#Fill in based on geocoding census 
df_miss = find_missing(df_tcad,'X_x') 
df_miss['state']='TX'
df_miss.to_csv('./bulk_all.csv',columns=['address','city','state','zip'])
exec(open('geocode.py').read()) #change this next line to point to /geocode/combined_results.csv MAKE SURE GEOCODE DIR IS EMPTY BEFORE DOING THIS!!!!
df_fill = pd.read_csv('./geocode/combined_results.csv')
del df_fill['Unnamed: 0']
df_fill = df_fill.merge(pd.DataFrame(df_fill.Loc.str.split(',',expand=True)),left_index=True,right_index=True)
df_fill.Addres_m.fillna(df_fill.Address,inplace=True)
df_fill.rename(index=df_fill.Idx,inplace=True)
clean_up(df_fill,cols=[0,1,'Addres_m'])
df_fill.columns = ['Address','X','Y']
df_tcad.X_x.fillna(df_fill.X,inplace=True)
df_tcad.Y_x.fillna(df_fill.Y,inplace=True)x
