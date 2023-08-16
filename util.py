import os
import urllib.request
import zipfile


def download_files(url, raw_path):
    zip_path, _ = urllib.request.urlretrieve(url)
    print(zip_path)

otp_path = 'GTFS'
os.makedirs(otp_path, exist_ok=True)
for tranit_type in ["local-bus", "light-rail", "metro", "marc", "commuter-bus"]:
    transit_gtfs_file = f"{otp_path}/mdotmta_gtfs_{tranit_type}"
    os.makedirs(transit_gtfs_file, exist_ok=True)
    if not os.path.isfile(transit_gtfs_file):
        url = f"https://feeds.mta.maryland.gov/gtfs/{tranit_type}"
        download_files(url, transit_gtfs_file)