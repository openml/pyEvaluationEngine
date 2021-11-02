import json
import logging
import os
import sys

import requests

from pyevaluationengine import config

_logger = logging.getLogger(__name__)


class EvaluationEngine:
    def __init__(self, url=config.defaults["url"], apikey=config.defaults["apikey"]):
        self.url = url
        self.apikey = apikey

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

    # Upload dataset
    def upload_dataset(self):

        # TODO: Upload dataset back to the server

        return

    # Process dataset
    def process_datasets(self):
        data_ids = self.get_data_ids()

        for data_id in data_ids:
            self.download_dataset(data_id)

            # TODO: process arff file using PyMFE

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