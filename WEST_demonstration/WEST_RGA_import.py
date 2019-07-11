
# coding: utf-8

# Importer for pfeifer RGA files
# used on WEST
# Aleksander Drenik
# December 2018
# IPP Garching

import scipy as sp
from os import path

def tag_to_hrs(timetag):
    hrs, mins, secs, stots = map(float, timetag.split(':'))
    hours = hrs + (mins + (secs + 0.01 * stots) / 60) / 60
    return hours
 
def tag_to_hrs_2(timetag):
    hrs, mins, secs = map(float, timetag.split(':'))
    hours = hrs + (mins + (secs) / 60) / 60
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
    
    
def read_tech_pressure(filename):
    # Error codes:
    # 10 - error opening file
    # 12 - no data in file
    tag = {'title': path.split(filename)[1]}
    datacols = {}
    try:
        with open(filename, 'r') as f:
            rawfeed = f.read().splitlines()

            header = rawfeed[0].split('\t')
            data = []
    except IOError:
        return [10, tag, datacols]
    for line in rawfeed[1:]:
        elements = line.split('\t')
        data.append(elements)
    if len(data) == 0:
        return [12, tag, datacols]
    data = sp.array(data[:-1])
    cols = sp.transpose(data)

    tag = {'date': cols[0][0],
          'time': cols[1][0]}

    datacols = {'hours': sp.array(map(tag_to_hrs_2, cols[1]))}
    for idx in [2, 3, 4]:
        datacols[header[idx]] = sp.array(map(float, cols[idx]))
    datacols['time'] = 3600 * datacols['hours']
    datacols['time'] -= datacols['time'][0]
    
    return [0, tag, datacols]

def read_MID(filename):
    # Error codes:
    # 10 - error opening file
    # 12 - no data in file
    # 13 - no data after applying line length filter
    tag = {'device':'Pfeifer Prisma', 'mode':'MID recording'}
    fn1 = path.split(filename)[1]
    tag['title'] = fn1.split('.')[0]

    try:
        rawfile = open(filename, 'r')
    except IOError:
        return [10, tag, columns]
    rawfeed = rawfile.read().splitlines()
    rawfile.close()

    # iskanje informacij o skanih
    for i in range(len(rawfeed)):
        line = rawfeed[i]
        elements = line.split('\t')
        if elements[0].find('Datablock') > -1:
            hdr_start_i = i + 1
        if elements[0].find('Cycle') >-1 :
            header_i = i
            data_start_i = i + 1
            break

    mass_index = {}
    for line in rawfeed[hdr_start_i:]:
        elements = line.replace("'",'').split('\t')
        if len(elements) < 2:
            break
        mass_index[elements[0]] = {'exact': float(elements[1]) , 'name': int(round(float(elements[1])))}

    header_raw = rawfeed[header_i].replace("'",'').split('\t')

    columns_raw = {}
    for what in header_raw:
        if what == '':
            continue
        if what in mass_index.keys():
            mass = mass_index[what]['name']
            columns_raw[mass] = []
        else:
            columns_raw[what] = []

    datablock = rawfeed[data_start_i:-1]
    if len(datablock) <= 1:
        return [12, tag, columns]

    for line in datablock:
        elements = line.split('\t')
        for i in range(len(header_raw)):
            name_raw = header_raw[i]
            if name_raw == '':
                continue
            if name_raw in mass_index.keys():
                name = mass_index[name_raw]['name']
            else:
                name = name_raw
            try:
                columns_raw[name].append(float(elements[i]))
            except:
                columns_raw[name].append(elements[i])
    columns_raw['hours'] = map(tag_to_hrs, columns_raw['Time'])    
    columns = {}
    columns['time'] = sp.array(columns_raw['RelTime[s]'])
    columns['time'] -= columns['time'][0]
    columns['hours'] = sp.array(columns_raw['hours'])
    for label in mass_index.values():
        mass = label['name']
        columns[mass] = sp.array(columns_raw[mass])
        
    tag['date'] = columns_raw['Date'][0]
    tag['time'] = columns_raw['Time'][0]
    #tag['time_col'] = 'time'

        
    return [0, tag, columns]
