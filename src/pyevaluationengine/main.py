import openml as oml
from pymfe.mfe import MFE
import arff
import pandas as pd
import numpy as np
import requests
import json
import os
from dicttoxml import dicttoxml
from collections import OrderedDict
import xmltodict


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
        ft = mfe.extract(suppress_warnings=True)
        qualities = convert(ft)
        return qualities
    except:
        print("Error in extract feartures")

def convert(ft):
    try:
        xml  = OrderedDict()
        xml["oml:data_qualities"] = OrderedDict()
        xml["oml:data_qualities"]["@xmlns:oml"] = "http://openml.org/openml"
        xml["oml:data_qualities"]["oml:did"] = 0
        xml["oml:data_qualities"]["oml:evaluation_engine_id"] = 0
        xml["oml:data_qualities"]["oml:quality"] = []
        for name, value in zip(ft[0], ft[1]):
            quality = OrderedDict()
            quality["oml:name"] = name
            quality["oml:value"] = value
            xml["oml:data_qualities"]["oml:quality"].append(quality) 
        print(xmltodict.unparse(xml))
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
