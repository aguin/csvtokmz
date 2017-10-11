import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from csv2kmz import create_kmz_from_csv

OUTPUT_DIR = 'output/'


def test_working_example():
    """ Should complete with no errors """
    csvFile = 'examples/Example1.csv'
    kmz = create_kmz_from_csv(csvFile, OUTPUT_DIR)
    assert os.path.split(kmz)[1] == 'Example1.kmz'


def test_example_with_warnings():
    """ Should complete with warnings but no errors """
    csvFile = 'examples/Example2.csv'
    kmz = create_kmz_from_csv(csvFile, OUTPUT_DIR)
    assert os.path.split(kmz)[1] == 'Example2.kmz'


def test_broken_example():
    """ Should raise an error as not in the right format """
    csvFile = 'examples/Example-Errors.csv'
    with pytest.raises(IndexError):
        kmz = create_kmz_from_csv(csvFile, OUTPUT_DIR)
