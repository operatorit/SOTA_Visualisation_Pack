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

def test_init_default():
    """Default initialisation test for SpotsDownloader."""
    downloader = SpotsDownloader()
    assert spots_downloader.lookback_time == -1
    assert spots_downloader.summits_filename == config._SUMMITS_FILENAME

def test_init_with_args():
    """Parametrised initialisation test for SpotsDownloader."""
    spots_downloader = SpotsDownloader(lookback_time = -3, 
                                 summits_filename = 'file_with_summits.csv')
    assert spots_downloader.lookback_time == -3
    assert spots_downloader.summits_filename == 'file_with_summits.csv'


# def test__init__():
#     """Test SpotsDownloader initialization."""
#     spots_downloader = SpotsDownloader.SpotsDownloader(lookback_time = -1,
#                                                        summits_filenate = 'test_summits.csv')
#     assert isinstance(spots_downloader, SpotsDownloader.SpotsDownloader), "Initiated object is not a SpotsDownloader instance"
#     assert isinstance(spots_downloader.spots_to_visualisation, pd.DataFrame), "Initiated spots_to_visualisation is not a pd.DataFrame"
#     assert spots_downloader.spots_to_visualisation.empty, "Initiated spots_to_visualisation is NOT empty." # no spots at initiation
#     assert spots_downloader.lookback_time == -1, "Lookcback time initiated incorrectly"
#     assert spots_downloader.summits_filename == 'test_summits.csv' "Summits filename initiated incorrectly"

