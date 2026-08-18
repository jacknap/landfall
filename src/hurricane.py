from datetime import datetime


class Hurricane:
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
            return f"Hurricane {self.name} started on {self.records[0][0].strftime('%Y-%m-%d at %H:%M')}, went until {self.records[-1][0].strftime('%Y-%m-%d at %H:%M')}, had a maximum wind speed of {self.max_wind_speed_record()[7]} knots."
        else:
            return f"Hurricane {self.id} started on {self.records[0][0].strftime('%Y-%m-%d at %H:%M')}, went until {self.records[-1][0].strftime('%Y-%m-%d at %H:%M')}, had a maximum wind speed of {self.max_wind_speed_record()[7]} knots."

    def add_record(
        self,
        date,
        time,
        identifier,
        status,
        latitude,
        ns_hemisphere,
        longitude,
        we_hemisphere,
        wind_speed,
    ):
        if len(self.records) + 1 > self.record_count:
            return False
        try:
            self.records.append(
                (
                    datetime(
                        int(date[:4]),
                        int(date[4:6]),
                        int(date[6:8]),
                        int(time[:2]),
                        int(time[2:4]),
                    ),
                    identifier,
                    status,
                    round(float(latitude), 1),
                    ns_hemisphere,
                    round(float(longitude), 1),
                    we_hemisphere,
                    int(wind_speed),
                )
            )
        except ValueError:
            return False
        return True

    def min_wind_speed_record(self):
        return min(self.records, key=lambda x: x[7])

    def max_wind_speed_record(self):
        return max(self.records, key=lambda x: x[7])
