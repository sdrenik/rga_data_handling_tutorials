# coding: utf-8


# Importer quaderinih ascii fajlov

import scipy as sp

def read_MID(filename):
    
    # Error codes:
    # 10 - error opening file
    # 12 - no data in file
    # 13 - no data after applying line length filter
    tag = {'device':'Pfeifer Prisma', 'mode':'MID recording'}
    columns_raw = {}
    columns_common = {}
    try:
        rawfile = open(filename, 'r')
    except IOError:
        return [10, tag, columns_raw, columns_common]
    rawfeed = rawfile.read().splitlines()
    rawfile.close()
    
    while rawfeed[0] == '':
        rawfeed = rawfeed[1:]
    header = rawfeed[0].split('\t')
    last_col = 0
    while header[-1] == '':
        header = header[:-1]
        last_col += 1
    data = []
    for line in rawfeed[2:]:
        splitline = line[:-last_col].split('\t')
        if splitline[-1] == '':
            continue
        data.append(splitline)
        #data.append(line[:-last_col].split('\t'))
    if len(data) == 0:
        return [12, tag, columns_raw, columns_common]
    data = sp.array(data)
    linelens = sp.array(map(len, data))
    good = linelens == max(linelens)
    data_g = data[good]
    if len(data_g) == 0:
        return [13, tag, columns_raw, columns_common]
    datacols = sp.transpose(data_g)
    first_timestamp = data[0][0]
    date, time = first_timestamp.split(' ')
    tag = {'device':'Pfeifer Prisma', 'mode':'MID recording'}
    tag['date'] = date
    tag['time'] = time

    hrs, mins, secs = map(int, time.split(':'))
    start_seconds = float(secs + 60 * (mins + 60 * hrs))

    col_index = {}
    sub_index = []
    for i in range(len(header)):
        sub_index.append(i)
        if header[i] != '':
            mass = int(header[i])
            col_index[mass] = sub_index
            sub_index = []

    columns_raw = {}
    for mass in col_index.keys():
        i1, i2, i3 = col_index[mass]
        columns_raw[mass] = {'timestamp': datacols[i1],
                             'seconds': sp.array(map(float,datacols[i2])),
                             'intensity': sp.array(map(float,datacols[i3]))}
        columns_raw[mass]['hours'] = (columns_raw[mass]['seconds'] + start_seconds)/3600

    columns_common = {}
    mass1 = col_index.keys()[0]
    columns_common['time'] = columns_raw[mass1]['seconds']
    columns_common['hours'] = columns_raw[mass1]['hours']
    for mass in columns_raw.keys():
        columns_common[mass] = columns_raw[mass]['intensity']

    return [0, tag, columns_raw, columns_common]
    
def read_quadera_MID2(filename):
    
    # Error codes:
    # 10 - error opening file
    # 12 - no data in file
    # 13 - no data after applying line length filter
    tag = {'device':'Pfeifer Prisma', 'mode':'MID recording'}
    columns_raw = {}
    columns_common = {}
    try:
        rawfile = open(filename, 'r')
    except IOError:
        return [10, tag, columns_raw, columns_common]
    rawfeed = rawfile.read().splitlines()
    rawfile.close()
    
    while rawfeed[0] == '':
        rawfeed = rawfeed[1:]
    subtag = {}
    full_header = False
    comma = False
    dataspot = 1
    datajump = 0
    for rawline in rawfeed[:10]:
        line = rawline.split('\t')
        if line[0] == 'Time':
            # nasli smo podatke
            dataspot = rawfeed.index(rawline)
            datajump = 1
            full_header = True
            comma = True
            break
        if len(line) < 2 or line[0] == '':
            continue
        subtag[line[0]] = line[1]
        
    header = rawfeed[dataspot - 1].split('\t')
    last_col = 0
    while header[-1] == '':
        header = header[:-1]
        last_col += 1
    data = []
    for line in rawfeed[dataspot + datajump:]:
        splitline = line[:-last_col].split('\t')
        if splitline[-1] == '':
            continue
        data.append(splitline)
        #data.append(line[:-last_col].split('\t'))
    if len(data) == 0:
        return [12, tag, columns_raw, columns_common]
    data = sp.array(data)
    linelens = sp.array(map(len, data))
    good = linelens == max(linelens)
    data_g = data[good]
    if len(data_g) == 0:
        return [13, tag, columns_raw, columns_common]
    datacols = sp.transpose(data_g)
    first_timestamp = data[0][0]
    date, time = first_timestamp.split(' ')
    tag = {'device':'Pfeifer Prisma', 'mode':'MID recording'}
    tag['date'] = date
    tag['time'] = time

    hrs, mins, secs = map(int, time.split(':'))
    start_seconds = float(secs + 60 * (mins + 60 * hrs))

    col_index = {}
    sub_index = []
    for i in range(len(header)):
        sub_index.append(i)
        if header[i] != '':
            mass = int(header[i])
            col_index[mass] = sub_index
            sub_index = []

    columns_raw = {}
    for mass in col_index.keys():
        i1, i2, i3 = col_index[mass]
        if comma:
            for subi in range(len(datacols[i2])):
                datacols[i2][subi] = datacols[i2][subi].replace(',', '.')
                datacols[i3][subi] = datacols[i3][subi].replace(',', '.')
        columns_raw[mass] = {'timestamp': datacols[i1],
                             'seconds': sp.array(map(float,datacols[i2])),
                             'intensity': sp.array(map(float,datacols[i3]))}
        columns_raw[mass]['hours'] = (columns_raw[mass]['seconds'] + start_seconds)/3600

    columns_common = {}
    mass1 = col_index.keys()[0]
    columns_common['time'] = columns_raw[mass1]['seconds']
    columns_common['hours'] = columns_raw[mass1]['hours']
    for mass in columns_raw.keys():
        columns_common[mass] = columns_raw[mass]['intensity']

    return [0, tag, columns_raw, columns_common]
