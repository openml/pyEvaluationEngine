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
        dest="name",
        type=str,
        required=True,
        help="Name of the to be processed dataset",
    )

    # Sub parser for amount mode
    parser_repeat = sub_parsers.add_parser("amount", help="Amount configuration")
    parser_repeat.add_argument( 
        "-n",
        "-number",
        dest="number",
        type=int,
        default=5,
        help="Amount datasets to process, default is 5",
    )

    # Sub parser for repeat mode
    parser_repeat = sub_parsers.add_parser("repeat", help="Repeat configuration")
    parser_repeat.add_argument( 
        "-t",
        "-time",
        dest="time",
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

def process_all(engine: EvaluationEngine):
    engine.process_datasets()

def print_unproccesed_data(engine: EvaluationEngine):
    dataset_ids = engine.get_unprocessed_dataset_ids()
    for id in dataset_ids:
        _logger.info(f"Unprocessed dataset: {id}")
    
def process_specific_dataset(dataset_name, engine: EvaluationEngine):
    engine.process_input_dataset(dataset_name)

def process_x_amount(amount_of_repeats, engine: EvaluationEngine):
    i=0
    while amount_of_repeats > i:
        i+=1
        _logger.info(f"Processing a single dataset for the {i}th time.")
        engine.process_one_dataset()

def keep_proccesing_all(sleeptime, engine: EvaluationEngine):
    while True:
        engine.process_datasets()
        _logger.info("Sleeping for " + str(sleeptime) + " minutes.")
        time.sleep(sleeptime * 60)
        _logger.info("Sleep of " + str(sleeptime) + " minutes has ended.")

def main():
    args = parse_args(sys.argv[1:])
    setup_logging(args.loglevel)

    # Configuration setting has priority above normal modes
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

    # Check if configuration file exists
    if not os.path.isfile('cli_config.json'):
        _logger.info("Config has nog been set. Run the config setter first.")
        sys.exit(0)
 
    # Load configuration file
    with open('cli_config.json', 'r') as config_file:
        openml_config = json.load(config_file)

    # Initialize engine
    engine = EvaluationEngine(openml_config["url"],openml_config["apikey"])

    # Execute the right mode
    if args.mode == 'all':
        process_all(engine)
    elif args.mode == 'print':
        print_unproccesed_data(engine)
    elif args.mode == 'singular':
        process_specific_dataset(args.name, engine)
    elif args.mode == 'amount':
        process_x_amount(args.number, engine)
    elif args.mode == 'repeat':
        keep_proccesing_all(args.time, engine)

if __name__ == "__main__":
    main()
