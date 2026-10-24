import pytest
from analysis.measure import index_of_coincidence

def test_index_of_coincidence():
    assert round(index_of_coincidence("CRYPTANALYSIS"), 4) == 0.0385
    assert round(index_of_coincidence("THEINDEXOFCOINCIDENCE"), 4) == 0.0810