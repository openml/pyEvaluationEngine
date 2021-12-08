import pytest

from pyevaluationengine.evaluationengine import EvaluationEngine
from pyevaluationengine.config import testing, defaults

import os
import arff

__author__ = "LUDev"
__copyright__ = "LUDev"
__license__ = "BSD 3-Clause License"


def test_constructor():
    # test default constructor
    instance = EvaluationEngine()
    assert instance.url == defaults["url"]
    assert instance.apikey == defaults["apikey"]

def test_calculate_data_qualities():
    #test calculate_data_qualities with dataset 'cload.arff' id = 890
    instance = EvaluationEngine()
    list_qualities = []
    path = 'tests/test_sets'
    test_file= open(os.path.join(path + '/test_890.csv'))
    test_qualities = test_file.readlines()
    fp = open(os.path.join(path +'/cloud.arff'))
    dataset = arff.load(fp)
    qualities = instance.calculate_data_qualities(dataset, 0)
    for quality, test_quality in zip(qualities[1], test_qualities):
        assert quality == float(test_quality)

if __name__ == "__main__":
    test_calculate_data_qualities()

