import pytest
import pandas as pd
import types

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import config
from SpotsDownloader import SpotsDownloader
from conftest import (timestamps_for_tests, 
                      now_for_tests, 
                      mock_sota_spots_list, 
                      mock_sota_spots_after_amend_frequencies_dataframe, 
                      mock_sota_spots_after_amend_datatypes_dataframe, 
                      mock_sota_spots_after_add_summit_codes_dataframe,
                      mock_sota_spots_after_prepare_spots_to_join_dataframe,)
 #_dataframe, mock_sota_spots_amended_frequencies, create_expected_modes_df, create_expected_bands_df, mock_summits_list, mock_visualisation_data_cleared_with_no_reference

def normalize_text(s: str) -> str:
    """Removes redundant whitespace and joins everything into a single string."""
    return ' '.join(s.split())

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
    check_summits_filename_errors_list_are_correct(default_spots_downloader)

def test_init_custom(custom_spots_downloader: SpotsDownloader) -> None:
    """Parametrised initialisation test for SpotsDownloader."""
    assert custom_spots_downloader.lookback_time == -3, f"Parametrized initiation failed, spots_downloader.lookback_time = {custom_spots_downloader.lookback_time} (should be -3)"
    check_summits_filename_errors_list_are_correct(custom_spots_downloader, 
                                                     summits_filename = 'file_with_summits.csv')

def check_summits_filename_errors_list_are_correct(initated_instance: SpotsDownloader,
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
    check_bands_and_modes_are_correct(default_spots_downloader, create_expected_bands_df, create_expected_modes_df)

def test_define_constants_custom(custom_spots_downloader: SpotsDownloader, 
                                 create_expected_bands_df: pd.DataFrame,
                                 create_expected_modes_df: pd.DataFrame) -> None:
    """Test define_constants method with custom parameters."""
    custom_spots_downloader.define_constants()
    assert custom_spots_downloader._API_URL == 'https://api2.sota.org.uk/api/spots/-3/all', f"self._API_URL is {custom_spots_downloader._API_URL}, should be 'https://api2.sota.org.uk/api/spots/-3/all."
    check_bands_and_modes_are_correct(custom_spots_downloader, create_expected_bands_df, create_expected_modes_df)

def check_bands_and_modes_are_correct(initated_instance: SpotsDownloader, 
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
    assert custom_spots_downloader.lookback_time == -4, f"Updated custom lookback_time should be -4, got {custom_spots_downloader.lookback_time}"
    assert custom_spots_downloader._API_URL == 'https://api2.sota.org.uk/api/spots/-4/all', "Incorrect APi URL generated when refreshed after updating self.lookback_time."

@pytest.mark.skip(reason="test_shell")
def test_process_spots_default(default_spots_downloader: SpotsDownloader) -> None:
    """Test process_spots. Tested on default instance only as the method do not depend on initialisation parameters."""
    pass

def test_get_spots(default_spots_downloader: SpotsDownloader, 
                   mock_sota_spots_list: list[dict], 
                   monkeypatch: pytest.MonkeyPatch
                   ) -> None:
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
                                 mock_sota_spots_dataframe: pd.DataFrame,
                                 mock_sota_spots_after_amend_frequencies_dataframe: pd.DataFrame,
                                 ) -> None:
    """Test amend_spots_frequencies. Incorrect frequencies (not in nn.nnn format) should be set to 0. 
    Tested on default instance only as the method do not depend on initialisation parameters."""
    
    default_spots_downloader.spots_to_visualisation = mock_sota_spots_dataframe

    assert len(default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['frequency'] == 0]) == 0, "Non-zero frequencies found in initial test dataframe."

    default_spots_downloader.amend_spots_frequencies()

    pd.testing.assert_frame_equal(default_spots_downloader.spots_to_visualisation, 
                                  mock_sota_spots_after_amend_frequencies_dataframe, 
                                  check_dtype = False), f"DataFrame SpotsDownloader.spots_to_visualisation after amend_spots_frequencies does not meet expected data. Differences: {default_spots_downloader.spots_to_visualisation.compare(mock_sota_spots_after_amend_frequencies_dataframe)}"
                                                                                                     
