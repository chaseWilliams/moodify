import time
import calendar
import datetime

class TimeMachine:
    
    def __init__(self, year):
        year = str(year)
        self.seasons = {
            'spring': ( time.strptime('21 Mar ' + year, '%d %b %Y'),
                      time.strptime('21 Jun ' + year, '%d %b %Y')),
            'summer': ( time.strptime('21 Jun ' + year, '%d %b %Y'),
                      time.strptime('23 Sep ' + year, '%d %b %Y')),
            'fall': ( time.strptime('23 Sep ' + year, '%d %b %Y'),
                      time.strptime('21 Dec ' + year, '%d %b %Y')),
            'winter': ( time.strptime('21 Dec ' + year, '%d %b %Y'),
                        time.strptime('21 Mar ' + str(int(year) + 1), '%d %b %Y'))
        }
        self.year = year
        
    def set_year(self, new_year):
        self = self.__init__(new_year)
        
    def in_season(self, season, df):
        timeslice = self.seasons[season]
        def check_time(seconds):
            try:
                listen_time =  time.gmtime(int(seconds))
            except TypeError:
                return False
            return listen_time > timeslice[0] and listen_time < timeslice[1]
        arr_time_check = np.vectorize(check_time)
        return df[arr_time_check(df['date'])]
    
    def in_year(self, df):
        date = datetime.date(int(self.year), 1, 1)
        def check_time(seconds):
            try: 
                listen_time =  datetime.date.fromtimestamp(int(seconds))
            except TypeError:
                return False
            return listen_time.year == date.year
        arr_time_check = np.vectorize(check_time)
        return df[ arr_time_check(df['date'])]
    
