import pytest
from mockfirestore import MockFirestore
from flathunter.googlecloud_idmaintainer import GoogleCloudIdMaintainer

class MockGoogleCloudIdMaintainer(GoogleCloudIdMaintainer):

    def __init__(self):
        self.db = MockFirestore()

@pytest.fixture
def id_watch():
    return MockGoogleCloudIdMaintainer()
    
def test_read_from_empty_db(id_watch):
    assert id_watch.get() == []

def test_read_after_write(id_watch):
    id_watch.add(12345)
    assert id_watch.get() == [12345]

def test_get_last_run_time_none_by_default(id_watch):
    assert id_watch.get_last_run_time() == None

def test_get_list_run_time_is_updated(id_watch):
    time = id_watch.update_last_run_time()
    assert time != None
    assert time == id_watch.get_last_run_time()
