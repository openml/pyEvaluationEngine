import json
import logging
import sys
import math
import openml as oml
from pymfe.mfe import MFE
from collections import OrderedDict
import xmltodict
import requests
import arff

from pyevaluationengine.config import defaults, testing

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
            data_ids.append(int(datasets['data_unprocessed'][key]['did']))
        
        # Logging
        if not data_ids:
            _logger.info('No unprocessed datasets found')
        else:
            _logger.debug(f'Unprocessed datasets found: {data_ids}')
        
        return data_ids

    # Downloads a dataset to OpenML cache and returns the ARFF dataset
    def download_dataset(self, data_id: int):
        _logger.info(f'Fetching dataset {data_id}')
        try:
            return arff.load(open(oml.datasets.get_dataset(data_id).data_file))
        except:
            _logger.error(f'Error while fetching dataset {data_id}')

    # Calculate all necessary qualities and return the qualities
    def calculate_data_qualities(self, dataset_arff, data_id):
        x = dataset_arff['data']

        # Calculate all qualities using MFE
        _logger.info(f'Calculating qualities of dataset {data_id}')
        try: 
            mfe = MFE(groups="all")
            mfe.fit(x)
            qualities = mfe.extract(suppress_warnings=True)
            _logger.debug("\n".join("{:50} {:30}".format(x, y) for x, y in zip(qualities[0], qualities[1])))
        except:
            _logger.error(f'Error while calculating qualities of dataset {data_id}')
            return []

        return qualities
    
    # Convert the qualities of a dateset to the correct xml format
    def qualities_to_xml_format(self, qualities, data_id: int):
        xml  = OrderedDict()
        xml["oml:data_qualities"] = OrderedDict()
        xml["oml:data_qualities"]["@xmlns:oml"] = "http://openml.org/openml"
        xml["oml:data_qualities"]["oml:did"] = data_id
        xml["oml:data_qualities"]["oml:evaluation_engine_id"] = self.evaluation_engine_id
        xml["oml:data_qualities"]["oml:quality"] = []

        for name, value, index in zip(qualities[0], qualities[1], range(len(qualities[0]))):
            quality = OrderedDict()
            quality["oml:name"] = name
            quality["oml:feature_index"] = index
            if not math.isnan(value) and not math.isinf(value):
                quality["oml:value"] = value
            xml["oml:data_qualities"]["oml:quality"].append(quality)
        
        # TODO: This is not in the correct format yet
        # Example is not complete: https://www.openml.org/api_docs#!/data/post_data_qualities

        return xmltodict.unparse(xml)

    # Upload the qualities of the given dataset
    def upload_qualities(self, xmldata):
        _logger.info("Uploading qualities")
        response = requests.post(self.url + "/data/qualities", params={'api_key': self.apikey}, data=xmldata)
        _logger.debug(f'Response: {response.text}')

    # Process dataset
    def process_datasets(self):
        data_ids = self.get_unprocessed_dataset_ids()

        for data_id in data_ids:
            dataset = self.download_dataset(data_id)
            qualities = self.calculate_data_qualities(dataset, data_id)
            qualities_xml = self.qualities_to_xml_format(qualities, data_id)
            self.upload_qualities(qualities_xml)


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    setup_logging(logging.DEBUG)

    engine = EvaluationEngine(testing['url'], testing['apikey'])
    engine.process_datasets()
    

if __name__ == "__main__":
    main()
