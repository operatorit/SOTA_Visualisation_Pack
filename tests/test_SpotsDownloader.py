import pytest
import pandas as pd


from datetime import datetime, timedelta
from unittest.mock import MagicMock

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
            'frequency': '433.500',
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

@pytest.fixture
def create_expected_bands_df():
    """Fixture: expected DataFrame for self._BANDS, defined as a list of dicts (one per row)."""
    bands_data = [
        {'band': '1.8 MHz or below', 'lower_freq': 0,    'upper_freq': 2.5,    'color': 'saddlebrown'},
        {'band': '3.5 MHz',          'lower_freq': 3,    'upper_freq': 4,      'color': 'chocolate'},
        {'band': '5 MHz',            'lower_freq': 4.5,  'upper_freq': 5.5,    'color': 'brown'},
        {'band': '7 MHz',            'lower_freq': 6,    'upper_freq': 8,      'color': 'red'},
        {'band': '10 MHz',           'lower_freq': 9,    'upper_freq': 11,     'color': 'salmon'},
        {'band': '14 MHz',           'lower_freq': 13,   'upper_freq': 15,     'color': 'orange'},
        {'band': '18 MHz',           'lower_freq': 16,   'upper_freq': 18.5,   'color': 'gold'},
        {'band': '21 MHz',           'lower_freq': 19,   'upper_freq': 23,     'color': 'yellow'},
        {'band': '24 MHz',           'lower_freq': 24,   'upper_freq': 26,     'color': 'olivedrab'},
        {'band': '28 MHz',           'lower_freq': 27,   'upper_freq': 35,     'color': 'green'},
        {'band': '50 MHz',           'lower_freq': 45,   'upper_freq': 55,     'color': 'lime'},
        {'band': '70 MHz',           'lower_freq': 65,   'upper_freq': 75,     'color': 'cyan'},
        {'band': '144 MHz',          'lower_freq': 142,  'upper_freq': 148,    'color': 'blue'},
        {'band': '220 MHz',          'lower_freq': 210,  'upper_freq': 240,    'color': 'purple'},
        {'band': '433 MHz',          'lower_freq': 420,  'upper_freq': 460,    'color': 'magenta'},
        {'band': '900 MHz or above', 'lower_freq': 850,  'upper_freq': 500000, 'color': 'pink'},
    ]
    bands_df = pd.DataFrame(bands_data)
    bands_df.set_index('band', drop=True, inplace=True)
    bands_df['color'] = bands_df['color'].astype('string')
    return  bands_df

@pytest.fixture
def create_expected_modes_df():
    """Fixture: expected DataFrame for self._MODES, defined as a list of dicts (one per row)."""
    modes_data = [
        {'mode': 'AM',    'color': 'lime'},
        {'mode': 'CW',    'color': 'red'},
        {'mode': 'Data',  'color': 'cyan'},
        {'mode': 'DV',    'color': 'magenta'},
        {'mode': 'FM',    'color': 'yellow'},
        {'mode': 'SSB',   'color': 'blue'},
        {'mode': 'Other', 'color': 'orange'},
    ]
    modes_df = pd.DataFrame(modes_data)
    modes_df['color'] = modes_df['color'].astype('string')
    modes_df['mode'] = modes_df['mode'].astype('string')
    return modes_df


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
    asserts_summits_filename_errors_list_are_correct(default_spots_downloader)

def test_init_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Parametrised initialisation test for SpotsDownloader."""
    assert custom_spots_downloader.lookback_time == -3, f"Parametrized initiation failed, spots_downloader.lookback_time = {custom_spots_downloader.lookback_time} (should be -3)"
    asserts_summits_filename_errors_list_are_correct(custom_spots_downloader, 
                                                     summits_filename = 'file_with_summits.csv')

def asserts_summits_filename_errors_list_are_correct(initated_instance: SpotsDownloader,
                                                     summits_filename:str = config._SUMMITS_FILENAME,
                                                     errors_list:list = []) -> None:
    """Assert that summits_filename and errors_list are correct."""
    assert initated_instance.summits_filename == summits_filename, f"Parametrized initiation failed, spots_downloader.summits_filename = {initated_instance.summits_filename} (should be {summits_filename})"
    assert initated_instance.summits_errors == errors_list, f"Default initiation failed, spots_downloader.summits_errors = {initated_instance.summits_errors} (should be {errors_list})"

def test_define_constants_default(default_spots_downloader: SpotsDownloader,
                                  create_expected_bands_df: pd.DataFrame,
                                  create_expected_modes_df: pd.DataFrame) -> None:
    """Test define_constants method with default parameters."""
    default_spots_downloader.define_constants()
    assert default_spots_downloader._API_URL == 'https://api2.sota.org.uk/api/spots/-1/all', f"self._API_URL is {default_spots_downloader._API_URL}, should be 'https://api2.sota.org.uk/api/spots/-1/all."
    assert_bands_and_modes_are_correct(default_spots_downloader, create_expected_bands_df, create_expected_modes_df)

def test_define_constants_custom(custom_spots_downloader: SpotsDownloader, 
                                 create_expected_bands_df: pd.DataFrame,
                                 create_expected_modes_df: pd.DataFrame) -> None:
    """Test define_constants method with custom parameters."""
    custom_spots_downloader.define_constants()
    assert custom_spots_downloader._API_URL == 'https://api2.sota.org.uk/api/spots/-3/all', f"self._API_URL is {custom_spots_downloader._API_URL}, should be 'https://api2.sota.org.uk/api/spots/-3/all."
    assert_bands_and_modes_are_correct(custom_spots_downloader, create_expected_bands_df, create_expected_modes_df)

def assert_bands_and_modes_are_correct(initated_instance: SpotsDownloader, 
                                       expected_bands_df: pd.DataFrame, 
                                       expected_modes_df: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(initated_instance._BANDS, expected_bands_df)
    pd.testing.assert_frame_equal(initated_instance._MODES, expected_modes_df)

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

@pytest.mark.skip(reason="test_shell")
def test_process_spots_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test process_spots. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass

def test_get_spots(default_spots_downloader: SpotsDownloader, 
                           mock_sota_spots_list, 
                           monkeypatch) -> None:
    """Test get_spots. Tested on default instance only as the method do not depend on initialisation parameters."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_sota_spots_list
    monkeypatch.setattr('requests.get', lambda *args, **kwargs: mock_resp)

    spots_mock_df = default_spots_downloader.get_spots()
    assert not spots_mock_df.empty, "DataFrame returned from mock is empty."
    assert len(spots_mock_df) == len(mock_sota_spots_list), f"Returned DataFrame has {len(spots_mock_df)} rows, expected {len(mock_sota_spots_list)}."
    assert set(spots_mock_df.columns) >= set(mock_sota_spots_list[0].keys()), "Returned DataFrame columns do not match mock data keys."

