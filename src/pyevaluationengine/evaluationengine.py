import json
import logging
import sys
import math
import openml as oml
from openml.datasets import dataset
from pymfe.mfe import MFE
from collections import OrderedDict
import xmltodict
import requests
import arff

from pyevaluationengine.config import defaults, testing

_logger = logging.getLogger(__name__)


class EvaluationEngine:
    """This class has contains all functionalities of the Evaluation Engine
    and is the core of the library.

    :param url: A string that points to the right openML URL. Defaults to the URL in config.py
    :type url: str
    :param apikey: A string that contains the API key to use for OpenML. Defaults to the API key in config.py
    :type apikey: str
    """
    def __init__(self, url=defaults["url"], apikey=defaults["apikey"]):
        self.url = url
        self.apikey = apikey
        self.evaluation_engine_id = 1 # will be changed later
        oml.config.server = url
        oml.config.apikey = apikey
        logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
        logging.basicConfig(
            level=logging.INFO, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
        )

    def get_unprocessed_dataset_ids(self):
        """Fetches a list of IDs of unprocessed datasets

        :return: List of integers
        """  
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

    def download_dataset(self, data_id: int):
        """Downloads a dataset to OpenML cache and returns the ARFF dataset.

        :param data_id: The id of the dataset that needs to be downloaded
        :type data_id: int

        :return: A dictionary of the downloaded ARFF file 
        :rtype: dictionary
        """  
        _logger.info(f'Fetching dataset {data_id}')
        try:
            return arff.load(open(oml.datasets.get_dataset(data_id).data_file))
        except:
            _logger.error(f'Error while fetching dataset {data_id}')

    
    def calculate_data_qualities(self, dataset_arff, data_id: int):
        """Calculate all necessary qualities and return the qualities

        :param dataset_arff: The ARFF dataset in the form of a dictionary object
        :type dataset_arff: dictionary

        :param data_id: The id of the dataset that is being analyzed
        :type data_id: int

        :return: A list of qualities
        """  
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
    
    def qualities_to_xml_format(self, qualities, data_id: int):
        """Convert the qualities of a dateset to the correct xml format

        :param qualities: The list of qualities of the dataset
        :type qualities: dictionary

        :param data_id: The id of the dataset
        :type data_id: int

        :return: An XML object that can be sent to the OpenML servers
        """  
        xml  = OrderedDict()
        xml["oml:data_qualities"] = OrderedDict()
        xml["oml:data_qualities"]["@xmlns:oml"] = "http://openml.org/openml"
        xml["oml:data_qualities"]["oml:did"] = data_id
        xml["oml:data_qualities"]["oml:evaluation_engine_id"] = self.evaluation_engine_id
        xml["oml:data_qualities"]["oml:quality"] = []

        for name, value, index in zip(qualities[0], qualities[1], range(len(qualities[0]))):
            quality = OrderedDict()
            quality["oml:name"] = f'pymfe.{name}'
            quality["oml:feature_index"] = index
            if not math.isnan(value) and not math.isinf(value):
                quality["oml:value"] = value
            xml["oml:data_qualities"]["oml:quality"].append(quality)

        return xmltodict.unparse(xml)

    def upload_qualities(self, xmldata):
        """Upload the qualities of the given dataset

        :param xmldata: The data of the qualities that need to be uploaded in XML format
        :type xmldata: xml

        :return: An XML object that can be sent to the OpenML servers
        """  
        _logger.info("Uploading qualities")
        response = requests.post(self.url + "/data/qualities", params={'api_key': self.apikey}, files={"description": xmldata})
        _logger.debug(f'Response: {response.text}')

    def process_datasets(self):
        """Method to start analyzing and process datasets. Fetches 
        a list of unprocessed datasets first, and then processes
        untill it runs out of datasets in the list.
        """  
        data_ids = self.get_unprocessed_dataset_ids()

        for data_id in data_ids:
            dataset = self.download_dataset(data_id)
            qualities = self.calculate_data_qualities(dataset, data_id)
            qualities_xml = self.qualities_to_xml_format(qualities, data_id)
            self.upload_qualities(qualities_xml)

    # Proces 1 dataset
    def process_one_dataset(self): #procceses only 1 dataset, dit word momenteel niet herkent in cli.py
        data_ids =self.get_unprocessed_dataset_ids() #je haalt alles op maar gebruikt er 1, dit kan optimaler
        dataset=self.download_dataset(data_ids[0])
        qualities=self.calculate_data_qualities(dataset,data_ids[0])
        qualities_xml=self.qualities_to_xml_format(qualities,data_ids[0])
        self.upload_qualities(qualities_xml)

    #proces 1 specific dataset
    def process_input_dataset(self):
        wanted_dataset_name=input("Enter dataset name: ")
        response = requests.get(self.url + "/json/data/unprocessed/0/normal", params={'api_key': self.apikey})
        print(response.status_code)
        datasets = json.loads(response.text)
        for dataset in datasets["data_unprocessed"]:
            print(datasets["data_unprocessed"][dataset]['did'])
            if datasets["data_unprocessed"][dataset]["name"] == wanted_dataset_name: #als dataset met die naam gevonden is
                did=datasets["data_unprocessed"][dataset]['did']
                dataset=self.download_dataset(did)
                qualities=self.calculate_data_qualities(dataset,did)
                qualities_xml=self.qualities_to_xml_format(qualities,did)
                self.upload_qualities(qualities_xml)
                return
        print("no dataset found with the name "+str(wanted_dataset_name))
