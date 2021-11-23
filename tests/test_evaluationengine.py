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

def get_test_data(dataset, filename):
    data = dataset['data']
    X = []
    y = []
    for row in data:
        if filename == "Brainsize.arff":
            X.append(row[1:])
            y.append(row[0])
        if filename == "hip.arff":
            X.append(row)
        if filename == "iq_brain_size - kopie.arff":
            X.append(row[:-1])
            y.append(row[len(row)-1])
        if filename == "iq_brain_size.arff":
            X.append(row[:-1])
            y.append(row[len(row)-1])
        if filename == "openml_filrev.arff":
            X.append(row)
        if filename == "red_wine.arff":
            X.append(row)
    return X,y

def test_calculate_data_qualities():
    instance = EvaluationEngine()
    list_qualities = []
    path = 'tests/test_sets'
    for filename in os.listdir(path):
        fp = open(os.path.join(path,filename))
        dataset = arff.load(fp)
        X,y = get_test_data(dataset, filename)
        list_qualities.append(instance.calculate_data_qualities(X,y))
    print(list_qualities)
    for qualities in list_qualities:
        assert(qualities == ([],[]) or len(qualities[0]) > 0)



if __name__ == "__main__":
    test_calculate_data_qualities()
