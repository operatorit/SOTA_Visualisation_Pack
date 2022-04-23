import adif_io as adif # to read the log
import pandas as pd # to analyse log as a DataFrame
import requests # to get data from SOTA API
from unidecode import unidecode # for log clearing
import folium # for data visualisation on a map
import maidenhead as mh # to calculate coordinates from GRID square
import branca.colormap as cm # to add colormap to the visualisation

# save name of your log under filename variable
filename = 'SOTAlog.adi'
working_log = 'working_log.adi'

# clear the log out of local charts (accents) by changing them into the closes latin one
# log file is opened, modified and then saved under the name specified in working_log variable
with open(filename, 'r', encoding='ansi') as filelog:
    content = unidecode(filelog.read())
filelog.close()
with open(working_log, 'w') as filelog:
    filelog.write(content)
filelog.close()

# load log into the variable log_raw, log_header stores header of ADIF file
log_raw,log_header = adif.read_from_file(working_log)

# convert the log into DataFrame df_log_raw
df_log_raw = pd.DataFrame(log_raw)

# check if there are any SOTA chases in log
if df_log_raw['SOTA_REF'].count() == 0:
    print('No SOTA chases found in log.')
    exit()
else:
    df_log_raw['SOTA_REF'] = df_log_raw['SOTA_REF'].str.upper()

# data filtering - move to further analysis only entries with SOTA reference provided in SOTA_REF column
df_log_SOTA = df_log_raw[df_log_raw.SOTA_REF.notnull()]

# check which SOTA summits are present in the log and remove duplicates
df_log_summits = df_log_SOTA['SOTA_REF'].copy().drop_duplicates().reset_index()
del(df_log_summits['index'])

# import relevant summits data from SOTA API and save them as DataFrame

summits_dict = {}
errors_dict = {}
url = 'https://api2.sota.org.uk/api/summits/'

for summit in df_log_summits['SOTA_REF']:
    summit_url = f"{url}{summit}"
    try:
        r = requests.get(summit_url)
        print(f'Status code: {r.status_code} for {summit}')
        summits_dict[summit] = r.json()
# if errors occur (summit from the log was not found in SOTA database, it's saved in a dictionary,
    except Exception:
        errors_dict[summit] = r.status_code
        pass

df_summits = pd.DataFrame(summits_dict)

# user is being notified about summits where errors occured and entries with them are removed from summits list for visualisation
if errors_dict:
    print(f'\nFollowing errors were reported - QSO will be not included')
    for summit in errors_dict.keys():
        print(f'Error {errors_dict[summit]} for {summit}.')
        df_log_summits = df_log_summits.loc[df_log_summits['SOTA_REF'] != summit]

# save number of chases for each summit (from log) in myChases field in DataFrame
for summit in df_log_summits['SOTA_REF']:
    df_summits[summit]['myChases'] = df_log_SOTA[['SOTA_REF']][df_log_SOTA['SOTA_REF'] == summit].count()[0]

# transpose df_summits dataframe for easier visualisation
df_summits_transposed = df_summits.transpose(copy = True)

# change data type for Series important for visualisation (summits coordinates, SOTA points and number of chases)
# for numeric format
df_summits_transposed['latitude'] = df_summits_transposed['latitude'].astype('float')
df_summits_transposed['longitude'] = df_summits_transposed['longitude'].astype('float')
df_summits_transposed['myChases'] = df_summits_transposed['myChases'].astype('int')
df_summits_transposed['points'] = df_summits_transposed['points'].astype('int')

# list chaser's positions from GRID square and re-calculate them into coordinates

# prepare list of my chasing locations if any
# if there's location saved as GRID Square reference - use it to determine coordinates and set map center
# on the most common locator (home QTH)
# if there is no chaser's location - center a map on most chased summit
my_coordinates = []

if ('MY_GRIDSQUARE' in df_log_SOTA) == True:
    for locator in df_log_SOTA['MY_GRIDSQUARE'].drop_duplicates():
            my_coordinates.append(list(mh.to_location(locator)))
    home_QTH = list(mh.to_location(df_log_SOTA['MY_GRIDSQUARE'].value_counts().idxmax()))
    map_center = home_QTH
else:
    map_center = [df_summits_transposed['latitude'][df_summits_transposed['myChases'].idxmax()],
    df_summits_transposed['longitude'][df_summits_transposed['myChases'].idxmax()]]

# add column rel_Chases to df_summits_transposed DataFrame with relative number of chasers for a summit
df_summits_transposed['rel_Chases'] = df_summits_transposed['myChases'] / df_summits_transposed['myChases'].max()


# set-up a colormap to visuelize summit's points (between 1 and 10)
summit_points = cm.LinearColormap(colors=['magenta', 'orange','red'], index=[1,5,10],vmin=1,vmax=10).to_step(10)

# create a map with Folium
chasers_map = folium.Map(location=map_center,
                         tiles="Stamen Terrain",
                         zoom_start=9)

# add summits to a map
for summit in df_log_summits['SOTA_REF']:
    folium.CircleMarker(
    location = [df_summits_transposed['latitude'][summit], df_summits_transposed['longitude'][summit]],
    radius = 20*df_summits_transposed['rel_Chases'][summit],
    popup = f"{df_summits_transposed['summitCode'][summit]},\n{df_summits_transposed['name'][summit]}\n{df_summits_transposed['myChases'][summit]} QSOs",
    color = summit_points(df_summits_transposed['points'][summit]),
    fill = True,
    weight = 0,
    fill_opacity = 1
).add_to(chasers_map)

# add home marker to map
if ('MY_GRIDSQUARE' in df_log_SOTA) == True:
    folium.Marker(
        location=home_QTH,
        popup=f"home QTH: {df_log_SOTA['MY_GRIDSQUARE'].value_counts().idxmax()}",
        icon=folium.Icon(color="blue", icon="glyphicon-home"),
    ).add_to(chasers_map)

# add other locations to map
for coordinate in my_coordinates:
    if coordinate == map_center:
        pass
    else:
        folium.CircleMarker(
            location = coordinate,
            popup = 'field QTH',
            color = 'dodgerblue',
            fill = True,
            fill_opacity = 1,
            weight = 0,
            radius = 5
        ).add_to(chasers_map)

# print map with colorscale and save it in chasers_map.html file
chasers_map.add_child(summit_points)
chasers_map.save('chasers_map.html')


