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

def uploadDataset():
    return

def processDatasets():
    dataids = getDataIds()
    for id in dataids:
        downloadDataset(id)
        #process arff file using PyMFE
        uploadDataset()
        os.remove('temp.arff')