@pytest.mark.skip(reason="test_shell")
def test_amend_spots_frequencies(default_spots_downloader: SpotsDownloader,
                                 mock_sota_spots_list,
                                 ) -> None:
    """Test amend_spots_frequencies. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass
@pytest.mark.skip(reason="test_shell")
def test_amend_spots_datatypes(default_spots_downloader: SpotsDownloader,
                               mock_sota_spots_list
                               ) -> None:
    """Test amend_spots_datatypes. Tested on default instance only as the method do not depend on initialisation parameters."""
    # default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    # default_spots_downloader.amend_spots_datatypes()
    # print(default_spots_downloader.dtypes)
    pass

    # default_spots_downloader.spots_to_visualisation['activatorCallsign'] = default_spots_downloader.spots_to_visualisation['activatorCallsign'].astype('string')
    # default_spots_downloader.spots_to_visualisation['associationCode'] = default_spots_downloader.spots_to_visualisation['associationCode'].astype('string')
    # default_spots_downloader.spots_to_visualisation['summitCode'] = default_spots_downloader.spots_to_visualisation['summitCode'].astype('string')
    # default_spots_downloader.spots_to_visualisation['mode'] = default_spots_downloader.spots_to_visualisation['mode'].astype('string')
    # default_spots_downloader.spots_to_visualisation['frequency'] = default_spots_downloader.spots_to_visualisation['frequency'].astype('float')
    # self.spots_to_visualisation['timeStamp'] = pd.to_datetime(self.spots_to_visualisation['timeStamp'], format="%Y-%m-%dT%H:%M:%S")

def test_add_summit_codes(default_spots_downloader: SpotsDownloader,
                           mock_sota_spots_list
                           ) -> None:
    """Test add_summit_codes. Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    default_spots_downloader.add_summit_codes()
    assert 'summit_ref' in default_spots_downloader.spots_to_visualisation.columns, "Column summitCode not found in spots_to_visualisation DataFrame after adding summit codes."
    assert default_spots_downloader.spots_to_visualisation['summit_ref'].notnull().all(), "Not all summit codes are filled in the DataFrame."
    assert default_spots_downloader.spots_to_visualisation['summit_ref'].tolist() == ['W7O/CS-098', 'W8W/CW-076', 'SP/BZ-001', 'JA/GM-107', 'DL/EW-017', 'W8W/CW-076', 'W1/W1-001'], "Summits references not concatenated correctly."

@pytest.mark.skip(reason="test_shell")
def test_prepare_spots_to_join(default_spots_downloader: SpotsDownloader) -> None:
    """Test prepare_spots_to_join. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass

@pytest.mark.skip(reason="test_shell")
def test_get_summits_list(default_spots_downloader: SpotsDownloader) -> None:
    """Test get_summits_list. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass

@pytest.mark.skip(reason="test_shell")
def test_check_error_references(default_spots_downloader: SpotsDownloader) -> None:
    """Test check_error_references. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass

@pytest.mark.skip(reason="test_shell")
def test_add_time_markers(default_spots_downloader: SpotsDownloader) -> None:
    """Test add_time_markers. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass

@pytest.mark.skip(reason="test_shell")
def test_create_visualisation_data(default_spots_downloader: SpotsDownloader) -> None:
    """Test create_visualisation_data. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass

@pytest.mark.skip(reason="test_shell")
def test_remove_unused_columns(default_spots_downloader: SpotsDownloader) -> None:
    """Test remove_unused_columns. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass

@pytest.mark.skip(reason="test_shell")
def test_drop_summits_not_found(default_spots_downloader: SpotsDownloader) -> None:
    """Test drop_summits_not_found. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass

