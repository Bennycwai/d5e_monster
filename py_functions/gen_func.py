import json
import numpy as np
import pandas as pd
import urllib.request
from PIL import Image
import glob

def read_data(file_location, json_file):
    ## read the monsters from the SRD
    with open('raw_data/srd_5e_monsters.json') as f:
      raw_data = json.load(f)
    
    df = pd.json_normalize(raw_data)
    
    return df

def read_and_clean(file_location, json_file):
    
    ## read the monsters from jupyter notebook
    df = read_data(file_location, json_file)
    
    ### clean the name column (replacing spaces with '_'s) and break meta into 4 seperate columns

    ## get name, lower case and _ between words
    clean_df = pd.DataFrame(df['name'].str.lower().str.replace(' ','_').str.replace('/','_').str.replace('(','_')
                            .str.replace(')','_'), columns = ['name'])

    ## split the size and type
    clean_df = pd.concat([clean_df,pd.DataFrame(
                pd.DataFrame(
                    df['meta'].str.split(', ').tolist()
                    , columns = ['creature_info','alignment'])
                        ['creature_info'].str.split(' ').tolist()
                            , columns = ['size','type'])], axis=1)

    ## create alignment column to be split later, first deal with outliers
    clean_df = pd.concat([clean_df,
                pd.DataFrame(pd.DataFrame(
                    df['meta'].str.split(', ').tolist()
                    , columns = ['creature_info','alignment'])['alignment'])], axis=1)
    when_conditions = [clean_df['alignment'] == 'unaligned',clean_df['alignment'] == 'any', clean_df['alignment'] == 'neutral', clean_df['alignment'] == 'any evil alignment']
    then_statements = ['unaligned unaligned','any any','neutral neutral','any evil']
    clean_df['alignment'] = np.select(when_conditions,then_statements, default=clean_df['alignment'])

    ## split the alignment column
    clean_df = pd.concat([clean_df,
                pd.DataFrame(
                    clean_df['alignment'].str.split(' ').tolist()
                    , columns = ['ethics','moral'])], axis=1)
    clean_df = clean_df.drop(['alignment'], axis = 1)

    ## lower case all current columns
    clean_df = clean_df.apply(lambda x: x.astype(str).str.lower())

    clean_df = pd.concat([clean_df,df.drop(['name','meta'],axis=1)],axis=1)
    
    
    return clean_df

### define function for saving images into folder
def save_img_from_url(x):
    urllib.request.urlretrieve(x['img_url'], "images/monsters/"+x['name']+".jpeg")
    
## create function to identify list monsters for to be replaced
def check_for_missing(monster_folder, template_folder):
    missing_name_list = []
    
    ## create list of all image names from both folders
    template_list = glob.glob(template_folder+"*.jpeg")
    monster_list = glob.glob(monster_folder+"*.jpeg")
    
    for monster_index in range(len(monster_list)):
        for template_index in range(len(template_list)):
            if (open(monster_list[monster_index],"rb").read() == open(template_list[template_index],"rb").read()):
                missing_name_list.append(monster_list[monster_index].split('\\')[1].split('.')[0])
    
    return missing_name_list

