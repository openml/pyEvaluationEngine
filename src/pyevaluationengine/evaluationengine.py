import argparse
import json
import logging
import os
import sys

import requests

from pyevaluationengine import config

from .__version__ import __version__

__author__ = "LUDev"
__copyright__ = "LUDev"
__license__ = "BSD 3-Clause License"

_logger = logging.getLogger(__name__)


# ---- Python API ----


class EvaluationEngine:
    def __init__(self, url=config.defaults["url"], apikey=config.defaults["apikey"]):
        self.url = url
        self.apikey = apikey

    # Get IDs of unprocessed datasets
    def get_data_ids(self):
        response = requests.get(self.url + "unprocessed/0/normal", params={'api_key': self.apikey})
        datasets = json.loads(response.text)
        data_ids = []
        for key in datasets['data_unprocessed']: 
            data_ids.append(datasets['data_unprocessed'][key]['did'])
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


# ---- CLI ----


def parse_args(args):
    parser = argparse.ArgumentParser(description="Python EvaluationEngine for the OpenML project")
    parser.add_argument(
        "--version",
        action="version",
        version="pyevaluationengine {ver}".format(ver=__version__),
    )
    parser.add_argument(
        "-h",
        action="help",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)

    # TODO: Write help function if -h tag is given

    # TODO: Initialize EvaluationEngine object

    # TODO: Do something with the EvaluationEngine based on the given arguments


if __name__ == "__main__":
    main(sys.argv[1:])
