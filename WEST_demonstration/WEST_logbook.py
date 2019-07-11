
# coding: utf-8

# WEST, branje logbooka

import scipy as sp
from os import path
from intervals2D import pin_point

def tag_to_hrs(timetag):
    hrs, mins = map(float, timetag.split(':'))
    hours = hrs + (mins ) / 60
    return hours

def tag_to_hrs_u(timetag):
    
    values = map(float, timetag.split(':'))
    hours = 0
    for idx in range(3):
        try:
            hours += values[idx] / 60**idx
        except IndexError:
            pass
    # stotinke
    try:
        hours += 0.01 * values[3] / 60**2
    except IndexError:
        pass

    return hours

def strip_date(datetag):
    datetag, timetag = datetag.split(' ')
    return datetag
    
month_d = {'Jan': '01',
           'Feb': '02',
           'Mar': '03',
           'Apr': '04',
           'Jun': '06',
           'Jul': '07',
           'Aug': '08',
           'Sep': '09',
           'Oct': '10',
           'Nov': '11',
           'Dec': '12'
          }

def reform_date(times_date):
    dd, mnt, yr = times_date.split('-')
    mm = month_d[mnt]
    yy = '20%s' %yr
    datetag = '%s-%s-%s' %(yy, mm, dd.zfill(2))
    return datetag

def read_pulse_times_file(filename):
    """Read a WEST logbook file"""
    # errors:
    # 10: file not found (IO error)
    # 12: file empty of sensible data
    tag = {'name': path.split(filename)[1]}
    cols = {'date': [], 'time': [], 'hours': [], 'shot': []}
    
    try:
        with open(filename, 'r') as f:
            rawfeed = f.read()
            rawfeed = rawfeed.splitlines()
    except IOError:
        return [10, tag, cols]
    if len(rawfeed) == 0:
        return [11, tag, cols]

    for line in rawfeed:
        if len(line) < 11:
            continue
        shot, datetag = line.split('\t')
        shot = int(shot)
        date, time = datetag.split(' ')
        cols['shot'].append(shot)
        cols['date'].append(reform_date(date))
        cols['time'].append(time.replace('.', ''))
        
    cols['hours'] = map(tag_to_hrs_u, cols['time'])
    #cols['date'] = map(strip_date, cols['date'])
    cols['shot'] = map(int, cols['shot'])
    for what in cols.keys():
        cols[what] = sp.array(cols[what])
    tag['dates'] = sorted(list(set(cols['date'])))
    return [0, tag, cols]

def read_logbook_file(filename):
    """Read a WEST logbook file"""
    # errors:
    # 10: file not found (IO error)
    # 12: file empty of sensible data
    tag = {'name': path.split(filename)[1]}
    cols = {'date': [], 'time': [], 'hours': [], 'shot': []}
    try:
        with open(filename, 'r') as f:
            rawfeed = f.read()
            rawfeed = rawfeed.replace('\xef\xbb\xbf','')
            rawfeed = rawfeed.replace('"', '')
            rawfeed = rawfeed.splitlines()
    except IOError:
        return [10, tag, cols]
    tab = []
    for line in rawfeed:
        tab.append(line.split(';'))
    if len(tab) == 0:
        return [11, tag, cols]
    header = tab[0]
    if len(tab) <= 2:
        return [12, tag, cols]
    # preprost primer: dan, ura, shot

    # shot idx = 6
    # day idx = 2
    # time idx = 7
    idx_d = {'date': 1, 'time': 7, 'shot': 6}
    
    for line in tab[1:]:
        if len(line) < len(header):
            continue
        if line[0] == 'session_id':
            continue
        for what in idx_d.keys():
            cols[what].append(line[idx_d[what]])
    cols['hours'] = map(tag_to_hrs, cols['time'])
    cols['date'] = map(strip_date, cols['date'])
    cols['shot'] = map(int, cols['shot'])
    for what in cols.keys():
        cols[what] = sp.array(cols[what])
    tag['dates'] = sorted(list(set(cols['date'])))
    return [0, tag, cols]


class WEST_logbook:
    
    def __init__(self, filename):
        #err, tag, cols = read_logbook_file(filename)
        err, tag, cols = read_pulse_times_file(filename)
        self.tag = tag
        self.tag['open_error'] = err
        self.tag['number_of_shots'] = len(cols['shot'])
        self.cols = cols
      
    def shot_hours(self, shot):
        mask = self.cols['shot'] == shot
        try:
            hours = self.cols['hours'][mask][0]
        except IndexError:
            hours = 0
            
        return hours
            
    def shot_date(self, shot):
        mask = self.cols['shot'] == shot
        try:
            date = self.cols['date'][mask][0]
            time = self.cols['time'][mask][0]
        except IndexError:
            date = 'N/A'
            time = 'N/A'
            
        return date, time

    def shots_at_date(self, date):
        on_day = self.cols['date'] == date
        shot_col = self.cols['shot'][on_day]
        return shot_col
    
    def shot_at_hours(self, date, hours):
        on_day = self.cols['date'] == date
        shot_col = self.cols['shot'][on_day]
        hours_col = self.cols['hours'][on_day]
        if len(shot_col) == 0:
            return 'N/A', 'N/A'
        
        idx = pin_point(hours_col, hours)
        found_shot = shot_col[idx]
        found_hours = hours_col[idx]
        
        return found_shot, found_hours
        
