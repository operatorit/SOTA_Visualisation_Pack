import requests # for communication with API
import pandas as pd # for data analysis
import folium # for data visualisation on a map
from datetime import datetime, timedelta # for time calculations

def get_spots(time = -1):
      """Downdload spots aleted in defined timeframe or defined number of latests spots"""
      # if time is negative - download spots alerted in defined number of alerts
      # if time is positive - download given number of latest spots
      # /api/.../all - if ... is positive - number of spots, if negative - number of hours
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


# create dataframes to store bands and modes data and map to colors for visualisation
# lower and upper freqs does not refer to bandplan to make sure frequencies are mapped correctly during visualisation
bands = {
    'band': ['1.8 MHz or below', '3.5 MHz', '5 MHz', '7 MHz', '10 MHz', '14 MHz', '18 MHz', '21 MHz', '24 MHz', '28 MHz', '50 MHz', '70 MHz', '144 MHz', '220 MHz', '433 MHz', '900 MHz or above'],
    'lower_freq': [0, 3, 4.5, 6, 9, 13, 16, 19, 24, 27, 45, 65, 142, 210, 420, 850],
    'upper_freq': [2.5, 4, 5.5, 8, 11, 15, 18.5, 23, 26, 35, 55, 75, 148, 240, 460, 500000],
    'color': ['saddlebrown','chocolate', 'brown','red', 'salmon', 'orange', 'gold', 'yellow', 'olivedrab', 'green', 'lime', 'cyan', 'blue', 'purple', 'magenta', 'pink'],
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
spots_dict = get_spots()
spots_df = pd.DataFrame(spots_dict)

# convert datatypes for relevant fields
spots_df['activatorCallsign'] = spots_df['activatorCallsign'].astype('string')
spots_df['associationCode'] = spots_df['associationCode'].astype('string')
spots_df['summitCode'] = spots_df['summitCode'].astype('string')
spots_df['mode'] = spots_df['mode'].astype('string')
spots_df['frequency'] = spots_df['frequency'].astype('float')
spots_df['timeStamp'] = pd.to_datetime(spots_df['timeStamp'])

# create DataFrame based on csv file with all the summits saved (regularly updated
# from https://www.sotadata.org.uk/summitslist.csv, and converting the datatypes
# first row of CSV file is a header, so should be ignored
# create DataFrame based on csv file with all the summits saved
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

# add summit codes to spots_df DataFrame
spots_df['summit'] = spots_df['associationCode']+'/'+spots_df['summitCode']

# drop duplicated activator-summit pairs from spots_df to avoid double visualisation for them
# only last spot sent by activator on a summit is considered
# create empty columns for data required for visualisation (will b filled with database data)
# then re-index this dataframe
spots_df = spots_df.drop_duplicates(subset = ['activatorCallsign', 'summit'])
spots_df['longitude'] = None
spots_df['latitude'] = None
spots_df['points'] = None
spots_df['summitName'] = None
spots_df['mode_color'] = None
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
# create a map
activations_map = folium.Map(location=[50, 20],  # map is centered on Kraków - city where I live
                             tiles="Stamen Terrain",
                             zoom_start=2  # show whole world at once
                             )

# add spots to a map
for i in range(0, len(spots_df)):  # add point for every spot (with duplicates removed)
    if spots_df.loc[i, ('longitude')] != None:  # ignore spots where no reference data in SOTA database was found
        folium.CircleMarker(
            location=[spots_df.loc[i, ('latitude')], spots_df.loc[i, ('longitude')]],  # spot's location
            radius=(1 - spots_df.loc[i, ('time_since_spot')]) * 15,  # radius is proportional to time from sending
            # the spot. The newest spot, the larger circle
            popup=spots_df.loc[i, ("popup")],
            fill_color=spots_df.loc[i, ('band_color')],  # circle's fill represents activation's band
            weight=3,
            color=spots_df.loc[i, ('mode_color')],  # border color represents activation's mode
            fill_opacity=1
        ).add_to(activations_map)

# save map in a file
activations_map.save('activations_map.html')
