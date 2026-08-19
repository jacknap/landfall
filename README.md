# Landfall

This is a small python project to process information from the Atlantic hurricane database (HURDAT2), and print some information on storms which made landfall in Florida.

The specification for the HURDAT2 database can be found [here](https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atlantic.pdf). The dataset will be downloaded if it is not already present in the data folder.

I used [uv](https://github.com/astral-sh/uv) to manage the virtual environment for this and ran it with `uv run landfall` after cloning the repo.
