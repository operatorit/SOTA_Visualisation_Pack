import requests # for communication with API
import pandas as pd # for data analysis
from datetime import datetime, timedelta # for time calculations
from dash import html, dcc, Dash, Input, Output # for dashboard construction
import dash_leaflet as dl # to visualise map

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
        """Defines contaants (related to SOTA API used and HAM radio characteristics)
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
        self.spots_to_visualisation['time_since_spot'] = self.spots_to_visualisation['time_since_spot']/timedelta(hours = 1)  
    
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
    spots_map.add_time_markers()
    spots_map.add_visualisation_markers()
    spots_map.remove_unused_columns()
    


### NEW above
### OLD below

# # save errors to file
# if len(summits_errors) != 0:
#     with open('summits_errors.txt', 'a') as f:
#         for error in summits_errors:
#             f.write(f'{error}\n')
# create spots_df_filtered dataframe as a copy of spots_df to be used later on in callbacks
# spots_df_filtered = spots_df.copy()


# def get_activation_data(spots):
#     """Prepare CircleMarkers list for spots visualisation, return a table of CircleMarkers"""
#     markers = []
#     for i in range(0, len(spots)):
#         if spots.loc[i, ('longitude')] != None: # ignore spots where no reference data in SOTA database was found
#             markers.append(
#             dl.CircleMarker(
#                 center=[spots.loc[i, ('latitude')], spots.loc[i, ('longitude')]],  # spot's location
#                 radius=(1 - spots.loc[i, ('time_since_spot')]) * 30,  # radius is proportional to time from sending
#                 # the spot. The newest spot, the larger circle. Spots with time above 1 hour will be presented as small points
#                 children = dl.Popup(spots.loc[i, ("popup")]), # pop-up with spot description
#                 fillColor=spots.loc[i, ('band_color')],  # circle's fill represents activation's band
#                 weight=3,
#                 color=spots.loc[i, ('mode_color')],  # border color represents activation's mode
#                 opacity=1,
#                 fillOpacity=1,
#             )
#             )
#         # skip incorrect summits
#         else:
#             pass
#     return markers

# def generate_maps(spots):
#     """Generate an input for dl.Map object"""
#     return [
#             dl.TileLayer(), # background layer
#             dl.LayerGroup(get_activation_data(spots)), # add layer with spots
#         ]

# # define Dash app layout
# sota_spots_dashboard.layout = html.Div([
#     html.Div(
#             dcc.Dropdown(
#                 modes_df['mode'], # values available
#                 modes_df['mode'], # values selected by default - all modes
#                 multi=True,
#                 placeholder='Select mode to apply filter or refresh page to show all',
#                 id = 'mode_selection' # dropdown list to select modes to visualise
#                 )),
#     html.Div(
#             dcc.Dropdown(
#                 bands_df.index, # valus available
#                 bands_df.index, # values selected by default - all bands
#                 multi=True,
#                 placeholder='Select band to apply filter or refresh page to show all',
#                 id = 'band_selection' #dropdown list to select bands to visualise
#                 )),
#     dl.Map(
#             children = generate_maps(spots_df), # generate map's layers
#             zoom=3, # whole world should be presented upon dashboard start
#             center=(50, 20), # map is centered near Kraków - city where I live
#             style={
#                 "height": "100vh", # map's height is 100% of the window
#             },
#             id = 'spots_map', # create a map with spots visualisation
#         )
# ])

# # add callbacks to dashboard to allow user to filter spots by band and mode
# @sota_spots_dashboard.callback(
#     Output('spots_map','children'),
#     Input('band_selection', 'value'),
#     Input('mode_selection', 'value')
#     )
# def update_map(bands, modes):
#     """Apply filters set-up by the user, return re-created map object"""
#     global spots_df
#     # operations are done on spots_df.filtered to make sure original DataFrame is kept safe
#     # dropdowns return lists with selected bands/modes, so need to check if spot's parameters are within these lists
#     spots_df_filtered = spots_df[spots_df['band'].isin(bands)].copy()
#     spots_df_filtered = spots_df_filtered[spots_df_filtered['mode'].isin(modes)]
#     # reset index to be list starting from 0
#     spots_df_filtered = spots_df_filtered.reset_index(drop = True)
#     return generate_maps(spots_df_filtered)


# # deploy the dashboard
# if __name__ == '__main__':
#     sota_spots_dashboard.run(port=8050, debug=True)
