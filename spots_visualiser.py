import dash_leaflet as dl # to visualise map
import pandas as pd

from dash import html, dcc, Dash, Input, Output # for dashboard construction

from SpotsDownloader import SpotsDownloader
import config # script configuration

# functions to deploy dash map 

def set_map_design(spots_map_instance) -> Dash.layout:
    """Defines Dash app layout."""
    layout = html.Div([
        html.Div(
                dcc.Dropdown(
                    spots_map_instance._MODES['mode'], # values available
                    spots_map_instance._MODES['mode'], # values selected by default - all modes
                    multi=True,
                    placeholder='Select mode to apply filter or refresh page to show all',
                    id = 'mode_selection' # dropdown list to select modes to visualise
                    )),
        html.Div(
                dcc.Dropdown(
                    spots_map_instance._BANDS.index, # valus available
                    spots_map_instance._BANDS.index, # values selected by default - all bands
                    multi=True,
                    placeholder='Select band to apply filter or refresh page to show all',
                    id = 'band_selection' #dropdown list to select bands to visualise
                    )),
        dl.Map(
                children = [dl.TileLayer(),
                            dl.LayerGroup(id='spots_layer')], 
                zoom=3, # whole world should be presented upon dashboard start
                center=(50, 20), # map is centered near Kraków
                style={
                    "height": "100vh", # map's height is 100% of the window
                },
                id = 'spots_map', # create a map with spots visualisation
            )
        ],
        )
    
    return layout

def create_callback(spots_map_instance) -> list:
    """
    Creates callback function with access to SpotsDownloader instance.
    Args:
        spots_map_instance: SpotsDownloader instance
    """
    @sota_spots_dashboard.callback(
        Output('spots_layer', 'children'),
        [Input('band_selection', 'value'),
         Input('mode_selection', 'value')]
    )
    def update_markers(bands, modes) -> list:
        """Update markers on the map according to bands and modes selected in callback."""
        filtered_spots = filter_spots(spots_map_instance, bands, modes)
        spots_markers = create_spots_markers(filtered_spots)
        return spots_markers
    return update_markers

def filter_spots(spots_map_instance, bands:list, modes:list) -> pd.DataFrame:
        """ Filter spots for selected bands and modes."""
        return spots_map_instance.spots_to_visualisation.loc[
            (spots_map_instance.spots_to_visualisation['band'].isin(bands)) & 
            (spots_map_instance.spots_to_visualisation['mode'].isin(modes))
        ]

def create_spots_markers(spots_df) -> list:
    """Prepare CircleMarkers list for spots visualisation."""
    spots_markers_for_map = []
    spots_df.reset_index(inplace=True, drop=True)
    for _, row in spots_df.iterrows():
        spots_markers_for_map.append(
            dl.CircleMarker(
                center = [row['latitude'], row['longitude']],
                radius = (1 - row['time_since_spot']) * 30,
                children = dl.Popup(row['popup']),
                fillColor = row['band_color'],
                weight = 3,
                color = row['mode_color'],
                opacity = 1,
                fillOpacity = 1,
                id = f"{row['latitude']}_{row['longitude']}_{row['timeStamp']}"
            )
        )
    return spots_markers_for_map

# script flow

sota_spots_dashboard = Dash(__name__)

if __name__ == "__main__":
    spots_map = SpotsDownloader(lookback_time = -1)
    spots_map.process_spots()

    sota_spots_dashboard.layout = set_map_design(spots_map)
    create_callback(spots_map) 
    sota_spots_dashboard.run(port=config._PORT_NUMBER, 
                             debug=config._DEBUG_FLAG)

# TODO: Amend variables annotations
# TODO; Amend docstrings
# TODO: update documentation
# TODO: save errors to file
# if len(summits_errors) != 0:
#     with open('summits_errors.txt', 'a') as f:
#         for error in summits_errors:
#             f.write(f'{error}\n')