import dash_leaflet as dl # to visualise map

from dash import html, dcc, Dash, Input, Output # for dashboard construction

from SpotsVisualiser import SpotsVisualiser
import config # script configuration

# functions to deploy dash map 

sota_spots_dashboard = Dash(__name__)

def set_map_design(map_dashboard, spots_map_instance) -> None:
        """Defines Dash app layout."""
        map_dashboard.layout = html.Div([
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
                    children = generate_maps(spots_map_instance.create_spots_markers(spots_map_instance.spots_to_visualisation)), # generate map's layers
                    zoom=3, # whole world should be presented upon dashboard start
                    center=(50, 20), # map is centered near Kraków - city where I live
                    style={
                        "height": "100vh", # map's height is 100% of the window
                    },
                    id = 'spots_map', # create a map with spots visualisation
                )
            ],)

def create_callback(spots_map_instance):
    """
    Creates callback function with access to SpotsVisualiser instance.
    Args:
        spots_map_instance: SpotsVisualiser instance
    """
    @sota_spots_dashboard.callback(
        Output('spots_map', 'children'),
        [Input('band_selection', 'value'),
         Input('mode_selection', 'value')]
    )
    def update_map(bands, modes):
        # Set default values if none selected
        if not bands:
            bands = spots_map_instance._BANDS.index
        if not modes:
            modes = spots_map_instance._MODES['mode']
            
        # spots_filtering
        filtered_spots = spots_map_instance.spots_to_visualisation[
            (spots_map_instance.spots_to_visualisation['band'].isin(bands)) & 
            (spots_map_instance.spots_to_visualisation['mode'].isin(modes))
        ].copy()
        
        # create markers for spots visualisation
        markers = spots_map_instance.create_spots_markers(filtered_spots)
        return generate_maps(markers)
    
    return update_map

def generate_maps(spots_markers) -> list:
    """Generate an input for dl.Map object"""
    return [
            dl.TileLayer(),
            dl.LayerGroup(spots_markers),
        ]    

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
    spots_map.create_visualisation_data()
    spots_map.remove_unused_columns()
    spots_map.drop_summits_not_found()
    print(spots_map.spots_to_visualisation)
    spots_map.create_spots_markers(spots_map.spots_to_visualisation)
    print(spots_map.spots_to_visualisation)
    
    set_map_design(sota_spots_dashboard, spots_map)
    create_callback(spots_map) 

    sota_spots_dashboard.run(port=config._PORT_NUMBER, 
                             debug=config._DEBUG_FLAG)


### NEW above
### OLD below

# # save errors to file
# if len(summits_errors) != 0:
#     with open('summits_errors.txt', 'a') as f:
#         for error in summits_errors:
#             f.write(f'{error}\n')