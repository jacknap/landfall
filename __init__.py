import os
import sys
from compression.zlib import error

import requests

from hurricane import Hurricane


def download_file(url, filename):
    try:
        print(f"Downloading {filename}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Write content to file in chunks
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f"Successfully downloaded {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


def parse_file(filename):
    hurricanes: list[Hurricane] = []
    current = None
    with open(filename, "rt") as file:
        for line in file:
            if line.startswith("AL"):
                if current != None:  # Start of file
                    hurricanes.append(current)
                tokens = [token.strip() for token in line.split(",")]
                current = Hurricane(tokens[0], tokens[1], tokens[2])
            else:
                if current == None:
                    print(f"Read error on line\n{line}")
                    sys.exit(1)
                tokens = [token.strip() for token in line.split(",")]
                if not current.add_record(
                    tokens[0],
                    tokens[1],
                    tokens[2],
                    tokens[3],
                    tokens[4][:-1],
                    tokens[4][-1:],
                    tokens[5][:-1],
                    tokens[5][-1:],
                    tokens[6],
                ):
                    print(f"Value error on line\n{line}")
                    sys.exit(1)
        if current != None:  # End of file
            if current.record_count != len(current.records):
                print(
                    f"Error: record count: {current.record_count} does not equal actual amount of records: {len(current.records)}"
                )
                sys.exit(1)
            hurricanes.append(current)
    return hurricanes


def max_wind_speed_hurricane(hurricanes):
    temp = max(hurricanes, key=lambda x: x.max_wind_speed_record())
    return f"Maximum wind speed was {temp.max_wind_speed_record()[7]} knots during {temp.id} {temp.name} at {temp.max_wind_speed_record()[0].strftime('%Y-%m-%d %H:%M')}"


def display_hurricanes(hurricanes):
    for h in hurricanes:
        print(h)


def main():
    filename = "hurdat2-1851-2025-02272026.txt"
    url = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-02272026.txt"
    if not os.path.exists(filename):
        download_file(url, filename)
    else:
        print(f"Found file {filename}")
    display_hurricanes(parse_file(filename))


if __name__ == "__main__":
    main()
