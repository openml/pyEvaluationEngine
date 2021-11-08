import openml as oml
from pymfe.mfe import MFE
import arff
import pandas as pd
import numpy as np
import requests
import json
import os
from dicttoxml import dicttoxml

api_key = "07ba2f75d031ff6997b8f93d466f1f1e"

oml.config.server = 'https://test.openml.org/api/v1'
oml.config.apikey = api_key


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

def extractMetafeatures(id):
    #extract features
    dsd = oml.datasets.get_dataset(id) # dataset discription
    default_target = dsd.default_target_attribute # get target attribute
    X,y,categorical_indicator,attribute_names = dsd.get_data(target=default_target, dataset_format='array')
    try:
        mfe = MFE(groups="all")
        mfe.fit(X, y)
        ft = mfe.extract(out_type=pd.DataFrame, suppress_warnings=True)
        qualities = convert(ft.to_dict('index')[0])
        return qualities
    except:
        print("Error in extract feartures")

def convert(qualities):
    try:
        qualitiesXML = dicttoxml(qualities)
        print(qualitiesXML)
        dom = parseString(qualitiesXML)
        print(dom.toprettyxml())
    except:
        print("error in convert")

def uploadDataset():
    return

def processDatasets():
    dataids = getDataIds()
    for id in dataids:
        #downloadDataset(id)
        #process arff file using PyMFE
        extractMetafeatures(id)
        #uploadDataset()
        #os.remove('temp.arff')


processDatasets()
