import argparse
import logging
import sys

from requests.models import Response
import evaluationengine

import json
import requests
from pyevaluationengine.evaluationengine import EvaluationEngine
from pyevaluationengine import config


from __version__ import __version__ #orgineel (.__version__ import ...) weet niet de reden voor die punt dus heb hem weg gehaald, comment voor het geval dat het dit iets sloopt

__author__ = "LUDev"
__copyright__ = "LUDev"
__license__ = "BSD 3-Clause License"

_logger = logging.getLogger(__name__)
def parse_args(args):
    parser = argparse.ArgumentParser(description="Python EvaluationEngine for the OpenML project")
    parser.add_argument(
        "--version",
        action="version",
        version="pyevaluationengine {ver}".format(ver=__version__),
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
    parser.add_argument( #hier mee kun je evaluationengine.py x aantal keer aanroepen
        "-t",
        "-times",
        type=int,
        default=0,
        help="set amount of times the evaluation engine is run",
    )
    parser.add_argument( 
        "-p",
        "-print",
        type=int,
        default=0,
        help="Print unprocesed data if its value is higher than 0",
    )
    parser.add_argument( 
        "-a",
        "-all",
        type=int,
        default=0,
        help="procces all unprocesed data if its value is higher than 0",
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


def run():
    main(sys.argv[1:])

def print_unproccesed_data(url=config.defaults["url"],apikey=config.defaults["apikey"]):
    response=requests.get(config.testing["url"]+"/data/unprocessed/0/normal", params={"api_key":config.testing["apikey"]})
    data=json.loads(response.text)
    datasets=[]
    print("the following datasets are unprocessed")
    for i in data["data_unprocessed"]:
        print(data["data_unprocessed"][i]["name"])

if __name__ == "__main__":
    run()
    amount_of_repeats=(parse_args(sys.argv[1:]).t)
    print_unproccesed=(parse_args(sys.argv[1:]).p)
    process=(parse_args(sys.argv[1:]).a)
    if amount_of_repeats > 0: #voert t=x keer eveluationengine.py uit kijk of dit correct is met wat script 2 zou moetten doen
        i=0
        while amount_of_repeats > i:
            i+=1
            _logger.info("executing main function for the "+str(i)+"th time")
            evaluationengine.main()
    if print_unproccesed>0:
        print_unproccesed_data()

