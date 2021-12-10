import argparse
import configparser
import logging
import sys
import time
import os

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
    # Top-level parser
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

    # Sub-parsers for mode selection
    sub_parsers = parser.add_subparsers(
        title="Operating modes",
        description="Select the operating mode",
        dest="mode",
        required=True,
    )

    # Sub parser for configuration setter
    parser_config = sub_parsers.add_parser("config", help="Setting configuration")
    parser_config.add_argument(
        "-url", 
        dest="url",
        type=str, 
        help="OpenML server url",
        required=True, 
        default=config.defaults["url"]
    )
    parser_config.add_argument(
        "-apikey",
        dest="apikey",
        type=str,
        help="OpenML API key",
        required=True,
        default=config.defaults["apikey"],
    )


    # Sub parser for all mode
    parser_all = sub_parsers.add_parser("all", help="All configuration")

    # Sub parser for print mode
    parser_print = sub_parsers.add_parser("print", help="Print configuration")

    # Sub parser for singlular mode
    parser_singular = sub_parsers.add_parser("singular", help="Singular configuration")
    parser_singular.add_argument( 
        "-n",
        "-name",
        type=str,
        required=True,
        help="Name of the to be processed dataset",
    )

    # Sub parser for amount mode
    parser_repeat = sub_parsers.add_parser("amount", help="Amount configuration")
    parser_repeat.add_argument( 
        "-n",
        "-number",
        type=int,
        default=5,
        help="Amount datasets to process, default is 5",
    )

    # Sub parser for continuous mode
    parser_repeat = sub_parsers.add_parser("repeat", help="Repeat configuration")
    parser_repeat.add_argument( 
        "-t",
        "-time",
        type=int,
        default=30,
        help="Amount of time to wait for new datasets in minutes, standard is 30",
    )

    # Exit if no arguments are given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    return parser.parse_args(args)

def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )

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

def main():
    args = parse_args(sys.argv[1:])
    setup_logging(args.loglevel)

    if not os.path.isfile('cli_config.json'):
        _logger.info("Config has nog been set. Run the config setter first.")
        sys.exit(0)
 
    with open('cli_config.json', 'r') as config_file:
        openml_config = json.load(config_file)

    if args.mode == 'config':
        _logger.info("Setting configuration:")
        _logger.info(f"APIKey: {args.apikey}")
        _logger.info(f"url: {args.url}")
        with open('cli_config.json', 'w') as config_file:
            contents = {
                "apikey": args.apikey,
                "url": args.url
            }
            json.dump(contents, config_file, indent=2)
        return
    elif args.mode == 'all':
        return
    elif args.mode == 'print':
        return
    elif args.mode == 'singular':
        return
    elif args.mode == 'amount':
        return
    elif args.mode == 'repeat':
        return


if __name__ == "__main__":
    main()
    # amount_of_repeats=(parse_args(sys.argv[1:]).n)
    # print_unproccesed=(parse_args(sys.argv[1:]).p)
    # process=(parse_args(sys.argv[1:]).a)
    # keep_prossesing=(parse_args(sys.argv[1:]).k)
    # process_singular=(parse_args(sys.argv[1:]).s)
    # if amount_of_repeats > 0: #voert t=x keer eveluationengine.py uit kijk of dit correct is met wat script 2 zou moetten doen
    #     process_x_amount(config.testing["url"],config.testing["apikey"],amount_of_repeats)
    # if print_unproccesed>0: #print lijst van unprocesd datasets
    #     print_unproccesed_data(config.testing["url"],config.testing["apikey"])
    # if process>0: #process alle datasets
        
    #     process_all(config.testing["url"],config.testing["apikey"])
    # if keep_prossesing>0:
    #     sleeptime=(parse_args(sys.argv[1:]).t)
    #     keep_proccesing_all(config.testing["url"],config.testing["apikey"],sleeptime)
    # if process_singular>0:
    #     process_specific_dataset(config.testing["url"],config.testing["apikey"])
