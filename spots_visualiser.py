import requests # for communication with API
import pandas as pd # for data analysis
from datetime import datetime, timedelta # for time calculations
from dash import html, dcc, Dash, Input, Output # for dashboard construction
import dash_leaflet as dl # to visualise map

class SpotsVisualiser:
    
    def __init__(self, 
                 lookback_time:int = -1, 
                 summits_filename:str = 'summitslist.csv'):
        """Initiates a class.
        lookback_time - time in hours to look back for spots.
        If lookback_time is negative - download spots alerted in defined number of hours.
        If lookback_time is positive - download given number of latest spots.
        Default value is -1, which means spots from last hour are downloaded.

        summits_filename - name of the file with summits data, saved in project's folder.
        """
        self.lookback_time = lookback_time
        self.summits_filename = summits_filename
        self.summits_errors = []

        self.define_constants()

    def define_constants(self) -> None:
        """Defines contaants (related to SOTA API used and HAM radio characteristics)
        required for the class to work.
        Bands are groupped into ranges to fit bandplands for different countries.
        """
        self._API_URL = f'https://api2.sota.org.uk/api/spots/{self.lookback_time}/all'

        self._BANDS = pd.DataFrame({'band': ['1.8 MHz or below', '3.5 MHz', '5 MHz', '7 MHz', '10 MHz', '14 MHz', '18 MHz', '21 MHz', '24 MHz', '28 MHz', '50 MHz', '70 MHz', '144 MHz', '220 MHz', '433 MHz', '900 MHz or above'],
                      'lower_freq': [0, 3, 4.5, 6, 9, 13, 16, 19, 24, 27, 45, 65, 142, 210, 420, 850],
                      'upper_freq': [2.5, 4, 5.5, 8, 11, 15, 18.5, 23, 26, 35, 55, 75, 148, 240, 460, 500000],
                      'color': ['saddlebrown','chocolate', 'brown','red', 'salmon', 'orange', 'gold', 'yellow', 'olivedrab', 'green', 'lime', 'cyan', 'blue', 'purple', 'magenta', 'pink'],
                      })

        self._BANDS.set_index('band', drop = True, inplace = True)
        self._BANDS['color'] = self._BANDS['color'].astype('string')

        self._MODES = pd.DataFrame({'mode': ['AM', 'CW', 'Data', 'DV', 'FM', 'SSB', 'Other'],
                                 'color': ['lime', 'red', 'cyan', 'magenta', 'yellow', 'blue', 'orange']
                                 })
        self._MODES['color'] = self._MODES['color'].astype('string')
        self._MODES['mode'] = self._MODES['mode'].astype('string')

    def get_spots(self) -> None:
      """Downloads spots aleted in defined timeframe or defined number of latests spots.
      If there are no spots sent in time provided, return latest 10 to make sure dictionary is not empty.
      """
      temp_spots_dict = {}
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
          
      self.spots_to_visualisation = pd.DataFrame(temp_spots_dict)
    
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
                                                    inplace = True)
        # self.spots_to_visualisation['longitude'] = None
        # self.spots_to_visualisation['latitude'] = None
        # self.spots_to_visualisation['points'] = None
        # self.spots_to_visualisation['summitName'] = None
        # self.spots_to_visualisation['mode_color'] = None
        # self.spots_to_visualisation['band_color'] = None
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
                                                    #    12: not relevant
                                                    #    13: not relevant
                                                        14: 'int',
                                                    #    15: not relevant
                                                        16: 'string'
                                                    },
                                                    # index_col = 'SummitCode'
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
        print(self.spots_to_visualisation.columns)

    def add_time_markers(self)  -> None:
        """Adds information regarding time since spot to spots_to_visualisation DataFrame.
        """
        self.spots_to_visualisation['time_since_spot'] = datetime.utcnow() - self.spots_to_visualisation['timeStamp']
        self.spots_to_visualisation['time_since_spot'] = self.spots_to_visualisation['time_since_spot']/timedelta(hours=1)
#        
    
    def add_visualisation_markers(self) -> None:
        """Adds information regarding visualisation markers to spots_to_visualisation DataFrame.
        """
        pass
        #  spots_df.loc[i, ('popup')] = f"Summit {spots_df.loc[i, ('summitName')].title()} - {spots_df.loc[i, ('summit')]} ({spots_df.loc[i, ('points')]} points)\nactivated by {spots_df.loc[i, ('activatorCallsign')].upper()}\non {spots_df.loc[i, ('frequency')]} - {spots_df.loc[i, ('mode')].upper()}\n{round(spots_df.loc[i, ('time_since_spot')]*60)} minutes ago\n."