def test_amend_spots_datatypes(default_spots_downloader: SpotsDownloader,
                               mock_sota_spots_after_amend_frequencies_dataframe: pd.DataFrame,
                               mock_sota_spots_after_amend_datatypes_dataframe: pd.DataFrame,
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
    default_spots_downloader.spots_to_visualisation = mock_sota_spots_after_amend_frequencies_dataframe
    default_spots_downloader.amend_spots_datatypes()
    
    for column_name in expected_columns_dtypes.keys():
        assert default_spots_downloader.spots_to_visualisation[column_name].dtype == expected_columns_dtypes[column_name], f"Incorrect datatype for column {column_name}: default_spots_downloader.spots_to_visualisation[column_name].dtype (expected: {expected_columns_dtypes[column_name]})."
    print(mock_sota_spots_after_amend_datatypes_dataframe.dtypes)
    pd.testing.assert_frame_equal(default_spots_downloader.spots_to_visualisation,
                                  mock_sota_spots_after_amend_datatypes_dataframe,
                                  check_dtype = True), f"DataFrame SpotsDownloader.spots_to_visualisation after amend_spots_datatypes does not meet expected data. Differences: {default_spots_downloader.spots_to_visualisation.compare(mock_sota_spots_after_amend_datatypes_dataframe)}"
                                  
def test_add_summit_codes(default_spots_downloader: SpotsDownloader,
                           mock_sota_spots_after_amend_datatypes_dataframe: pd.DataFrame,
                           mock_sota_spots_after_add_summit_codes_dataframe: pd.DataFrame,
                           ) -> None:
    """Test add_summit_codes - if associationCode and summitCode are concatenated correctly ito summit_ref column.
    Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = mock_sota_spots_after_amend_datatypes_dataframe
    default_spots_downloader.add_summit_codes()

    assert 'summit_ref' in default_spots_downloader.spots_to_visualisation.columns, "Column summit_ref not found in spots_to_visualisation DataFrame after adding summit codes."
    assert default_spots_downloader.spots_to_visualisation['summit_ref'].notnull().all(), "Not all summit codes are filled in the DataFrame."

    assert default_spots_downloader.spots_to_visualisation['summit_ref'].tolist() == ['W7O/CS-098', 'W8W/CW-076', 'SP/BZ-001', 'JA/GM-107', 'DL/EW-017', 'W8W/CW-076', 'W1/W1-001'], "Summits references not concatenated correctly."

    pd.testing.assert_frame_equal(default_spots_downloader.spots_to_visualisation,
                                  mock_sota_spots_after_add_summit_codes_dataframe,
                                  check_dtype = True), f"DataFrame SpotsDownloader.spots_to_visualisation after add_summit_codes does not meet expected data. Differences: {default_spots_downloader.spots_to_visualisation.compare(mock_sota_spots_after_add_summit_codes_dataframe)}"   

def test_prepare_spots_to_join(default_spots_downloader: SpotsDownloader,
                               mock_sota_spots_after_add_summit_codes_dataframe: pd.DataFrame,
                               mock_sota_spots_after_prepare_spots_to_join_dataframe: pd.DataFrame,
                               ) -> None:
    """Test prepare_spots_to_join. Tested on default instance only as the method do not depend on initialisation parameters."""

    default_spots_downloader.spots_to_visualisation = mock_sota_spots_after_add_summit_codes_dataframe
    
    length_no_duplicates = len(default_spots_downloader.spots_to_visualisation.groupby(['callsign', 'summit_ref']).first())

    default_spots_downloader.prepare_spots_to_join()
    print(default_spots_downloader.spots_to_visualisation['frequency'])
    print(mock_sota_spots_after_prepare_spots_to_join_dataframe['frequency'])

    assert len(default_spots_downloader.spots_to_visualisation) == length_no_duplicates, f"Incorrect spots dataframe length after duplicates removal. Expected; {length_no_duplicates}, got {len(default_spots_downloader.spots_to_visualisation)}."
    assert default_spots_downloader.spots_to_visualisation[['callsign', 'summit_ref']].duplicated().sum() == 0, "Duplicated pairs callsign-summit_ref found on spots list after duplicates removal."
    assert default_spots_downloader.spots_to_visualisation.loc[(default_spots_downloader.spots_to_visualisation['callsign'] == 'AG7EDG')
                                                               & (default_spots_downloader.spots_to_visualisation['summit_ref'] == 'W8W/CW-076'), 
                                                               'frequency'].item() == 145.550, f"Incorrect row deleted for AG7EDG, not the newest one left in the DataFrame."
    assert list(default_spots_downloader.spots_to_visualisation.index) == list(range(0, length_no_duplicates)), f"Reindexing after duplicates removal failed. Index is {default_spots_downloader.spots_to_visualisation.index}, expected {range(0, length_no_duplicates)}."

    pd.testing.assert_frame_equal(default_spots_downloader.spots_to_visualisation, mock_sota_spots_after_prepare_spots_to_join_dataframe), "DataFrame SpotsDownloader.spots_to_visualisation after prepare_spots_to_join does not meet expected data. Differences: {default_spots_downloader.spots_to_visualisation.compare(mock_sota_spots_after_add_summit_codes_dataframe)}"   

@pytest.mark.skip(reason="test_shell")    
def test_get_summits_list_file_not_found(custom_spots_downloader: SpotsDownloader,
                                         capsys):
    """Tests if get_summits_list raises FileNotfoundError if looking for non-existing file (like in custom initialisation for tests)."""
    try:
        custom_spots_downloader.get_summits_list()
    except FileNotFoundError:
        pass 

    assert capsys.readouterr().out == f"File {custom_spots_downloader.summits_filename} not found. Make sure it's saved in project's directory.\n", "No error message printed for missing file."

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

@pytest.mark.skip(reason="test_shell")
def test_check_error_references(default_spots_downloader: SpotsDownloader,
                                 mock_sota_spots_list: list[dict],
                                 mock_summits_list: list[dict]) -> None:
    """Test check_error_references. Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    
    default_spots_downloader.amend_spots_datatypes()
    default_spots_downloader.add_summit_codes()
    default_spots_downloader.prepare_spots_to_join()

    default_spots_downloader.SOTA_summits_data = pd.DataFrame(mock_summits_list)

    default_spots_downloader.check_error_references()

    assert len(default_spots_downloader.summits_errors) == 1, f"There should be 1 summit error, got {len(default_spots_downloader.summits_errors)}."
    assert default_spots_downloader.summits_errors == ['W1/W1-001'], f"Summit error should be 'W1/W1-001', got {default_spots_downloader.summits_errors}."
    assert 'W1/W1-001' not in default_spots_downloader.spots_to_visualisation['summit_ref'].values, "Summit reference W1/W1-001 has been not removed from spots_to_visualisation in check_error_references."
    assert len(default_spots_downloader.spots_to_visualisation) == 5, f"Spots to visualisation DataFrame should have 6 rows after removing errors, got {len(default_spots_downloader.spots_to_visualisation)}."

@pytest.mark.skip(reason="test_shell")
def test_join_spots_with_summits(default_spots_downloader: SpotsDownloader,
                                 mock_sota_spots_list: list[dict],
                                 mock_summits_list: list[dict]) -> None:
    """Tests join_spots_with_summits. Tested on default instance only as the method do not depend on initialisation parameters."""
    
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    
    default_spots_downloader.amend_spots_datatypes()
    default_spots_downloader.add_summit_codes()
    default_spots_downloader.prepare_spots_to_join()

    default_spots_downloader.SOTA_summits_data = pd.DataFrame(mock_summits_list)

    default_spots_downloader.check_error_references()
    initial_spots_to_visualisation = default_spots_downloader.spots_to_visualisation.copy()

    default_spots_downloader.join_spots_with_summits()
    
    assert len(default_spots_downloader.spots_to_visualisation) == len(initial_spots_to_visualisation), f"Merging spots and summits DataFrames changed number of spots to visualisation by {len(default_spots_downloader.spots_to_visualisation) - len(initial_spots_to_visualisation)} rows."
    for column_name in ['Longitude', 'Latitude', 'Points', 'SummitName']:
        assert column_name not in default_spots_downloader.spots_to_visualisation.columns, f"Column {column_name} is still present in spots_to_visualisation DataFrame, while it should be renamed."
    for column_name in ['longitude', 'latitude', 'points', 'summitName']:
        assert column_name in default_spots_downloader.spots_to_visualisation.columns, f"Column {column_name} is missing from spots_to_visualisation DataFrame, while it should be present."
    
    for summit_reference in default_spots_downloader.spots_to_visualisation['summit_ref'].unique():
        assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, 'summit_ref'].item() == summit_reference, f"Summit reference {summit_reference} does not match after merging spots with summits list."    

        for column_name in default_spots_downloader.spots_to_visualisation:
            # columns originating from spots_to_visualisation
            if column_name in initial_spots_to_visualisation.columns:
                print(column_name)
                assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, column_name].item() == initial_spots_to_visualisation.loc[initial_spots_to_visualisation['summit_ref'] == summit_reference, column_name].item(), f"{column_name} for {summit_reference} does not match after merging spots with summits list."
            # columns originating from SOTA_summits_data with changed name
            elif column_name in ['summitName', 'latitude', 'longitude', 'points']:
                print(column_name)
                assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, column_name].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, column_name[0].capitalize()+column_name[1:]].item(), f"{column_name} for {summit_reference} does not match after merging spots with summits list."
            # columns originating from SOTA_summits_data without name change
            else:
                print(column_name)
                assert default_spots_downloader.spots_to_visualisation.loc[default_spots_downloader.spots_to_visualisation['summit_ref'] == summit_reference, column_name].item() == default_spots_downloader.SOTA_summits_data.loc[default_spots_downloader.SOTA_summits_data['SummitCode'] == summit_reference, column_name].item(), f"{column_name} for {summit_reference} does not match after merging spots with summits list."

