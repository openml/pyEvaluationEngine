import json
import logging
import os
import sys
import openml as oml
import requests

from pyevaluationengine import config

_logger = logging.getLogger(__name__)


class EvaluationEngine:
    def __init__(self, url=config.defaults["url"], apikey=config.defaults["apikey"]):
        self.url = url
        self.apikey = apikey
        self.evaluation_engine_id = 1 # will be changed later

    # Get IDs of unprocessed datasets
    def get_data_ids(self):
        _logger.info("Fetching ID of unprocessed datasets")
        response = requests.get(self.url + "/data/unprocessed/0/normal", params={'api_key': self.apikey})
        datasets = json.loads(response.text)
        data_ids = []
        for key in datasets['data_unprocessed']:
            data_ids.append(datasets['data_unprocessed'][key]['did'])
            _logger.debug(f'Found unprocessed dataset: {data_ids[-1]}')
        return data_ids

    # Downloads dataset and store as temp.arff
    def download_dataset(self, data_id):
        response = requests.get(self.url + "/data/"+data_id, params={'api_key': self.apikey})
        url = json.loads(response.text)['data_set_description']['url']
        open('temp.arff', 'wb').write(requests.get(url).content)

    def calculate_metafeatures(dsd, default_target, data_id):
        X,y,categorical_indicator,attribute_names = dsd.get_data(target=default_target, dataset_format='array')
        mfe = MFE(groups="all")
        mfe.fit(X, y)   
        ft = mfe.extract(suppress_warnings=True)
        qualities = to_xml_format(ft, data_id)
        return qualities
    
    def to_xml_format(ft, data_id)
        xml  = OrderedDict()
        xml["oml:data_qualities"] = OrderedDict()
        xml["oml:data_qualities"]["@xmlns:oml"] = "http://openml.org/openml"
        xml["oml:data_qualities"]["oml:did"] = data_id
        xml["oml:data_qualities"]["oml:evaluation_engine_id"] = 1 
        xml["oml:data_qualities"]["oml:quality"] = []
        for name, value, index in zip(ft[0], ft[1], range(len(ft[0]))):
            quality = OrderedDict()
            quality["oml:name"] = name
            quality["oml:feature_index"] = index
            if not math.isnan(value) and not math.isinf(value):
                quality["oml:value"] = value
            xml["oml:data_qualities"]["oml:quality"].append(quality) 
        xmltodict.unparse(xml)

    # Upload dataset
    def upload_dataset(self):
        return

    # Process dataset
    def process_datasets(self):
        data_ids = self.get_data_ids()

        for data_id in data_ids:
            self.download_dataset(data_id)

            self.upload_dataset()
            os.remove('temp.arff')


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    setup_logging(logging.DEBUG)

    engine = EvaluationEngine(config.testing['url'], config.testing['apikey'])

    EvaluationEngine.get_data_ids(engine)


if __name__ == "__main__":
    main()