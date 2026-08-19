import os
import sys
from compression.zlib import error
from datetime import datetime
from pathlib import Path

import pandas
import requests

from landfall.storm import Storm


# download given url and write it to file_path
def download_file(url, file_path):
    try:
        print(f"Downloading {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Write content to file in chunks
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f"Successfully downloaded {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


# parse given file_path and create storm objects from its contents
def parse_file(file_path):
    storms: list[Storm] = []
    current = None
    with open(file_path, "rt") as file:
        for line in file:
            if line.startswith("AL"):  # start of storm block
                # Start of file does not need to append last read storm to list
                if current != None:
                    storms.append(current)

                # create new storm
                tokens = [token.strip() for token in line.split(",")]

                # store current storm to add records to it on following lines
                try:
                    current = Storm(tokens[0], tokens[1], tokens[2])
                except ValueError:
                    print(f"Value error on line\n{line}")
                    sys.exit(1)
            else:  # record line
                if current == None:
                    print(f"First line should start with basin code\n{line}")
                    sys.exit(1)
                tokens = [token.strip() for token in line.split(",")]

                # use +/- for latitude and longitude instead of NSWE
                if tokens[4][-1:] == "S":
                    latitude_mult = -1
                elif tokens[4][-1:] == "N":
                    latitude_mult = 1
                else:
                    print(f"Latitude read error on line\n{line}")
                    sys.exit(1)
                if tokens[5][-1:] == "W":
                    longitude_mult = -1
                elif tokens[5][-1:] == "E":
                    longitude_mult = 1
                else:
                    print(f"Longitude read error on line\n{line}")
                    sys.exit(1)

                # landfall cannot happen twice in a row, or at the beginning of a hurricane
                if len(current.records) == 0 or (current.records[-1][6]):
                    landfall_not_possible = True
                else:
                    landfall_not_possible = False

                # add record to storm
                try:
                    current.add_record(
                        date_time=datetime(
                            int(tokens[0][:4]),
                            int(tokens[0][4:6]),
                            int(tokens[0][6:8]),
                            int(tokens[1][:2]),
                            int(tokens[1][2:4]),
                        ),
                        identifier=tokens[2],
                        status=tokens[3],
                        latitude=round(float(tokens[4][:-1]) * latitude_mult, 1),
                        longitude=round(float(tokens[5][:-1]) * longitude_mult, 1),
                        wind_speed=int(tokens[6]),
                        florida_landfall=in_florida(  # landfall is when it is in Florida and last record was not in Florida
                            latitude=round(float(tokens[4][:-1]) * latitude_mult, 1),
                            longitude=round(float(tokens[5][:-1]) * longitude_mult, 1),
                        )
                        and not landfall_not_possible,
                    )
                except ValueError:
                    print(f"Value error on line\n{line}")
                    sys.exit(1)
                except IndexError:
                    print(f"Index error on line\n{line}")
                    sys.exit(1)
        if current != None:  # End of file
            if current.record_count != len(current.records):
                print(
                    f"Error: record count: {current.record_count} does not equal actual amount of records: {len(current.records)}."
                )
                sys.exit(1)
            storms.append(current)
    return storms


# returns record with highest wind speed from storm with the highest wind speed
def max_wind_speed_storm(storms):
    return max(storms, key=lambda x: x.max_wind_speed_record())


# loads necessary file, attempts to download it if it is not present
def load_file():
    DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
    file_path = DATA_DIR / "hurdat2-1851-2025-02272026.txt"

    url = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-02272026.txt"
    if not os.path.exists(file_path):
        download_file(url, file_path)
    else:
        print(f"Found file {file_path}")
    return file_path


# returns true if the storm is in Florida (ish)
def in_florida(latitude, longitude):
    if 31.0 > latitude > 30.3 and -86.0 > longitude > -87.5:
        return True
    if 31.0 > latitude > 30.0 and -85.4 > longitude > -86.0:
        return True
    if 30.7 > latitude > 29.6 and -84.3 > longitude > -85.4:
        return True
    if 30.7 > latitude > 30.0 and -83.9 > longitude > -84.3:
        return True
    if 30.7 > latitude > 29.9 and -83.6 > longitude > -83.9:
        return True
    if 30.7 > latitude > 29.7 and -83.4 > longitude > -83.6:
        return True
    if 30.7 > latitude > 29.4 and -83.2 > longitude > -83.4:
        return True
    if 30.7 > latitude > 29.1 and -83.7 > longitude > -83.2:
        return True
    if 30.7 > latitude > 29.1 and -82.8 > longitude > -83.7:
        return True
    if 30.7 > latitude > 27.4 and -82.5 > longitude > -82.8:
        return True
    if 30.7 > latitude > 26.4 and -81.8 > longitude > -82.5:
        return True
    if 30.7 > latitude > 25.1 and -80.0 > longitude > -81.8:
        return True
    if 24.7 > latitude > 24.5 and -80.8 > longitude > -82.2:  # Florida Keys
        return True
    return False


# display information from given storms in standard print output
def display_stdout(storms):
    # filter by storms which made landfall in Florida
    f_storms = list(filter(Storm.florida_landfall, storms))

    mydataset = {
        "Name": list(map(lambda x: x.name, f_storms)),
        "Records": list(map(lambda x: x.record_count, f_storms)),
        "Max Wind Speed": list(map(lambda x: x.max_wind_speed_record()[5], f_storms)),
        "Florida Landfall": list(map(lambda x: x.florida_landfall(), f_storms)),
    }

    table = pandas.DataFrame(mydataset, index=list(map(lambda x: x.id, f_storms)))
    with pandas.option_context("display.max_rows", None, "display.max_columns", None):
        print(table)


def main():
    storms = parse_file(load_file())
    display_stdout(storms)


if __name__ == "__main__":
    main()
