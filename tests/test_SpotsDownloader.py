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
def mock_sota_spots_list() -> list:
    """Fixture: test data as a list of dicts (one dict per row)."""

    test_timestamps = generate_timestamps(7)
    
    data = [
        {
            'id': 1001,
            'userID': 2001,
            'timeStamp': test_timestamps[0],
            'comments': 'comment1',
            'callsign': 'SP0ABC',
            'associationCode': 'W7O',
            'summitCode': 'CS-098',
            'activatorCallsign': 'SP0ABC',
            'activatorName': 'Amy',
            'frequency': '14.0615',
            'mode': 'CW',
            'summitDetails': 'Bieberstedt Butte, 1599m, 4 points',
            'highlightColor': None
        },
        {
            'id': 1002,
            'userID': 2002,
            'timeStamp': test_timestamps[1],
            'comments': 'comment2',
            'callsign': 'AG7EDG',
            'associationCode': 'W8W',
            'summitCode': 'CW-076',
            'activatorCallsign': 'AG7EDG',
            'activatorName': 'Bob',
            'frequency': '145.550',
            'mode': 'FM',
            'summitDetails': 'Amabilis Mountain, 1396m, 4 points',
            'highlightColor': None
        },
        {
            'id': 1003,
            'userID': 2003,
            'timeStamp': test_timestamps[2],
            'comments': 'comment3',
            'callsign': 'W6HIJ',
            'associationCode': 'SP',
            'summitCode': 'BZ-001',
            'activatorCallsign': 'W6HIJ',
            'activatorName': 'Charlie',
            'frequency': '7.0615',
            'mode': 'CW',
            'summitDetails': 'Babia Góra, 1725m, 10 points',
            'highlightColor': None
        },
        {
            'id': 1004,
            'userID': 2004,
            'timeStamp': test_timestamps[3],
            'comments': 'comment4',
            'callsign': 'IK1LMN',
            'associationCode': 'JA',
            'summitCode': 'GM-107',
            'activatorCallsign': 'IK1LMN',
            'activatorName': 'David',
            'frequency': '7.158',
            'mode': 'SSB',
            'summitDetails': 'Hirschberg, 1660m, 6 points',
            'highlightColor': None
        },
        {
            'id': 1005,
            'userID': 2005,
            'timeStamp': test_timestamps[4],
            'comments': 'comment5',
            'callsign': 'GB10OPR',
            'associationCode': 'DL',
            'summitCode': 'EW-017',
            'activatorCallsign': 'GB10OPR',
            'activatorName': 'Eve',
            'frequency': '21.055',
            'mode': 'CW',
            'summitDetails': 'Amabilis Mountain, 1396m, 4 points',
            'highlightColor': None
        },
        {
            'id': 1006,
            'userID': 2002,
            'timeStamp': test_timestamps[5],
            'comments': 'comment6',
            'callsign': 'AG7EDG',
            'associationCode': 'W8W',
            'summitCode': 'CW-076',
            'activatorCallsign': 'AG7EDG',
            'activatorName': 'Bob',
            'frequency': '433,500',
            'mode': 'FM',
            'summitDetails': None,
            'highlightColor': None
        },
        { # incorrect frequency format for amend_spots_frequencies test
            'id': 1007,
            'userID': 2006,
            'timeStamp': test_timestamps[6],
            'comments': 'comment7',
            'callsign': 'K1XYZ',
            'associationCode': 'W1',
            'summitCode': 'W1-001',
            'activatorCallsign': 'K1XYZ',
            'activatorName': 'Alice',
            'frequency': '.18',
            'mode': 'CW',
            'summitDetails': None,
            'highlightColor': None
        }

    ]
    return data

@pytest.fixture(scope = "module")
def mock_sota_spots_dataframe(mock_sota_spots_list) -> pd.DataFrame:
    """Fixture: returns a DataFrame based on mock_sota_spots_list."""
    return pd.DataFrame(mock_sota_spots_list)

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

def test_amend_spots_frequencies(default_spots_downloader: SpotsDownloader, 
                                 mock_sota_spots_dataframe:pd.DataFrame) -> None:
    """Test amend_spots_frequencies on test DataFrame."""
    default_spots_downloader.spots_to_visualisation = mock_sota_spots_dataframe.copy()
    default_spots_downloader.amend_spots_frequencies()
    assert default_spots_downloader.spots_to_visualisation.iloc[6]['frequency'] == 0, "Frequency of incorrect format (no integer part) not amended."


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