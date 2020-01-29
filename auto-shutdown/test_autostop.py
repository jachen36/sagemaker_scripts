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





# notebook data looks like below

# data
# [{'id': 'f1188143-f22b-46d1-85d0-8c5d370bf78c',
#   'path': 'Untitled.ipynb',
#   'name': '002509a6-5b5d-4b60-b9fd-6821f45f7482',
#   'type': '',
#   'kernel': {'id': '78dfefcf-e78a-4ef4-a463-b6058bb758f4',
#    'name': 'python37464bitbokivirtualenv60a2167245d644b6ab7c9f62b121068a',
#    'last_activity': '2020-01-26T20:01:06.159172Z',
#    'execution_state': 'busy',
#    'connections': 1}},
#  {'id': '10548a62-939d-4e01-9b67-430d6b6526f2',
#   'path': 'Untitled1.ipynb',
#   'name': '9d594b0c-b157-4e4a-87b7-511ae9413dfd',
#   'type': '',
#   'kernel': {'id': '5c7597e4-ab6a-4f15-a28a-6654253eb726',
#    'name': 'python37464bitbokivirtualenv60a2167245d644b6ab7c9f62b121068a',
#    'last_activity': '2020-01-26T19:50:35.404690Z',
#    'execution_state': 'idle',
#    'connections': 1}}]