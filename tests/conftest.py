import pytest
import pandas as pd

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
        {   # incorrect frequency format for amend_spots_frequencies test
            # non-existing summmitCode for check_error_references test
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
    ]

@pytest.fixture(scope="module")
def mock_visualisation_data_cleared_with_no_reference():
    """Fixture: mock SOTA visualisation data for drop_summits_not_found method."""

    test_timestamps = generate_timestamps_as_strings(7)

    return pd.DataFrame([
        {
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
            'summit_ref': "W7O/CS-098",
            "SummitCode": "W7O/CS-098",
            "AssociationName": "USA - OREGON",
            "RegionName": "OR-CASCADES SOUTH",
            "SummitName": "BIEBERSTEDT BUTTE",
            "longitude": "-122.47310",
            "latitude": "42.41030",
            "Points": "4",
            "BonusPoints": "3",
            "ActivationDate": "",
            "ActivationCall": "",
            'time_since_spot': -0.9998,
            'popup': 'SP0ABC (Amy) on W7O/CS-098',
            'band_color': 'orange',
            'band': '14 MHz',
            'mode_color': 'red',

        },
        # to be removed
        {
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
            'summit_ref': "W8W/CW-076",
            "SummitCode": "W8W/CW-076",
            "AssociationName": "USA - WEST VIRGINIA",
            "RegionName": "CW REGION",
            "SummitName": "AMABILIS MOUNTAIN",
            "longitude": pd.NA,
            "latitude": pd.NA,
            "Points": "4",
            "BonusPoints": "0",
            "ActivationDate": "15/07/2022",
            "ActivationCall": "W8W/TEST",
            'time_since_spot': -0.9998,
            'popup': 'SP0ABC (Amy) on W7O/CS-098',
            'band_color': 'orange',
            'band': '14 MHz',
            'mode_color': 'red',
        },
        {   
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
            'summit_ref': "JA/GM-107",
            "SummitCode": "JA/GM-107",
            "AssociationName": "JAPAN - HONSHU",
            "RegionName": "GUNMA PREFECTURE",
            "SummitName": "TAKAJYOKKI",
            "longitude": "138.67180",
            "latitude": "36.52280",
            "Points": "8",
            "BonusPoints": "3",
            "ActivationDate": "09/12/2021",
            "ActivationCall": "JJ1HWM/1",
            'time_since_spot': -0.9998,
            'popup': 'SP0ABC (Amy) on W7O/CS-098',
            'band_color': 'orange',
            'band': '14 MHz',
            'mode_color': 'red',
        },
    ])