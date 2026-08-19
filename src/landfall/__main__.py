import os
import sys
from compression.zlib import error
from pathlib import Path

import PySimpleGUI as sg
import requests

from hurricane import Hurricane


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


def parse_file(file_path):
    hurricanes: list[Hurricane] = []
    current = None
    with open(file_path, "rt") as file:
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


def load_data():
    DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
    file_path = DATA_DIR / "hurdat2-1851-2025-02272026.txt"

    url = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-02272026.txt"
    if not os.path.exists(file_path):
        download_file(url, file_path)
    else:
        print(f"Found file {file_path}")
    return file_path


def main():
    """tkinter implementation
    display = tk.Tk()
    label = tk.Label(display, text="Hurricanes", font=("Arial", 50)).grid(
        row=0, columnspan=4
    )
    col = ("ID", "Name", "Max Wind Speed", "Date")
    listBox = ttk.Treeview(display, columns=col, show="headings")

    get_data = tk.Button(
        display, text="Get Data", width=15, command=parse_file(load_data())
    ).grid(row=4, column=0)

    closeButton = tk.Button(display, text="Close", width=15, command=exit).grid(
        row=4, column=1
    )
    display.mainloop()
    """


if __name__ == "__main__":
    main()