@pytest.mark.skip(reason="test_shell")
def test_add_time_markers(default_spots_downloader: SpotsDownloader,
                          mock_sota_spots_list: list[dict],
                          mock_summits_list: list[dict]) -> None:
    """Test add_time_markers. Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    default_spots_downloader.SOTA_summits_data = pd.DataFrame(mock_summits_list)

    default_spots_downloader.amend_spots_frequencies()
    default_spots_downloader.amend_spots_datatypes()
    default_spots_downloader.add_summit_codes()
    default_spots_downloader.prepare_spots_to_join()
    default_spots_downloader.check_error_references()
    default_spots_downloader.join_spots_with_summits()

    assert 'time_since_spot' not in default_spots_downloader.spots_to_visualisation.columns, "Column 'time_since_spot' found in spots_to_visualisation DataFrame before adding time markers."
    
    default_spots_downloader.add_time_markers()
    
    assert 'time_since_spot' in default_spots_downloader.spots_to_visualisation.columns, "Column 'time_since_spot' not found in spots_to_visualisation DataFrame after adding time markers."
    assert default_spots_downloader.spots_to_visualisation['time_since_spot'].dtype == 'float64', f"Column 'time_since_spot' is not of type float64, but {default_spots_downloader.spots_to_visualisation['time_since_spot'].dtype}."
    assert default_spots_downloader.spots_to_visualisation['time_since_spot'].notnull().all(), "Column 'time_since_spot' contains null values."
    assert default_spots_downloader.spots_to_visualisation['time_since_spot'].max() <= 0, "Column 'time_since_spot' contains positive values, only negative ones are expected."
    assert default_spots_downloader.spots_to_visualisation['time_since_spot'].min() >= -1, f"Value {default_spots_downloader.spots_to_visualisation['time_since_spot'].min()} found in 'time_since_spot' column, where expected range is [-1, 0]."
    assert abs(default_spots_downloader.spots_to_visualisation['time_since_spot'].min() + 0.9999) < 1e-4, f"Column 'time_since_spot' min value differs from expected 0.9999 by more than 1e-4."
    assert abs(default_spots_downloader.spots_to_visualisation['time_since_spot'].max() + 0.8333) < 1e-4, f"Column 'time_since_spot' max value differs from expected 0.8333 by more than 1e-4 ."

@pytest.mark.skip(reason="test_shell")
def test_create_visualisation_data(default_spots_downloader: SpotsDownloader,
                                   mock_sota_spots_list: list[dict],
                                   mock_summits_list: list[dict]) -> None:
    """Test create_visualisation_data. Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    default_spots_downloader.SOTA_summits_data = pd.DataFrame(mock_summits_list)

    default_spots_downloader.amend_spots_frequencies()
    default_spots_downloader.amend_spots_datatypes()
    default_spots_downloader.add_summit_codes()
    default_spots_downloader.prepare_spots_to_join()
    default_spots_downloader.check_error_references()
    default_spots_downloader.join_spots_with_summits()
    default_spots_downloader.add_time_markers()
    default_spots_downloader.create_visualisation_data()

    expected_values = {'band': ['14 MHz', '144 MHz', '7 MHz', '7 MHz', '21 MHz',],
                       'band_color': ['orange', 'blue', 'red', 'red', 'yellow',],
                       'mode_color': ['red', 'yellow', 'red', 'blue', 'red',],
                       }

    for column_name in ['popup', 'band_color', 'band', 'mode_color']:
        assert column_name in default_spots_downloader.spots_to_visualisation.columns, f"Column {column_name} not found in spots_to_visualisation DataFrame after create_visualisation_data."
        assert default_spots_downloader.spots_to_visualisation[column_name].notnull().all(), f"Column '{column_name}' contains null values."
        if column_name != 'popup':
            assert default_spots_downloader.spots_to_visualisation[column_name].tolist() == expected_values[column_name], f"Column '{column_name}' does not contain expected values after create_visualisation_data."

    for spot_row in default_spots_downloader.spots_to_visualisation.index:
        spot = default_spots_downloader.spots_to_visualisation.loc[spot_row]

        assert normalize_text(spot['popup']) == normalize_text(f"Summit {spot['summitName'].title()} - {spot['summit_ref']} "
                                                               f"{spot['points']} points\n"
                                                               f"activated by {spot['activatorCallsign'].upper()}\n"
                                                               f"on {spot['frequency']} - {spot['mode'].upper()}\n"
                                                               f"{round(spot['time_since_spot']*60)} minutes ago\n."
                                                               ), f"Popup text for spot row {spot_row} does not match expected format after create_visualisation_data."
