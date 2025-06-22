import requests # for communication with API
import pandas as pd # for data analysis
import dash_leaflet as dl # to visualise map

from datetime import datetime, timedelta # for time calculations

import config # script configuration

class SpotsVisualiser:
    
    def __init__(self, 
                 lookback_time:int = -1, 
                 summits_filename:str = config._SUMMITS_FILENAME):
        """Initiates a class.
        lookback_time - time in hours to look back for spots.
        If lookback_time is negative - download spots alerted in defined number of hours.
        If lookback_time is positive - download given number of latest spots.
        Default value is -1, which means spots from last hour are downloaded.

        summits_filename - name of the file with summits data, saved in project's folder.
        """
        self.lookback_time = lookback_time
        self.summits_filename = summits_filename
        self.summits_errors:list = []

        self.define_constants()

    def define_constants(self) -> None:
        """Defines contants (related to SOTA API used and HAM radio characteristics)
        required for the class to work.
        Bands are groupped into ranges to fit bandplands for different countries.
        """
        self._API_URL = f'https://api2.sota.org.uk/api/spots/{self.lookback_time}/all' # explicitely address for other implementations, thus not via config file

        self._BANDS = pd.DataFrame({'band': ['1.8 MHz or below', '3.5 MHz', '5 MHz', '7 MHz', '10 MHz', '14 MHz', '18 MHz', '21 MHz', '24 MHz', '28 MHz', '50 MHz', '70 MHz', '144 MHz', '220 MHz', '433 MHz', '900 MHz or above'],
                      'lower_freq': [0, 3, 4.5, 6, 9, 13, 16, 19, 24, 27, 45, 65, 142, 210, 420, 850],
                      'upper_freq': [2.5, 4, 5.5, 8, 11, 15, 18.5, 23, 26, 35, 55, 75, 148, 240, 460, 500000], # upper limit is a placeholder for 900 MHz and above
                      'color': ['saddlebrown','chocolate', 'brown','red', 'salmon', 'orange', 'gold', 'yellow', 'olivedrab', 'green', 'lime', 'cyan', 'blue', 'purple', 'magenta', 'pink'],
                      })
        self._BANDS.set_index('band', drop = True, inplace = True)
        self._BANDS['color'] = self._BANDS['color'].astype('string')

        self._MODES = pd.DataFrame({'mode': ['AM', 'CW', 'Data', 'DV', 'FM', 'SSB', 'Other'],
                                 'color': ['lime', 'red', 'cyan', 'magenta', 'yellow', 'blue', 'orange']
                                 })
        self._MODES['color'] = self._MODES['color'].astype('string')
        self._MODES['mode'] = self._MODES['mode'].astype('string')
    
    def process_spots(self) -> pd.DataFrame:
        self.spots_to_visualisation = self.get_spots()
        self.amend_spots_frequencies()
        self.amend_spots_datatypes()
        self.add_summit_codes()
        self.prepare_spots_to_join()
        self.get_summits_list()
        self.check_error_references()
        self.join_spots_with_summits()
        self.add_time_markers()
        # print(self.spots_to_visualisation)
        self.create_visualisation_data()
        self.remove_unused_columns()
        self.drop_summits_not_found()

        return self.spots_to_visualisation


    def get_spots(self) -> pd.DataFrame:
        """Downloads spots aleted in defined timeframe or defined number of latests spots.
        If there are no spots sent in time provided, return latest 10 to make sure dictionary is not empty.
        """
        temp_spots_dict = {}
        try:
            r = requests.get(self._API_URL)
            print(f'Status code: {r.status_code}')
            temp_spots_dict = r.json()

            if self.lookback_time > 0:
                    print(f'{len(temp_spots_dict)} found where expected number was {self.lookback_time}.')
            if self.lookback_time < 0:
                    print(f'{len(temp_spots_dict)} spots found in latest {-self.lookback_time} h.')

            if len(temp_spots_dict) == 0:
                temp_spots_dict = self.get_spots(10)
                print(f"No spots found in the timeframe provided. Returning latest 10 spots.")
            
            return pd.DataFrame(temp_spots_dict)
        
        except requests.exceptions.RequestException as e:
            print(f"Error occurred, spots not downloaded.")
            return pd.DataFrame()  # return empty DataFrame if error occurs
    
    def amend_spots_frequencies(self) -> None:
        """Amend incorrect frequencies (defined as not matchng regular expression for
        digits-dot-digits) to 0 to avoid errors during visualisation.
        """
        self.spots_to_visualisation.loc[~self.spots_to_visualisation['frequency'].str.match(r'\d+(\.\d+)?'), 'frequency'] = 0

    def amend_spots_datatypes(self) -> None:
        """Convert datatypes for relevant fields.
        """
        self.spots_to_visualisation['activatorCallsign'] = self.spots_to_visualisation['activatorCallsign'].astype('string')
        self.spots_to_visualisation['associationCode'] = self.spots_to_visualisation['associationCode'].astype('string')
        self.spots_to_visualisation['summitCode'] = self.spots_to_visualisation['summitCode'].astype('string')
        self.spots_to_visualisation['mode'] = self.spots_to_visualisation['mode'].astype('string')
        self.spots_to_visualisation['frequency'] = self.spots_to_visualisation['frequency'].astype('float')
        self.spots_to_visualisation['timeStamp'] = pd.to_datetime(self.spots_to_visualisation['timeStamp'])

    def add_summit_codes(self) -> None:
        """Combines associationCode and summitCode to summit's reference in formmat country/range-summit_number.
        Eg. SP/BZ-001.
        """
        self.spots_to_visualisation['summit_ref'] = self.spots_to_visualisation['associationCode'] \
            + '/' \
            + self.spots_to_visualisation['summitCode']

    def prepare_spots_to_join(self) -> None:
        """ Drops duplicated activator-summit pairs from self.spots_to_visualisation to avoid 
        double visualisation for them. Only last spot sent by activator on a summit is considered.
        Creates empty columns for data required for visualisation (will be filled with database data).
        Finally, re-indexes dataframe with spots.
        """
        self.spots_to_visualisation.drop_duplicates(subset = ['activatorCallsign', 'summit_ref'],
                                                    inplace = True, keep = 'last')
        self.spots_to_visualisation.reset_index(drop = True, inplace = True)
        
    def get_summits_list(self) -> None:
        """Create DataFrame based on csv file with all the summits saved (regularly updated
        from https://www.sotadata.org.uk/summitslist.csv), and converting the datatypes
        first row of CSV file is a header, so should be ignored.
        """
        try:
            self.SOTA_summits_data = pd.read_csv(self.summits_filename, 
                                            skiprows = 1, 
                                            dtype = {0: 'string',
                                                        1: 'string',
                                                        2: 'string',
                                                        3: 'string',
                                                        4: 'int',
                                                        5: 'int',
                                                        6: 'string',
                                                        7: 'string',
                                                        8: 'float',
                                                        9: 'float',
                                                        10: 'int',
                                                        11: 'int',
                                                    #    12: '', # not relevant
                                                    #    13: '', # not relevant
                                                        14: 'int',
                                                    #    15: '', # not relevant
                                                        16: 'string'
                                                    },
                                            )
        except FileNotFoundError:
            print(f"File {self.summits_filename} not found. Make sure it's saved in project's directory.")

    def check_error_references(self) -> None:
        """Checks if all references in spots are on summits list.
        If not, adds non-found ones to a list and prints a warning.
        Such references stays on the spots list with data for visualisation filled with None,
        thus no impacting map.
        """
        for summit_reference in self.spots_to_visualisation['summit_ref']:
            if summit_reference.upper() not in self.SOTA_summits_data['SummitCode'].str.upper().values:
                print(f"Summit {summit_reference} NOT FOUND.")
                self.summits_errors.append(summit_reference)
                self.spots_to_visualisation.drop(self.spots_to_visualisation.loc[self.spots_to_visualisation['summit_ref'] == summit_reference].index, inplace = True)
                self.spots_to_visualisation.reset_index(drop = True, inplace = True)

    def join_spots_with_summits(self) -> None:
        """Join spots dataframe with summits dataframe to get all the data required for visualisation.
        """
        self.spots_to_visualisation = pd.merge(left = self.spots_to_visualisation,
                                               right = self.SOTA_summits_data, 
                                               left_on = 'summit_ref', 
                                               right_on = 'SummitCode',
                                               how = 'left',
                                               )
        self.spots_to_visualisation.rename(columns = {'Longitude': 'longitude',
                                                      'Latitude': 'latitude',
                                                      'Points': 'points',
                                                      'SummitName': 'summitName',
                                                      }, inplace = True)


    def add_time_markers(self)  -> None:
        """Adds information regarding time since spot to spots_to_visualisation DataFrame.
        """
        self.spots_to_visualisation['time_since_spot'] = datetime.utcnow() - self.spots_to_visualisation['timeStamp']
        self.spots_to_visualisation['time_since_spot'] = self.spots_to_visualisation['time_since_spot']/timedelta(hours = 1)  
    
    def create_visualisation_data(self) -> None:
        """Adds information regarding visualisation markers to spots_to_visualisation DataFrame.
        """
        self.spots_to_visualisation['popup'] = self.spots_to_visualisation.apply(lambda row: f"Summit {row['summitName'].title()} - {row['summit_ref']} \
                                                                                                {row['points']} points\n \
                                                                                                activated by {row['activatorCallsign'].upper()}\n\
                                                                                                on {row['frequency']} \
                                                                                                - {row['mode'].upper()}\n\
                                                                                                {round(row['time_since_spot']*60)} minutes ago\n.", axis=1)

        self.spots_to_visualisation['mode'] = self.spots_to_visualisation['mode'].str.upper()
        self.spots_to_visualisation['band_color'], self.spots_to_visualisation['band'], self.spots_to_visualisation['mode_color'] = pd.NA, pd.NA, pd.NA
        for band in self._BANDS.index: # assess band based on frequency spotted
            self.spots_to_visualisation.loc[(self._BANDS['upper_freq'][band] >= self.spots_to_visualisation['frequency']) \
                                                 & (self.spots_to_visualisation['frequency']>= self._BANDS['lower_freq'][band]), 
                                                 'band'] = band
            self.spots_to_visualisation.loc[(self._BANDS['upper_freq'][band] >= self.spots_to_visualisation['frequency']) \
                                                 & (self.spots_to_visualisation['frequency'] >= self._BANDS['lower_freq'][band]), 
                                                 'band_color'] = self._BANDS['color'][band]

        for mode in self._MODES['mode'].unique():
            self.spots_to_visualisation.loc[self.spots_to_visualisation['mode'] == mode, 'mode_color'] = self._MODES.loc[self._MODES['mode'] == mode, 'color'].item()

    def remove_unused_columns(self) -> None:
        """Removes columns not used for visualisation from spots_to_visualisation DataFrame.
        """
        #TODO: check which columns are nmecessary
        self.spots_to_visualisation = self.spots_to_visualisation[['timeStamp', 'comments', 'callsign', 'associationCode',
       'summitCode', 'activatorCallsign', 'activatorName', 'frequency', 'mode',
       'summitDetails', 'summit_ref', 'SummitCode',
       'AssociationName', 'RegionName', 'summitName', 'longitude', 'latitude', 'points',
       'BonusPoints',
       'ActivationDate', 'ActivationCall', 'time_since_spot', 'popup',
       'band_color', 'band', 'mode_color']]

    def drop_summits_not_found(self) -> None:
        """Removes spots with references not found in SOTA summits list.
        """
        self.spots_to_visualisation.drop(self.spots_to_visualisation[self.spots_to_visualisation['longitude'].isna()].index, inplace = True)
        self.spots_to_visualisation.reset_index(drop = True, inplace = True)