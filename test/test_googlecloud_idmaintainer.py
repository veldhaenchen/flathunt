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
