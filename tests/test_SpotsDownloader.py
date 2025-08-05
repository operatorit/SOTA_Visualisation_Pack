import pytest
import pandas as pd
import types

from datetime import datetime, timedelta
from unittest.mock import MagicMock

from SpotsDownloader import SpotsDownloader
import config


def generate_timestamps_as_strings(n = 6):
    """Generate a list of n timestamps for testing."""
    start_time = datetime.now()
    return [str((start_time - timedelta(minutes=5*i)).isoformat()).split('.')[0] for i in range(n)]

@pytest.fixture(scope = "module")
def mock_sota_spots_list() -> list:
    """Fixture: test data as a list of dicts (one dict per row)."""

    test_timestamps = generate_timestamps_as_strings(7)
    
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

@pytest.fixture(scope="module")
def mock_summits_list():
    """Fixture: mock SOTA summits data for get_summits_list test (all uppercase, real and synthetic)."""
    return [
        {
            "SummitCode": "W7O/CS-098",
            "AssociationName": "USA - OREGON",
            "RegionName": "OR-CASCADES SOUTH",
            "SummitName": "BIEBERSTEDT BUTTE",
            "AltM": "1599",
            "AltFt": "5246",
            "GridRef1": "-122.4731",
            "GridRef2": "42.4103",
            "Longitude": "-122.47310",
            "Latitude": "42.41030",
            "Points": "4",
            "BonusPoints": "3",
            "ValidFrom": "01/07/2010",
            "ValidTo": "31/12/2099",
            "ActivationCount": "0",
            "ActivationDate": "",
            "ActivationCall": ""
        },
        {
            "SummitCode": "W8W/CW-076",
            "AssociationName": "USA - WEST VIRGINIA",
            "RegionName": "CW REGION",
            "SummitName": "AMABILIS MOUNTAIN",
            "AltM": "1396",
            "AltFt": "4580",
            "GridRef1": "-80.1234",
            "GridRef2": "38.5678",
            "Longitude": "-80.12340",
            "Latitude": "38.56780",
            "Points": "4",
            "BonusPoints": "0",
            "ValidFrom": "01/01/2015",
            "ValidTo": "31/12/2099",
            "ActivationCount": "2",
            "ActivationDate": "15/07/2022",
            "ActivationCall": "W8W/TEST"
        },
        {
            "SummitCode": "SP/BZ-001",
            "AssociationName": "POLAND",
            "RegionName": "BESKIDY ZACHODNIE",
            "SummitName": "DIABLAK (BABIA GÓRA)",
            "AltM": "1725",
            "AltFt": "5659",
            "GridRef1": "19.5296",
            "GridRef2": "49.5732",
            "Longitude": "19.52960",
            "Latitude": "49.57320",
            "Points": "10",
            "BonusPoints": "3",
            "ValidFrom": "01/04/2008",
            "ValidTo": "31/12/2099",
            "ActivationCount": "179",
            "ActivationDate": "13/03/2022",
            "ActivationCall": "SP9ML/P"
        },
        {
            "SummitCode": "JA/GM-107",
            "AssociationName": "JAPAN - HONSHU",
            "RegionName": "GUNMA PREFECTURE",
            "SummitName": "TAKAJYOKKI",
            "AltM": "1237",
            "AltFt": "4059",
            "GridRef1": "138.6718",
            "GridRef2": "36.5228",
            "Longitude": "138.67180",
            "Latitude": "36.52280",
            "Points": "8",
            "BonusPoints": "3",
            "ValidFrom": "01/11/2021",
            "ValidTo": "31/12/2099",
            "ActivationCount": "1",
            "ActivationDate": "09/12/2021",
            "ActivationCall": "JJ1HWM/1"
        },
        {
            "SummitCode": "DL/EW-017",
            "AssociationName": "GERMANY (ALPINE)",
            "RegionName": "ESTERGEBIRGE/WALCHENSEEBERGE",
            "SummitName": "HIRSCHBERG",
            "AltM": "1659",
            "AltFt": "5443",
            "GridRef1": "11.2414",
            "GridRef2": "47.6008",
            "Longitude": "11.24140",
            "Latitude": "47.60080",
            "Points": "6",
            "BonusPoints": "3",
            "ValidFrom": "01/03/2004",
            "ValidTo": "31/12/2099",
            "ActivationCount": "16",
            "ActivationDate": "27/02/2022",
            "ActivationCall": "DO2MPS/P"
        },
        {
            "SummitCode": "W1/W1-001",
            "AssociationName": "USA - NEW ENGLAND",
            "RegionName": "W1 REGION",
            "SummitName": "MOUNT WASHINGTON",
            "AltM": "1917",
            "AltFt": "6290",
            "GridRef1": "-71.3036",
            "GridRef2": "44.2706",
            "Longitude": "-71.30360",
            "Latitude": "44.27060",
            "Points": "10",
            "BonusPoints": "3",
            "ValidFrom": "01/01/2000",
            "ValidTo": "31/12/2099",
            "ActivationCount": "100",
            "ActivationDate": "01/08/2025",
            "ActivationCall": "K1XYZ/P"
        }
    ]

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

