import random
from itertools import cycle, zip_longest
from time import sleep

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import mplleaflet
from shapely.geometry import Point

from public_traces import GPX


def plot_gpx_trace(gpx_data):
    # Step 1: Data Preparation
    track_points = gpx_data["track_segments"][0]["track_points"]
    latitudes = [point["lat"] for point in track_points]
    longitudes = [point["lon"] for point in track_points]

    # Step 2: GeoDataFrame Creation
    geometry = [Point(xy) for xy in zip(longitudes, latitudes)]
    gdf = gpd.GeoDataFrame(geometry=geometry)

    # Step 3: Map Plotting
    fig, ax = plt.subplots()
    gdf.plot(ax=ax, marker="o", color="blue", markersize=5)
    mplleaflet.show(fig=ax.figure)


def get_map(gpx_list: list[GPX]) -> folium.Map:
    gpx_data = gpx_list[0].as_dict()
    track_points = gpx_data["track_segments"][0]["track_points"]
    m = folium.Map(
        location=[track_points[0]["lat"], track_points[0]["lon"]],
        zoom_start=15,
    )
    m.render()
    return m


def plot_gpx_trace_folium(m: folium.Map, gpx_list: list[GPX]) -> None:
    for (i, gpx), color in zip(
        enumerate(gpx_list),
        cycle(["red", "blue", "green", "purple", "orange", "darkred"]),
    ):
        gpx_data = gpx.as_dict()
        track_points = gpx_data["track_segments"][0]["track_points"]
        # Initialize the Folium map at the first point

        # Add points to the map
        folium.PolyLine(
            locations=[[point["lat"], point["lon"]] for point in track_points],
            radius=3,
            color=color,
            # fill=True,
            # fill_color=color,
            # fill_opacity=0.6,
        ).add_to(m)
        print(i, color)


# def plot_gpx_trace_folium(m: folium.Map, gpx_list: list[GPX]) -> None:
#     for (i, gpx), color in zip(
#         enumerate(gpx_list),
#         cycle(["red", "blue", "green", "purple", "orange", "darkred"]),
#     ):
#         gpx_data = gpx.as_dict()
#         track_points = gpx_data["track_segments"][0]["track_points"]
#         # Initialize the Folium map at the first point
#
#         # Add points to the map
#         for point in track_points:
#             folium.CircleMarker(
#                 location=(point["lat"], point["lon"]),
#                 radius=3,
#                 color=color,
#                 fill=True,
#                 fill_color=color,
#                 fill_opacity=0.6,
#             ).add_to(m)
#         print(i)
