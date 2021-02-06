import json
import numpy as np
import pandas as pd
import urllib.request
from PIL import Image
import glob

def read_data():
    ## read the monsters from the SRD
    with open('raw_data/srd_5e_monsters.json') as f:
      raw_data = json.load(f)
    
    df = pd.json_normalize(raw_data)
    
    return df