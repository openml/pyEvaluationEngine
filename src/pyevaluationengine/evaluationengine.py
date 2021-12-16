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

from pyevaluationengine.config import defaults, testing, pymfe_qualities_csv

_logger = logging.getLogger(__name__)


class EvaluationEngine:
    """
    This class has contains all functionalities of the Evaluation Engine
    and is the core of the library.

    :param id: The ID that the EvaluationEngine needs to use for requesting jobs. Defaults to 1.
    :type id: int
    :param url: A string that points to the right openML URL. Defaults to the URL in config.py
    :type url: str
    :param apikey: A string that contains the API key to use for OpenML. Defaults to the API key in config.py
    :type apikey: str
    """
    def __init__(self, id:int=1, url=defaults["url"], apikey=defaults["apikey"], loglevel=logging.INFO):
        self.url = url
        self.apikey = apikey
        self.engine_id = id
        oml.config.server = url
        oml.config.apikey = apikey
        logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
        logging.basicConfig(
            level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
        )

    def get_unprocessed_dataset_ids(self):
        """
        Fetches a list of IDs of unprocessed datasets

        :return: List of integers
        """  
        _logger.info("Fetching IDs of unprocessed datasets")

        # Send request to OpenML server
        response = requests.post(self.url + f"/data/qualities/unprocessed/{self.engine_id}/normal", params={'api_key': self.apikey}, data={'qualities': pymfe_qualities_csv})
        if response.status_code != 200:
            _logger.error('Could not fetch the IDs of unprocessed datasets')
            return []

        # Parse requests
        datasets = dict(xmltodict.parse(response.text))
        data_ids = []
        if type(datasets['oml:data_unprocessed']['oml:dataset']) is OrderedDict:
                data_ids.append(datasets['oml:data_unprocessed']['oml:dataset']['oml:did'])
        else:
            for dataset in datasets['oml:data_unprocessed']['oml:dataset'][0]:
                data_ids.append(int(dataset['did']))
             
        # Logging
        if not data_ids:
            _logger.info('No unprocessed datasets found')
        else:
            _logger.debug(f'Unprocessed datasets found: {data_ids}')
        
        return data_ids

    def download_dataset(self, data_id: int):
        """
        Downloads a dataset to OpenML cache and returns the ARFF dataset.

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
        """
        Calculate all necessary qualities and return the qualities

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
            mfe.fit(x, suppress_warnings=True)
            qualities = mfe.extract(suppress_warnings=True)
            _logger.info(f"Sucessfully calculated qualities of dataset {data_id}")

            # Only comment this out for extensive analysis checking
            # for name, value in zip(qualities[0], qualities[1]):
            #     _logger.debug(f"{name} \t\t {value}")
        except:
            _logger.error(f'Error while calculating qualities of dataset {data_id}')
            return []

        return qualities
    
    def qualities_to_xml_format(self, qualities, data_id: int):
        """
        Convert the qualities of a dateset to the correct xml format

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
        xml["oml:data_qualities"]["oml:evaluation_engine_id"] = self.engine_id
        xml["oml:data_qualities"]["oml:quality"] = []

        for name, value in zip(qualities[0], qualities[1]):
            quality = OrderedDict()
            quality["oml:name"] = f'pymfe.{name}'
            if not math.isnan(value) and not math.isinf(value):
                quality["oml:value"] = value
            xml["oml:data_qualities"]["oml:quality"].append(quality)

        return xmltodict.unparse(xml)

    def upload_qualities(self, xmldata):
        """
        Upload the qualities of the given dataset

        :param xmldata: The data of the qualities that need to be uploaded in XML format
        :type xmldata: xml

        :return: An XML object that can be sent to the OpenML servers
        """  
        _logger.info("Uploading qualities")
        response = requests.post(self.url + "/data/qualities", params={'api_key': self.apikey}, files={"description": xmldata})
        _logger.debug(f'Response: {response.text}')

    def process_datasets(self):
        """
        Method to start analyzing and process datasets. Fetches 
        a list of unprocessed datasets first, and then processes
        untill it runs out of datasets in the list.
        """  
        data_ids = self.get_unprocessed_dataset_ids()

        for data_id in data_ids:
            dataset = self.download_dataset(data_id)
            qualities = self.calculate_data_qualities(dataset, data_id)
            qualities_xml = self.qualities_to_xml_format(qualities, data_id)
            self.upload_qualities(qualities_xml)

    def process_one_dataset(self):
        """
        Method to process a single dataset. 
        Fetches  a list of unprocessed datasets first
        and picks the first one to analyze.
        """

        # Fetching the full list is not efficient but a singluar 
        # unprocessed dataset fetch is not supported yet
        data_ids =self.get_unprocessed_dataset_ids()

        if len(data_ids) == 0:
            _logger.info("No datasets to be processed")
            return
        
        dataset=self.download_dataset(data_ids[0])
        qualities=self.calculate_data_qualities(dataset,data_ids[0])
        qualities_xml=self.qualities_to_xml_format(qualities,data_ids[0])
        self.upload_qualities(qualities_xml)

    def process_input_dataset(self, dataset_name: str):
        """
        Method to process a specific dataset. 

        :param dataset_name: The name of the dataset
        :type data_id: str
        """
        response = requests.get(self.url + f"/data/list/data_name/{dataset_name}/limit/5", params={'api_key': self.apikey})

        if response.status_code != 200:
            _logger.info(f"No dataset found with the name:  {dataset_name}")
            return

        datasets = dict(xmltodict.parse(response.text))

        # Larger than 2 because extra header also counts as an item in XML
        if len(datasets['oml:data']['oml:dataset']) > 1:
            _logger.info(f"Found more than one dataset with the name {dataset_name}. Analysing and processing the first occurence.")

        if type(datasets['oml:data']['oml:dataset']) is OrderedDict:
            did=datasets['oml:data']['oml:dataset']['oml:did']
        else:
            did=datasets['oml:data']['oml:dataset'][0]['oml:did']

        _logger.info(f"Analysing and processing dataset with did {did}")

        dataset=self.download_dataset(did)
        qualities=self.calculate_data_qualities(dataset,did)
        qualities_xml=self.qualities_to_xml_format(qualities,did)
        self.upload_qualities(qualities_xml)