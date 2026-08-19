class Storm:
    def __init__(self, id, name, record_count):
        self.id = id
        self.year = id[4:]
        self.name = name
        try:
            self.record_count = int(record_count)
        except ValueError:
            print(f"Value error on {record_count} in {self.id}")
        self.records = []

    def __str__(self):
        if self.name != "UNNAMED":
            return f"Storm {self.name} started on {self.records[0][0].strftime('%Y-%m-%d')}, went until {self.records[-1][0].strftime('%Y-%m-%d')}, and had a maximum wind speed of {self.max_wind_speed_record()[7]} knots."
        else:
            return f"Storm {self.id} started on {self.records[0][0].strftime('%Y-%m-%d')}, went until {self.records[-1][0].strftime('%Y-%m-%d')}, and had a maximum wind speed of {self.max_wind_speed_record()[7]} knots."

    # add a record of the storm
    def add_record(
        self,
        date_time,
        identifier,  # ex. landfall
        status,  # HU, TS, DB, EX, SS, etc.
        latitude,
        longitude,
        wind_speed,
        florida_landfall,
    ):
        if len(self.records) + 1 > self.record_count:
            return False  # if more records than specified in starting line
        self.records.append(
            (
                date_time,
                identifier,
                status,
                latitude,
                longitude,
                wind_speed,
                florida_landfall,
            )
        )
        return

    # returns if a landfall event occurred with Florida
    def florida_landfall(self):
        # get record where florida_landfall is true
        record = max(self.records, key=lambda x: x[6])

        if record[6]:  # if Florida landfall
            return f"{record[0].strftime('%Y-%m-%d')} at {record[3]}, {record[4]}"
        return False

    # return record with maximum wind speed
    def max_wind_speed_record(self):
        return max(self.records, key=lambda x: x[5])
