import pytest

from pyevaluationengine.evaluationengine import EvaluationEngine, main
from pyevaluationengine.config import testing, defaults


__author__ = "LUDev"
__copyright__ = "LUDev"
__license__ = "BSD 3-Clause License"


def test_constructor():
    # test default constructor
    instance = EvaluationEngine()
    assert instance.url == defaults["url"]
    assert instance.apikey == defaults["apikey"]


def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts agains stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    # main(["-h"])
    # captured = capsys.readouterr()
    # assert "The 7-th Fibonacci number is 13" in captured.out