def test_amend_spots_frequencies(default_spots_downloader: SpotsDownloader,
                                 mock_sota_spots_list,
                                 ) -> None:
    """Test amend_spots_frequencies. Incorrect frequencies (not in nn.nnn format) should be set to 0. 
    Tested on default instance only as the method do not depend on initialisation parameters."""
    
    incorrect_frequencies_references = {'fq1': {'id': 1007,
                                                'userID': 2006,},}
    
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    assert len(default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['frequency'] == 0]) == 0, "Non-zero frequencies found in initial test dataframe."

    default_spots_downloader.amend_spots_frequencies()
    for incorrect_frequency_reference in incorrect_frequencies_references.values():
        assert default_spots_downloader.spots_to_visualisation.loc[(default_spots_downloader.spots_to_visualisation['id'] == incorrect_frequency_reference['id'])
                                                                   & (default_spots_downloader.spots_to_visualisation['userID'] == incorrect_frequency_reference['userID']),
                                                                   'frequency'].values[0] == 0, f"Frequency for id = {incorrect_frequency_reference['id']}, userID = {incorrect_frequency_reference['userID']} should be 0."
                                                                     
def test_amend_spots_datatypes(default_spots_downloader: SpotsDownloader,
                               mock_sota_spots_list
                               ) -> None:
    """Test amend_spots_datatypes - if data types are as expected after method run. 
    Tested on default instance only as the method do not depend on initialisation parameters."""
    expected_columns_dtypes = {'activatorCallsign': 'string',
                               'associationCode': 'string',
                               'summitCode': 'string',
                               'mode': 'string',
                               'frequency': 'float',
                               'timeStamp': 'datetime64[ns]',
                               }
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    default_spots_downloader.amend_spots_datatypes()
    
    for column_name in expected_columns_dtypes.keys():
        assert default_spots_downloader.spots_to_visualisation[column_name].dtype == expected_columns_dtypes[column_name], f"Incorrect datatype for column {column_name}: default_spots_downloader.spots_to_visualisation[column_name].dtype (expected: {expected_columns_dtypes[column_name]})."
    
def test_add_summit_codes(default_spots_downloader: SpotsDownloader,
                           mock_sota_spots_list: list[dict]
                           ) -> None:
    """Test add_summit_codes - if associationCode and summitCode are concatenated correctly ito summit_ref column.
    Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    default_spots_downloader.add_summit_codes()
    assert 'summit_ref' in default_spots_downloader.spots_to_visualisation.columns, "Column summit_ref not found in spots_to_visualisation DataFrame after adding summit codes."
    assert default_spots_downloader.spots_to_visualisation['summit_ref'].notnull().all(), "Not all summit codes are filled in the DataFrame."
    assert default_spots_downloader.spots_to_visualisation['summit_ref'].tolist() == ['W7O/CS-098', 'W8W/CW-076', 'SP/BZ-001', 'JA/GM-107', 'DL/EW-017', 'W8W/CW-076', 'W1/W1-001'], "Summits references not concatenated correctly."

def test_prepare_spots_to_join(default_spots_downloader: SpotsDownloader,
                               mock_sota_spots_list
                               ) -> None:
    """Test prepare_spots_to_join. Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    default_spots_downloader.add_summit_codes()
    length_no_duplicates = len(default_spots_downloader.spots_to_visualisation.groupby(['callsign', 'summit_ref']).first())

    default_spots_downloader.prepare_spots_to_join()

    assert len(default_spots_downloader.spots_to_visualisation) == length_no_duplicates, f"Incorrect spots dataframe length after duplicates removal. Expected; {length_no_duplicates}, got {len(default_spots_downloader.spots_to_visualisation)}."
    assert default_spots_downloader.spots_to_visualisation[['callsign', 'summit_ref']].duplicated().sum() == 0, "Duplicated pairs callsign-summit_ref found on spots list after duplicates removal."
    assert default_spots_downloader.spots_to_visualisation.loc[(default_spots_downloader.spots_to_visualisation['callsign'] == 'AG7EDG')
                                                               & (default_spots_downloader.spots_to_visualisation['summit_ref'] == 'W8W/CW-076'), 
                                                               'frequency'].item() == '145.550', f"Incorrect row deleted for AG7EDG, not the newest one left in the DataFrame."
    assert list(default_spots_downloader.spots_to_visualisation.index) == list(range(0, length_no_duplicates)), f"Reindexing after duplicates removal failed. Index is {default_spots_downloader.spots_to_visualisation.index}, expected {range(0, length_no_duplicates)}."
    
