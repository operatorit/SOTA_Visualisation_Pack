import requests # for communication with API
import pandas as pd # for data analysis
from datetime import datetime, timedelta # for time calculations
from dash import html, dcc, Dash, Input, Output # for dashboard construction
import dash_leaflet as dl # to visualise map

def get_spots(time = -1):
      """Downdload SOTA spots sent in defined timeframe or defined number of latests spots and returns them as dictionary"""
      # if time is negative - download spots alerted in defined number of alerts
      # if time is positive - download given number of latest spots
      # by default looking from a spots sent in last 1 hour
      temp_spots_dict = {}
      url = f'https://api2.sota.org.uk/api/spots/{time}/all'
      r = requests.get(url)
      print(f'Status code: {r.status_code}')
      temp_spots_dict = r.json()
      if time > 0:
            print(f'{len(temp_spots_dict)} found where expected number was {time}.')
      if time <= 0:
            print(f'{len(temp_spots_dict)} spots found in latest {-time} h.')
      # if there are no spots sent in time provided, return latest 10 to make sure dictionary is not empty
      if len(temp_spots_dict) == 0:
          temp_spots_dict = get_spots(10)
      return temp_spots_dict

# deploy sota_spots_dashboard app in Dash
sota_spots_dashboard = Dash(__name__)

# create dataframes to store bands and modes data and map to colors for visualisation
# lower and upper freqs does not refer exactly to bandplan to make sure frequencies are mapped correctly during visualisation
bands = {
    'band': ['1.8 MHz or below', '3.5 MHz', '5 MHz', '7 MHz', '10 MHz', '14 MHz', '18 MHz', '21 MHz', '24 MHz', '28 MHz', '50 MHz', '70 MHz', '144 MHz', '220 MHz', '433 MHz', '900 MHz or above'],
    'lower_freq': [0, 3, 4.5, 6, 9, 13, 16, 19, 24, 27, 45, 65, 142, 210, 420, 850],
    'upper_freq': [2.5, 4, 5.5, 8, 11, 15, 18.5, 23, 26, 35, 55, 75, 148, 240, 460, 500000],
    'color': ['saddlebrown','chocolate', 'brown','red', 'salmon', 'orange', 'darkkhaki', 'yellow', 'olivedrab', 'green', 'lime', 'cyan', 'blue', 'purple', 'magenta', 'pink'],
}
bands_df = pd.DataFrame(bands)

bands_df = bands_df.set_index('band')
bands_df['color'] = bands_df['color'].astype('string')

modes = {
    'mode': ['AM', 'CW', 'Data', 'DV', 'FM', 'SSB', 'Other'],
    'color': ['lime', 'red', 'cyan', 'magenta', 'yellow', 'blue', 'orange']
}

modes_df = pd.DataFrame(modes)
modes_df['color'] = modes_df['color'].astype('string')
modes_df['mode'] = modes_df['mode'].astype('string')

# create dictionary to keep the spots a list for summits
spots_dict = {}

# import spots and convert them into DataFrame
spots_dict = get_spots(-1)

spots_df = pd.DataFrame(spots_dict)

# replace frequency where it's provided in incorrect format with 0
spots_df.loc[~spots_df['frequency'].str.match(r'\d+(\.\d+)?'), 'frequency'] = 0

# convert datatypes for relevant fields
spots_df['activatorCallsign'] = spots_df['activatorCallsign'].astype('string')
spots_df['associationCode'] = spots_df['associationCode'].astype('string')
spots_df['summitCode'] = spots_df['summitCode'].astype('string')
spots_df['mode'] = spots_df['mode'].astype('string')
spots_df['frequency'] =  spots_df['frequency'].astype('float')
spots_df['timeStamp'] = pd.to_datetime(spots_df['timeStamp'])

# create DataFrame based on csv file with all the summits saved (regularly updated
# from https://www.sotadata.org.uk/summitslist.csv, and converting the datatypes
# first row of CSV file is a header, so should be ignored
SOTA_summits_df = pd.read_csv('summitslist.csv', skiprows = 1, dtype = {
    0: 'string',
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
}
)

SOTA_summits_df = SOTA_summits_df.set_index('SummitCode')

# add full summit codes column to spots_df DataFrame
spots_df['summit'] = spots_df['associationCode']+'/'+spots_df['summitCode']

# drop duplicated activator-summit pairs from spots_df to avoid double visualisation for them
# only last spot sent by activator on a summit is considered
# create empty columns for data required for visualisation (will b filled with database data)
# then re-index this dataframe
spots_df = spots_df.drop_duplicates(subset = ['activatorCallsign', 'summit'])
print(f'{len(spots_df)} found without duplicates.')
spots_df['longitude'] = None
spots_df['latitude'] = None
spots_df['points'] = None
spots_df['summitName'] = None
spots_df['mode_color'] = None
spots_df['band'] = None
spots_df['band_color'] = None
spots_df = spots_df.reset_index(drop = True)

# list to keep summit codes not found in SOTA Database file
# List of summits is periodically updated, but typos in summits codes in spots are also common
summits_errors = []

