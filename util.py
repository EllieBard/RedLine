import os
import urllib.request
import zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def download_files(url, raw_path):
    zip_path, _ = urllib.request.urlretrieve(url)
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(raw_path)

otp_path = 'GTFS'
os.makedirs(otp_path, exist_ok=True)
for tranit_type in ["local-bus", "light-rail", "metro", "marc", "commuter-bus"]:
    transit_gtfs_file = f"{otp_path}/mdotmta_gtfs_{tranit_type}"
    os.makedirs(transit_gtfs_file, exist_ok=True)
    if not os.path.isfile(transit_gtfs_file):
        url = f"https://feeds.mta.maryland.gov/gtfs/{tranit_type}"
        download_files(url, transit_gtfs_file)

def plotting(df, column_name, label, plot_title):
    ax = df.plot(column = column_name, legend = True, missing_kwds = {'color':'lightgrey'}, legend_kwds = {'location' : 'left', 'label' : label})
    ax.set_axis_off()
    plt.title(plot_title)
    return ax

def transpose_create_geoid(df):
    #transpose
    df = df.set_index('Label (Grouping)').transpose().reset_index()
    #replace non-standard values
    df.replace('-', np.nan, inplace=True)
    df.replace('250,000+','250000', inplace=True)
    df.replace('2,500-','2500', inplace=True)
    #to create a GEOID column, split the census data labels and create a new dataframe
    geoid = df['index'].str.split(expand = True)
    geoid = geoid[2].str.split(pat='.', expand = True)
    geoid = geoid.replace('\W','', regex = True)
    #fill in first four digits of tract number
    geoid[0] = geoid[0].str.pad(width = 4, side = 'left', fillchar = '0')
    #fill in last two digits of tract number
    geoid[1] = geoid[1].fillna('0')
    geoid[1] = geoid[1].str.pad(width = 2, side = 'left', fillchar = '0')
    #concatenate state, county, and tract codes(24510 = state and county code for Baltimore City, Maryland)
    df['GEOID'] = '24510' + geoid[0] + geoid[1]
    df['GEOID'] = df['GEOID'].astype('Int64')
    return df

def food_desert_map(ttm_df, title, centroid_df, blockgroup_df, vulnerability_df, tract_df):
    shortest_time_df = ttm_df.groupby('from_id')['travel_time'].min().reset_index()
    shortest_time_df = centroid_df.merge(shortest_time_df, left_on = 'id', right_on = 'from_id')
    shortest_time_df = shortest_time_df.to_crs(4269)
    shortest_time_df = blockgroup_df.sjoin(shortest_time_df)
    shortest_time_df['GEOID'] = shortest_time_df['GEOID_left'].astype(str).str.slice(stop=11).astype('int64')
    shortest_time_df = shortest_time_df.loc[shortest_time_df['travel_time'] >= 10]
    shortest_time_df = shortest_time_df.groupby('GEOID')['travel_time'].mean().reset_index()
    shortest_time_df = vulnerability_df.merge(shortest_time_df, on = 'GEOID')
    base = tract_df.plot(color = 'white', edgecolor = 'black')
    shortest_time_df.plot('travel_time', ax = base, edgecolor = 'black')
    plt.title(title)
    base.set_axis_off()
    return base