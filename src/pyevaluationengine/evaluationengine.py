from configparser import Error
import json
import logging
import os
import sys
import math
import openml as oml
from pymfe.mfe import MFE
from collections import OrderedDict
import xmltodict
import requests
from xml.etree import ElementTree

from config import defaults, testing

_logger = logging.getLogger(__name__)


class EvaluationEngine:
    def __init__(self, url=defaults["url"], apikey=defaults["apikey"]):
        self.url = url
        self.apikey = apikey
        self.evaluation_engine_id = 1 # will be changed later
        oml.config.server = url
        oml.config.apikey = apikey

    # Get unprocessed IDs of unprocessed datasets
    def get_unprocessed_dataset_ids(self):
        _logger.info("Fetching IDs of unprocessed datasets")

        # Send request to OpenML server
        response = requests.get(self.url + "/json/data/unprocessed/0/normal", params={'api_key': self.apikey})
        if response.status_code != 200:
            _logger.error('Could not fetch the IDs of unprocessed datasets')
            return []

        # Parse requests
        datasets = json.loads(response.text)
        data_ids = []
        for key in datasets['data_unprocessed']:
            data_ids.append(datasets['data_unprocessed'][key]['did'])
        
        # Logging
        if not data_ids:
            _logger.info('No unprocessed datasets found')
        else:
            _logger.debug(f'Unprocessed datasets found: {data_ids}')
        
        return data_ids

    # Downloads a dataset to OpenML cache
    def download_dataset(self, data_id):
        _logger.info(f'Fetching dataset {data_id}')
        try:
            oml.datasets.get_dataset(data_id)
        except:
            _logger.error(f'Error while fetching dataset {data_id}')

    # Calculate all necessary qualities
    def calculate_data_qualities(self, X, y):
        try: 
            mfe = MFE(groups="all")
            mfe.fit(X, y)   
            qualities = mfe.extract(suppress_warnings=True)
        except:
            qualities = ([],[])
        return qualities
    
    def to_xml_format(self, ft, data_id):
        xml  = OrderedDict()
        xml["oml:data_qualities"] = OrderedDict()
        xml["oml:data_qualities"]["@xmlns:oml"] = "http://openml.org/openml"
        xml["oml:data_qualities"]["oml:did"] = data_id
        xml["oml:data_qualities"]["oml:evaluation_engine_id"] = self.evaluation_engine_id
        xml["oml:data_qualities"]["oml:quality"] = []
        for name, value, index in zip(ft[0], ft[1], range(len(ft[0]))):
            quality = OrderedDict()
            quality["oml:name"] = name
            quality["oml:feature_index"] = index
            if not math.isnan(value) and not math.isinf(value):
                quality["oml:value"] = value
            xml["oml:data_qualities"]["oml:quality"].append(quality) 
        return xmltodict.unparse(xml)

    # Upload dataset
    def upload_dataset(self, xmldata):
        _logger.info("Uploading qualities")
        response = requests.post(self.url + "/data/qualities", params={'api_key': self.apikey}, data=xmldata)
        _logger.debug(f'Response: {response.text}')

    # Process dataset
    def process_datasets(self):
        data_ids = self.get_unprocessed_dataset_ids()

        for data_id in data_ids:
            X, y = self.download_dataset(data_id)
            xmldata = self.calculate_data_qualities(X, y)
            qualities = self.to_xml_format(xmldata, data_id)
            self.upload_dataset()


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    setup_logging(logging.DEBUG)

    engine = EvaluationEngine(testing['url'], testing['apikey'])

    # engine.get_unprocessed_dataset_ids()
    engine.download_dataset(1)
    




if __name__ == "__main__":
    main()
