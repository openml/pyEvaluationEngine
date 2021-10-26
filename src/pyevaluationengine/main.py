import openml.datasets as dt
from pymfe.mfe import MFE
import arff
import pandas as pd
import numpy as np
import requests
import json
import os

api_key = "07ba2f75d031ff6997b8f93d466f1f1e"


#get url
def getUrl(data):
    return data['data_set_description']['url']


#get unprocessed data ids
def getDataIds():
    response = requests.get("https://test.openml.org/api/v1/json/data/unprocessed/0/normal", params={'api_key':api_key})
    datasets = json.loads(response.text)
    dataids = []
    for key in datasets['data_unprocessed']: 
        dataids.append(datasets['data_unprocessed'][key]['did'])
    return dataids

#downloads dataset and stores as temp.arff
def downloadDataset(id):
    response = requests.get("https://test.openml.org/api/v1/json/data/"+id, params={'api_key':api_key})
    url = getUrl(json.loads(response.text))
    open('temp.arff', 'wb').write(requests.get(url).content)

def extractFeatures(id):
    #extract features
    dsd = dt.get_dataset(id) # dataset discription
    default_target = dsd.default_target_attribute
    X,y,categorical_indicator,attribute_names = dsd.get_data(target=default_target)
    features = []
    try:
        for name, attribute in X.iteritems(): 
            feature = {}
            att_index = X.columns.get_loc(name)
            feature["Index"] = index
            feature["Name"] = name
            if index in dsd.get_features_by_type('nominal') :
                 feature["data_type"] = "nominal"
            elif index in dsd.get_features_by_type('numeric') :
                feature["data_type"] = "numeric" 
            elif index in dsd.get_features_by_type('date') :
                feature["data_type"] = "date" 
            elif index in dsd.get_features_by_type('string') :
                feature["data_type"] = "string" 
            else:
                feature["data_type"] = "unknown" 
    except:
        print("Error")
    #extract properties
    d_X = X.to_numpy()
    d_y = y.to_numpy()
    mfe = MFE(groups="all")
    mfe.fit(d_X, d_y)
    ft = mfe.extract()
    #return ft?

def uploadDataset():
    return

def processDatasets():
    dataids = getDataIds()
    for id in dataids:
        downloadDataset(id)
        #process arff file using PyMFE
        uploadDataset()
        os.remove('temp.arff')