@pytest.mark.skip(reason="test_shell")
def test_remove_unused_columns(default_spots_downloader: SpotsDownloader,
                                   mock_sota_spots_list: list[dict],
                                   mock_summits_list: list[dict]) -> None:
    """Test remove_unused_columns. Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = pd.DataFrame(mock_sota_spots_list)
    default_spots_downloader.SOTA_summits_data = pd.DataFrame(mock_summits_list)

    default_spots_downloader.amend_spots_frequencies()
    default_spots_downloader.amend_spots_datatypes()
    default_spots_downloader.add_summit_codes()
    default_spots_downloader.prepare_spots_to_join()
    default_spots_downloader.check_error_references()
    default_spots_downloader.join_spots_with_summits()
    default_spots_downloader.add_time_markers()
    default_spots_downloader.create_visualisation_data()
    default_spots_downloader.remove_unused_columns()

    expected_columns = ['timeStamp', 'comments', 'callsign', 'associationCode',
                        'summitCode', 'activatorCallsign', 'activatorName', 'frequency', 'mode',
                        'summitDetails', 'summit_ref', 'SummitCode',
                        'AssociationName', 'RegionName', 'summitName', 'longitude', 'latitude', 'points',
                        'BonusPoints', 'ActivationDate', 'ActivationCall', 'time_since_spot', 'popup',
                        'band_color', 'band', 'mode_color'
                        ]
    
    for column in default_spots_downloader.spots_to_visualisation.columns:
        assert column in expected_columns, f"Column {column} not expected in spots_to_visualisation DataFrame after create_visualisation_data."

@pytest.mark.skip(reason="test_shell")
def test_drop_summits_not_found(default_spots_downloader: SpotsDownloader,
                                mock_visualisation_data_cleared_with_no_reference: pd.DataFrame) -> None:
    """Test drop_summits_not_found. Tested on default instance only as the method do not depend on initialisation parameters."""
    default_spots_downloader.spots_to_visualisation = mock_visualisation_data_cleared_with_no_reference
    default_spots_downloader.drop_summits_not_found()

    assert len(default_spots_downloader.spots_to_visualisation) == 2, f"DataFrame should have 2 rows after dropping summits not found, got {len(default_spots_downloader.spots_to_visualisation)}."
    assert list(default_spots_downloader.spots_to_visualisation.index) == [0, 1], f"DataFrame index should be [0, 1] after dropping summits not found, got {default_spots_downloader.spots_to_visualisation.index}."
    assert 'W8W/CW-076' not in default_spots_downloader.spots_to_visualisation['summit_ref'].values, "Summit reference 'W8W/CW-076' should be removed from spots_to_visualisation DataFrame after dropping summits not found."
    assert default_spots_downloader.spots_to_visualisation['summit_ref'].tolist() == ['W7O/CS-098', 'JA/GM-107'], "Remaining summit references do not match expected values after dropping summits not found."