@pytest.mark.skip(reason="test_shell")
def test_get_summits_list():
    pass

def test_get_summits_list_mock(default_spots_downloader: SpotsDownloader,
                          mock_summits_list: list[dict]) -> None:
    """Test if mock_summits_list format is correct and it fits SOTA_summits_data object in SpotsDownloader instance.
    Tested on default initialisation as do not depend on initialisation parameters."""

    default_spots_downloader.SOTA_summits_data = pd.DataFrame(mock_summits_list)

    assert isinstance(default_spots_downloader.SOTA_summits_data, pd.DataFrame), "SOTA_summits_data is not a pandas DataFrame."
    expected_codes = [s['SummitCode'] for s in mock_summits_list]
    assert set(default_spots_downloader.SOTA_summits_data['SummitCode']) == set(expected_codes), f"Returned SummitCodes do not match expected: {expected_codes}"
    # Sprawdź, czy wszystkie kolumny są obecne
    required_columns = [
        "SummitCode", "AssociationName", "RegionName", "SummitName", "AltM", "AltFt",
        "GridRef1", "GridRef2", "Longitude", "Latitude", "Points", "BonusPoints",
        "ValidFrom", "ValidTo", "ActivationCount", "ActivationDate", "ActivationCall"
    ]
    for col in required_columns:
        assert col in default_spots_downloader.SOTA_summits_data.columns, f"Missing column: {col}"

# @pytest.mark.skip(reason="test_shell")
def test_join_spots_with_summits(default_spots_downloader: SpotsDownloader,
                                 mock_sota_spots_list: list[dict],
                                 mock_summits_list: list[dict]) -> None:
    """Tests join_spots_with_summits. Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    default_spots_downloader.amend_spots_datatypes()
    default_spots_downloader.add_summit_codes()
    default_spots_downloader.prepare_spots_to_join()

    initial_spots_df_len = len(default_spots_downloader.spots_to_visualisation)

    default_spots_downloader.SOTA_summits_data = pd.DataFrame(mock_summits_list)

    default_spots_downloader.join_spots_with_summits()
    print(default_spots_downloader.spots_to_visualisation.columns)
    assert len(default_spots_downloader.spots_to_visualisation) == initial_spots_df_len, f"Merging spots and summits DataFrames changed number of spots to visualisation by {len(default_spots_downloader.spots_to_visualisation) - initial_spots_df_len} rows."
    for column_name in ['Longitude', 'Latitude', 'Points', 'SummitName']:
        assert column_name not in default_spots_downloader.spots_to_visualisation.columns, f"Column {column_name} is still present in spots_to_visualisation DataFrame, while it should be renamed."
    for column_name in ['longitude', 'latitude', 'points', 'summitName']:
        assert column_name in default_spots_downloader.spots_to_visualisation.columns, f"Column {column_name} is missing from spots_to_visualisation DataFrame, while it should be present."
    
    for summit_reference in default_spots_downloader.spots_to_visualisation['summit_ref'].unique():
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'SummitCode'].item() == summit_reference, f"Summit reference {summit_reference} does not match SummitCode after merging spots with summits list."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'summitName'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'SummitName'].item(), f"Summit name for {summit_reference} does not match summits list after merging spots with summits list. Should be {default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'SummitName'].item()}, is {default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'summitName'].item()}, is {default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'summitName'].item()}."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'AssociationName'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'AssociationName'].item(), f"AssociationName for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'RegionName'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'RegionName'].item(), f"RegionName for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'AltM'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'AltM'].item(), f"AltM for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'AltFt'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'AltFt'].item(), f"AltFt for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'GridRef1'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'GridRef1'].item(), f"GridRef1 for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'GridRef2'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'GridRef2'].item(), f"GridRef2 for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'longitude'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'Longitude'].item(), f"longitude for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'latitude'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'Latitude'].item(), f"latitude for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'points'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'Points'].item(), f"points for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'BonusPoints'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'BonusPoints'].item(), f"BonusPoints for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'ValidFrom'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'ValidFrom'].item(), f"ValidFrom for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'ValidTo'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'ValidTo'].item(), f"ValidTo for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'ActivationCount'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'ActivationCount'].item(), f"ActivationCount for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'ActivationDate'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'ActivationDate'].item(), f"ActivationDate for {summit_reference} does not match after merging."
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'ActivationCall'].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, 'ActivationCall'].item(), f"ActivationCall for {summit_reference} does not match after merging."

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

