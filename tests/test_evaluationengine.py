import pytest

from pyevaluationengine.evaluationengine import EvaluationEngine
from pyevaluationengine.config import testing, defaults


__author__ = "LUDev"
__copyright__ = "LUDev"
__license__ = "BSD 3-Clause License"


def test_constructor():
    # test default constructor
    instance = EvaluationEngine()
    assert instance.url == defaults["url"]
    assert instance.apikey == defaults["apikey"]

