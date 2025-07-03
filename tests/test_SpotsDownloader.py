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
def default_spots_downloader() -> SpotsDownloader:
    """Fixture: SpotsDownloader instance with default parameters."""
    return SpotsDownloader()

@pytest.fixture(scope = "module")
def custom_spots_downloader() -> SpotsDownloader:
    """Fixture: SpotsDownloader instance with custom parameters."""
    return SpotsDownloader(lookback_time = -3,
                           summits_filename = 'file_with_summits.csv',)

def test_init_default(default_spots_downloader: SpotsDownloader) -> None:
    """Default initialisation test for SpotsDownloader."""
    assert default_spots_downloader.lookback_time == -1, f"Default initiation failed, spots_downloader.lookback_time = {default_spots_downloader.lookback_time} (should be -1)"
    assert default_spots_downloader.summits_filename == config._SUMMITS_FILENAME, f"Default initiation failed, spots_downloader.summits_filename = {default_spots_downloader.summits_filename} (should be {config._SUMMITS_FILENAME})"
    assert default_spots_downloader.summits_errors == [], f"Default initiation failed, spots_downloader.summits_errors = {default_spots_downloader.summits_errors} (should be empty list)"

def test_init_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Parametrised initialisation test for SpotsDownloader."""
    assert custom_spots_downloader.lookback_time == -3, f"Parametrized initiation failed, spots_downloader.lookback_time = {custom_spots_downloader.lookback_time} (should be -3)"
    assert custom_spots_downloader.summits_filename == 'file_with_summits.csv', f"Parametrized initiation failed, spots_downloader.summits_filename = {custom_spots_downloader.summits_filename} (should be 'file_with_summits.csv')"
    assert custom_spots_downloader.summits_errors == [], f"Default initiation failed, spots_downloader.summits_errors = {custom_spots_downloader.summits_errors} (should be empty list)"

def test_define_constants_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test define_constants method with default parameters."""
    pass

def test_define_constants_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test define_constants method with custom parameters."""
    pass

def test_update_request_parameters_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test update_request_parameters method with default parameters."""
    default_spots_downloader.update_request_parameters()
    assert default_spots_downloader.lookback_time == -2, f"Updated default lookback_time should be -2, got {default_spots_downloader.lookback_time}"
    assert default_spots_downloader._API_URL == 'https://api2.sota.org.uk/api/spots/-2/all', "Incorrect APi URL generated when refreshed after updating self.lookback_time."

def test_update_request_parameters_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test update_request_parameters method with custom parameters."""
    custom_spots_downloader.update_request_parameters()
    assert custom_spots_downloader.lookback_time == -4, f"Updated custom lookback_time should be -2, got {custom_spots_downloader.lookback_time}"
    assert custom_spots_downloader._API_URL == 'https://api2.sota.org.uk/api/spots/-4/all', "Incorrect APi URL generated when refreshed after updating self.lookback_time."

def test_process_spots_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test process_spots on default instance."""
    pass

def test_process_spots_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test process_spots on custom instance."""
    pass

def test_get_spots_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test get_spots on default instance."""
    pass

def test_get_spots_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test get_spots on custom instance."""
    pass

def test_amend_spots_frequencies_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test amend_spots_frequencies on default instance."""
    pass

def test_amend_spots_frequencies_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test amend_spots_frequencies on custom instance."""
    pass

def test_amend_spots_datatypes_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test amend_spots_datatypes on default instance."""
    pass

def test_amend_spots_datatypes_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test amend_spots_datatypes on custom instance."""
    pass

def test_add_summit_codes_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test add_summit_codes on default instance."""
    pass

def test_add_summit_codes_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test add_summit_codes on custom instance."""
    pass

def test_prepare_spots_to_join_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test prepare_spots_to_join on default instance."""
    pass

def test_prepare_spots_to_join_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test prepare_spots_to_join on custom instance."""
    pass

def test_get_summits_list_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test get_summits_list on default instance."""
    pass

def test_get_summits_list_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test get_summits_list on custom instance."""
    pass

def test_check_error_references_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test check_error_references on default instance."""
    pass

def test_check_error_references_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test check_error_references on custom instance."""
    pass

def test_join_spots_with_summits_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test join_spots_with_summits on default instance."""
    pass

def test_join_spots_with_summits_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test join_spots_with_summits on custom instance."""
    pass

def test_add_time_markers_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test add_time_markers on default instance."""
    pass

def test_add_time_markers_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test add_time_markers on custom instance."""
    pass

def test_create_visualisation_data_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test create_visualisation_data on default instance."""
    pass

def test_create_visualisation_data_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test create_visualisation_data on custom instance."""
    pass

def test_remove_unused_columns_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test remove_unused_columns on default instance."""
    pass

def test_remove_unused_columns_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test remove_unused_columns on custom instance."""
    pass

def test_drop_summits_not_found_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test drop_summits_not_found on default instance."""
    pass

def test_drop_summits_not_found_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Test drop_summits_not_found on custom instance."""
    pass