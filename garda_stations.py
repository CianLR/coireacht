import math

class Station:
    def __init__(self, csv_line_tup, lat=0, lng=0):
        self.station_name = csv_line_tup[1]
        self.division = csv_line_tup[2]
        self.x = csv_line_tup[3]
        self.y = csv_line_tup[4]
        self.murders = list(map(int, csv_line_tup[5:18]))
        self.lat = lat
        self.lng = lng

    def dist_from_coord(self, lat2, lng2):
        return ((self.lat - lat2)**2 + (self.lng - lng2)**2)**0.5

