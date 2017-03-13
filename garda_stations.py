import math

class Station:
    def __init__(self, csv_line_tup, lat=0, lng=0):
        self.station_name = csv_line_tup[1]
        self.division = csv_line_tup[2] if 'D.M.R' not in csv_line_tup[2] else 'Dublin'
        self.x = csv_line_tup[3]
        self.y = csv_line_tup[4]
        self.murders = list(map(int, csv_line_tup[5:18]))
        self.negligent = list(map(int, csv_line_tup[18:31]))
        self.kidnapping = list(map(int, csv_line_tup[31:45]))
        self.robery = list(map(int, csv_line_tup[45:59]))
        self.burglary = list(map(int, csv_line_tup[59:73]))
        self.theft = list(map(int, csv_line_tup[73:87]))
        self.lat = lat
        self.lng = lng
        self.score = (self.five_year_burglary() +
                      self.five_year_theft() +
                      self.five_year_robery() +
                      self.five_year_violent_crime_avg())/4

    def five_year_violent_crime_avg(self):
        return sum(self.murders[-5:])/5

    def five_year_burglary(self):
        return sum(self.burglary[-5:])/5

    def five_year_theft(self):
        return sum(self.theft[-5:])/5

    def five_year_robery(self):
        return sum(self.robery[-5:])/5

    def get_score(self):
        return self.score

    def dist_from_coord(self, lat2, lng2):
        return ((self.lat - lat2)**2 + (self.lng - lng2)**2)**0.5

