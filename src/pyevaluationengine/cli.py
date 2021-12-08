import argparse
import logging
import sys
import time
from requests import api
#from typing_extensions import runtime

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
        "-n",
        "-number",
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
    parser.add_argument( 
        "-t",
        "-time",
        type=int,
        default=30,
        help="amount of time to wait for new datasets, standart is 30",
    )
    parser.add_argument( 
        "-k",
        "-keep_processing",
        type=int,
        default=0,
        help="procceses all datasets and then waits for a time and checks if there are more datasets, if there are repeat program inf not stops. runs if it is higher than 0",
    )
    parser.add_argument( 
        "-s",
        "-process_singular",
        type=int,
        default=0,
        help="if largert than 0, input a dataset name, if that dataset exist it will be procesd",
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
    response=requests.get(url+"/json/data/unprocessed/0/normal", params={"api_key":apikey})
    data=json.loads(response.text)
    print("the following datasets are unprocessed")
    for i in data["data_unprocessed"]:
        print(data["data_unprocessed"][i]["name"])
    
def process_all(url=config.defaults["url"],apikey=config.defaults["apikey"]): 
    engine=EvaluationEngine(url, apikey)
    engine.process_datasets()

def keep_proccesing_all(url=config.defaults["url"],apikey=config.defaults["apikey"],sleeptime=30):
    engine=EvaluationEngine(url, apikey)
    while True:
        response=requests.get(url+"/data/unprocessed/0/normal", params={"api_key":apikey})
        data=json.loads(response.text)
        if data["data_unprocessed"]=={}:
            _logger.info("no more unprocessed data sets are left, ending program")
            break
        engine.process_datasets() #we kunnen nog niet goed testen omdat we nog niet uploaden
        time.sleep(sleeptime)
        _logger.info("sleep of "+str(sleeptime)+" has ended")

def process_x_amount(url=config.defaults["url"],apikey=config.defaults["apikey"],amount_of_repeats=0):
    engine=EvaluationEngine(url, apikey)
    i=0
    while amount_of_repeats > i:
        i+=1
        _logger.info("executing main function for the "+str(i)+"th time")
        engine.process_one_dataset()

def process_specific_dataset(url=config.defaults["url"],apikey=config.defaults["apikey"]):
    engine=EvaluationEngine(url,apikey)
    #engine.get_unprocessed_dataset_ids()
    engine.process_input_dataset()


if __name__ == "__main__":
    run()
    amount_of_repeats=(parse_args(sys.argv[1:]).n)
    print_unproccesed=(parse_args(sys.argv[1:]).p)
    process=(parse_args(sys.argv[1:]).a)
    keep_prossesing=(parse_args(sys.argv[1:]).k)
    process_singular=(parse_args(sys.argv[1:]).s)
    if amount_of_repeats > 0: #voert t=x keer eveluationengine.py uit kijk of dit correct is met wat script 2 zou moetten doen
        process_x_amount(config.testing["url"],config.testing["apikey"],amount_of_repeats)
    if print_unproccesed>0: #print lijst van unprocesd datasets
        print_unproccesed_data(config.testing["url"],config.testing["apikey"])
    if process>0: #process alle datasets
        
        process_all(config.testing["url"],config.testing["apikey"])
    if keep_prossesing>0:
        sleeptime=(parse_args(sys.argv[1:]).t)
        keep_proccesing_all(config.testing["url"],config.testing["apikey"],sleeptime)
    if process_singular>0:
        process_specific_dataset(config.testing["url"],config.testing["apikey"])
