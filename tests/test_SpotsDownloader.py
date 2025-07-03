import pandas as pd
import pytest

from datetime import datetime, timedelta

from SpotsDownloader import SpotsDownloader
import config


def generate_timestamps(n = 6):
    """Generate a list of n timestamps for testing."""
    start_time = datetime.now()
    return [(start_time - timedelta(minutes=5*i)).isoformat() for i in range(n)]


@pytest.fixture(scope = "module")
def mock_sota_spots():
    """Fixture to mock API response - dictionary with spots data."""
    test_spots_dict = {"id": [1001, 1002, 1003, 1004, 1005, 1006,],
                       "userID": [2001, 2002, 2003, 2004, 2005, 2002,],
                       "timeStamp": [generate_timestamps(6)],
                       "comments": ["comment1", "comment2", "comment3", "comment4", "comment5", "comment6",],
                       "callsign": ["SP0ABC", "AG7EDG", "W6HIJ", "IK1LMN", "GB10OPR", "AG7EDG",],
                       "associationCode": ["W7O", "W8W", "SP", "JA", "DL", "W8W",],
                       "summitCode": ["CS-098", "CW-076", "BZ-001", "GM-107", "EW-017", "CW-076",],
                       "activatorCallsign": ["SP0ABC", "AG7EDG", "W6HIJ", "IK1LMN", "GB10OPR", "AG7EDG",],
                       "activatorName": ["Amy", "Bob", "Charlie", "David", "Eve", "Bob",],
                       "frequency": ["14.0615", "145.550", "7.0615", "7.158", "21.055", "433,500",],
                       "mode": ["CW", "FM", "CW", "SSB", "CW", "FM"] ,
                       "summitDetails": ["Bieberstedt Butte, 1599m, 4 points", 
                                         "Amabilis Mountain, 1396m, 4 points",
                                         "Babia Góra, 1725m, 10 points",
                                         "Takajyokki, 1237m, 8 points",
                                         "Hirschberg, 1660m, 6 points",
                                         "Amabilis Mountain, 1396m, 4 points",],
                       "highlightColor": [null, null, null, null, null, null],
                       }
    return test_spots_dict

@pytest.fixture(scope = "module")
def SpotsDownloader_default_instance():
    """Fixture to create an instance of SpotsDownloader with default parameters."""
    return SpotsDownloader()

@pytest.fixture(scope = "module")
def SpotsDownloader_custom_instance():
    """Fixture to create an instance of SpotsDownloader with default parameters."""
    return SpotsDownloader(lookback_time = -3,
                           summits_filename = 'file_with_summits.csv',)

def test_init_default(SpotsDownloader_default_instance):
    """Default initialisation test for SpotsDownloader."""
    assert SpotsDownloader_default_instance.lookback_time == -1, f"Default initiation failed, spots_downloader.lookback_time = {SpotsDownloader_default_instance.lookback_time} (should be -1)"
    assert SpotsDownloader_default_instance.summits_filename == config._SUMMITS_FILENAME, f"Default initiation failed, spots_downloader.summits_filename = {SpotsDownloader_default_instance.summits_filename} (should be {config._SUMMITS_FILENAME})"
    assert SpotsDownloader_default_instance.summits_errors == [], f"Default initiation failed, spots_downloader.summits_errors = {SpotsDownloader_default_instance.summits_errors} (should be empty list)"

def test_init_custom(SpotsDownloader_custom_instance):
    """Parametrised initialisation test for SpotsDownloader."""
    assert SpotsDownloader_custom_instance.lookback_time == -3, f"Parametrized initiation failed, spots_downloader.lookback_time = {SpotsDownloader_custom_instance.lookback_time} (should be -3)"
    assert SpotsDownloader_custom_instance.summits_filename == 'file_with_summits.csv', f"Parametrized initiation failed, spots_downloader.summits_filename = {SpotsDownloader_custom_instance.summits_filename} (should be 'file_with_summits.csv')"
    assert SpotsDownloader_custom_instance.summits_errors == [], f"Default initiation failed, spots_downloader.summits_errors = {SpotsDownloader_custom_instance.summits_errors} (should be empty list)"

def test_define_constants_default(SpotsDownloader_default_instance):
    """Test define_constants method with default parameters."""
    pass

def test_define_constants_custom(SpotsDownloader_custom_instance):
    """Test define_constants method with custom parameters."""
    pass

def test_update_request_parameters_default(SpotsDownloader_default_instance):
    """Test update_request_parameters method with default parameters."""
    SpotsDownloader_default_instance.update_request_parameters()
    assert SpotsDownloader_default_instance.lookback_time == -2, f"Updated default lookback_time should be -2, got {SpotsDownloader_default_instance.lookback_time}"
    assert SpotsDownloader_default_instance._API_URL == 'https://api2.sota.org.uk/api/spots/-2/all', "Incorrect APi URL generated when refreshed after updating self.lookback_time."

def test_update_request_parameters_custom(SpotsDownloader_custom_instance):
    """Test update_request_parameters method with custom parameters."""
    SpotsDownloader_custom_instance.update_request_parameters()
    assert SpotsDownloader_custom_instance.lookback_time == -4, f"Updated custom lookback_time should be -2, got {SpotsDownloader_custom_instance.lookback_time}"
    assert SpotsDownloader_custom_instance._API_URL == 'https://api2.sota.org.uk/api/spots/-4/all', "Incorrect APi URL generated when refreshed after updating self.lookback_time."