#         spots_df.loc[i, ('mode')] = spots_df.loc[i, ('mode')].upper()
#         for band in bands_df.index: # assess band based on frequency spotted
#             if (spots_df.loc[i, ('frequency')] >= bands_df['lower_freq'][band]) and (spots_df.loc[i, ('frequency')] <= bands_df['upper_freq'][band]):
#                 spots_df.loc[i, ('band_color')] = bands_df['color'][band]
#                 spots_df.loc[i, ('band')] = band
#         for j in modes_df.index:
#             if spots_df.loc[i, ('mode')] == modes_df.iloc[j]['mode'].upper():
#                 spots_df.loc[i,('mode_color')] = modes_df.iloc[j]['color']

    def remove_unused_columns(self) -> None:
        """Removes columns not used for visualisation from spots_to_visualisation DataFrame.
        """
        pass
        # self.spots_to_visualisation.drop(columns = [], inplace = True)


# script flow
if __name__ == "__main__":
    spots_map = SpotsVisualiser(lookback_time = -1)

    spots_map.get_spots()
    spots_map.amend_spots_frequencies()
    spots_map.amend_spots_datatypes()
    spots_map.add_summit_codes()
    spots_map.prepare_spots_to_join()

    spots_map.get_summits_list()
    spots_map.check_error_references()
    spots_map.join_spots_with_summits()
    


### NEW above
### OLD below



# # copying relevant data for visualisation from SOTA database extract to spots dataframe
# # also adding time since spot in hour fraction and description of spot
# # adding previously defined colorcodes for band and mode to each spot, together with a band for each one
# # popup column provides a summary of activation to be displayed on map
# for i in range(0, len(spots_df)):
#     # if summits data are correct,prepare spot's data for visualisation
#     if spots_df.loc[i, ('summit')].upper() in SOTA_summits_data.index:
#         spots_df.loc[i, ('time_since_spot')] = datetime.utcnow()-spots_df.loc[i, ('timeStamp')]
#         spots_df.loc[i, ('time_since_spot')] = spots_df.loc[i, ('time_since_spot')]/timedelta(hours=1)
#         spots_df.loc[i, ('popup')] = f"Summit {spots_df.loc[i, ('summitName')].title()} - {spots_df.loc[i, ('summit')]} ({spots_df.loc[i, ('points')]} points)\nactivated by {spots_df.loc[i, ('activatorCallsign')].upper()}\non {spots_df.loc[i, ('frequency')]} - {spots_df.loc[i, ('mode')].upper()}\n{round(spots_df.loc[i, ('time_since_spot')]*60)} minutes ago\n."
#         spots_df.loc[i, ('mode')] = spots_df.loc[i, ('mode')].upper()
#         for band in bands_df.index: # assess band based on frequency spotted
#             if (spots_df.loc[i, ('frequency')] >= bands_df['lower_freq'][band]) and (spots_df.loc[i, ('frequency')] <= bands_df['upper_freq'][band]):
#                 spots_df.loc[i, ('band_color')] = bands_df['color'][band]
#                 spots_df.loc[i, ('band')] = band
#         for j in modes_df.index:
#             if spots_df.loc[i, ('mode')] == modes_df.iloc[j]['mode'].upper():
#                 spots_df.loc[i,('mode_color')] = modes_df.iloc[j]['color']


# # save errors to file
# if len(summits_errors) != 0:
#     with open('summits_errors.txt', 'a') as f:
#         for error in summits_errors:
#             f.write(f'{error}\n')
# # create a map
# activations_map = folium.Map(location=[50, 20],  # map is centered on Kraków - city where I live
#                              tiles="OpenStreetMap",
#                              zoom_start=2  # show whole world at once
#                              )

# # add spots to a map
# for i in range(0, len(spots_df)):  # add point for every spot (with duplicates removed)
#     if spots_df.loc[i, ('longitude')] != None:  # ignore spots where no reference data in SOTA database was found
#         folium.CircleMarker(
#             location=[spots_df.loc[i, ('latitude')], spots_df.loc[i, ('longitude')]],  # spot's location
#             radius=(1 - spots_df.loc[i, ('time_since_spot')]) * 15,  # radius is proportional to time from sending
#             # the spot. The newest spot, the larger circle
#             popup=spots_df.loc[i, ("popup")],
#             fill_color=spots_df.loc[i, ('band_color')],  # circle's fill represents activation's band
#             weight=3,
#             color=spots_df.loc[i, ('mode_color')],  # border color represents activation's mode
#             fill_opacity=1
#         ).add_to(activations_map)

# # save map in a file
# activations_map.save('activations_map.html')
