import pytest
from pytest import approx
from datetime import datetime, timedelta
import autostop


test_act_time = [
    # 
    '2020-01-23T06:45:53.672333Z'
]

@pytest.mark.parametrize("", )
def test_time_diff():
    diff = timedelta(seconds=60)