# copying relevant data for visualisation from SOTA database extract to spots dataframe
# also adding time since spot in hour fraction and description of spot
# adding previously defined colorcodes for band and mode to each spot, together with a band for each one
# popup column provides a summary of activation to be displayed on map
for i in range(0, len(spots_df)):
    # if summits data are correct,prepare spot's data for visualisation
    if spots_df.loc[i, ('summit')].upper() in SOTA_summits_df.index:
        spots_df.loc[i, ('longitude')] = SOTA_summits_df['Longitude'][spots_df.loc[i, 'summit']]
        spots_df.loc[i, ('latitude')] = SOTA_summits_df['Latitude'][spots_df.loc[i, 'summit']]
        spots_df.loc[i, ('points')] = SOTA_summits_df['Points'][spots_df.loc[i, 'summit']]
        spots_df.loc[i, ('summitName')] = SOTA_summits_df['SummitName'][spots_df.loc[i, 'summit']]
        spots_df.loc[i, ('time_since_spot')] = datetime.utcnow()-spots_df.loc[i, ('timeStamp')]
        spots_df.loc[i, ('time_since_spot')] = spots_df.loc[i, ('time_since_spot')]/timedelta(hours=1)
        spots_df.loc[i, ('popup')] = f"Summit {spots_df.loc[i, ('summitName')].title()} - {spots_df.loc[i, ('summit')]} ({spots_df.loc[i, ('points')]} points)\nactivated by {spots_df.loc[i, ('activatorCallsign')].upper()}\non {spots_df.loc[i, ('frequency')]} - {spots_df.loc[i, ('mode')].upper()}\n{round(spots_df.loc[i, ('time_since_spot')]*60)} minutes ago\n."
        spots_df.loc[i, ('mode')] = spots_df.loc[i, ('mode')].upper()
        for band in bands_df.index: # assess band based on frequency spotted
            if (spots_df.loc[i, ('frequency')] >= bands_df['lower_freq'][band]) and (spots_df.loc[i, ('frequency')] <= bands_df['upper_freq'][band]):
                spots_df.loc[i, ('band_color')] = bands_df['color'][band]
                spots_df.loc[i, ('band')] = band
        for j in modes_df.index:
            if spots_df.loc[i, ('mode')] == modes_df.iloc[j]['mode'].upper():
                spots_df.loc[i,('mode_color')] = modes_df.iloc[j]['color']
    # if summit isn't found in database, print warning, save it on a list and leave their data with None
    else:
        print(f"Summit {spots_df.loc[i, ('summit')]} activated by {spots_df.loc[i, ('activatorCallsign')].upper()} on {spots_df.loc[i, ('frequency')]} - {spots_df.loc[i, ('mode')].upper()}  NOT FOUND.")
        summits_errors.append({spots_df.loc[i, ('summit')]})

# save errors to file
if len(summits_errors) != 0:
    with open('summits_errors.txt', 'a') as f:
        for error in summits_errors:
            f.write(f'{error}\n')

# create spots_df_filtered dataframe as a copy of spots_df to be used later on in callbacks
spots_df_filtered = spots_df.copy()


def get_activation_data(spots):
    """Prepare CircleMarkers list for spots visualisation, return a table of CircleMarkers"""
    markers = []
    for i in range(0, len(spots)):
        if spots.loc[i, ('longitude')] != None: # ignore spots where no reference data in SOTA database was found
            markers.append(
            dl.CircleMarker(
                center=[spots.loc[i, ('latitude')], spots.loc[i, ('longitude')]],  # spot's location
                radius=(1 - spots.loc[i, ('time_since_spot')]) * 30,  # radius is proportional to time from sending
                # the spot. The newest spot, the larger circle. Spots with time above 1 hour will be presented as small points
                children = dl.Popup(spots.loc[i, ("popup")]), # pop-up with spot description
                fillColor=spots.loc[i, ('band_color')],  # circle's fill represents activation's band
                weight=3,
                color=spots.loc[i, ('mode_color')],  # border color represents activation's mode
                opacity=1,
                fillOpacity=1,
            )
            )
        # skip incorrect summits
        else:
            pass
    return markers

def generate_maps(spots):
    """Generate an input for dl.Map object"""
    return [
            dl.TileLayer(), # background layer
            dl.LayerGroup(get_activation_data(spots)), # add layer with spots
        ]

# define Dash app layout
sota_spots_dashboard.layout = html.Div([
    html.Div(
            dcc.Dropdown(
                modes_df['mode'], # values available
                modes_df['mode'], # values selected by default - all modes
                multi=True,
                placeholder='Select mode to apply filter or refresh page to show all',
                id = 'mode_selection' # dropdown list to select modes to visualise
                )),
    html.Div(
            dcc.Dropdown(
                bands_df.index, # valus available
                bands_df.index, # values selected by default - all bands
                multi=True,
                placeholder='Select band to apply filter or refresh page to show all',
                id = 'band_selection' #dropdown list to select bands to visualise
                )),
    dl.Map(
            children = generate_maps(spots_df), # generate map's layers
            zoom=3, # whole world should be presented upon dashboard start
            center=(50, 20), # map is centered near Kraków - city where I live
            style={
                "height": "100vh", # map's height is 100% of the window
            },
            id = 'spots_map', # create a map with spots visualisation
        )
])

# add callbacks to dashboard to allow user to filter spots by band and mode
@sota_spots_dashboard.callback(
    Output('spots_map','children'),
    Input('band_selection', 'value'),
    Input('mode_selection', 'value')
    )
def update_map(bands, modes):
    """Apply filters set-up by the user, return re-created map object"""
    global spots_df
    # operations are done on spots_df.filtered to make sure original DataFrame is kept safe
    # dropdowns return lists with selected bands/modes, so need to check if spot's parameters are within these lists
    spots_df_filtered = spots_df[spots_df['band'].isin(bands)].copy()
    spots_df_filtered = spots_df_filtered[spots_df_filtered['mode'].isin(modes)]
    # reset index to be list starting from 0
    spots_df_filtered = spots_df_filtered.reset_index(drop = True)
    return generate_maps(spots_df_filtered)


# deploy the dashboard
if __name__ == '__main__':
    sota_spots_dashboard.run_server(port=8050, debug=True)