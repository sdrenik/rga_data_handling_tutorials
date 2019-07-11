# Module for working with intervals in time-traces of signals which do not share the same
# time column.

# Aleksander Drenik
# JSI Ljubljana, IPP Garching
# Jan 2017

import scipy as sp

version = '1.05'


# new version of borders:


def borders(inlist, step_size=1):
    """Returns pairs of lists of first and last element of ranges of consecutive integers in a list."""
    if len(inlist) == 0:
        return []
    borders = []
    b1 = inlist[0]
    for i in range(1,len(inlist)):
        if inlist[i] > inlist[i-1] + step_size:
            borders.append([b1, inlist[i -1]])
            b1 = inlist[i]
    borders.append([b1, inlist[-1]])
    return borders

   
#def borders(selected):
    """Returns pairs of lists of first and last element of ranges of consecutive integers in a list"""
    
    """selected_sh = sp.zeros(len(selected), dtype=int)
    for i in range(1,len(selected)):
        selected_sh[i] = selected[i-1]
    selected_i = sp.zeros(len(selected), dtype=int)
    for i in range(1,len(selected_i)):
        selected_i[i] = i
    
    islands = selected_i[selected - selected_sh == 1]
     
    if len(islands) > 0:
        borders=[]
        borders.append([islands[0]])
        for i in range(1,len(islands)):
            if islands[i] > islands[i-1] + 1:
                borders[-1].append(islands[i-1])
                borders.append([islands[i]])
        borders[-1].append(islands[-1])
        
        i_borders = []
        for pair in borders:
            i_borders.append([selected[pair[0]],selected[pair[1]]])
    
        return i_borders
    else:
        return []"""
        
def islands(in_list, low, high=None):
    """Returns indexes of values between low and high (optional) borders. in_list must be scipy array"""
    if len(in_list)==0:
        return []
    if high == None:
        high = max(in_list)
    i_list = sp.zeros(len(in_list), dtype=int)
    for i in range (0,len(i_list)):
        i_list[i] = i
        
    selected = i_list[(in_list >= low) * (in_list <= high)]
    return borders(selected)

def islands_to_intervals(tcol,islands):
    """Translate index-written intervals into time-written intervals"""
    intervals = []
    for island in islands:
        intervals.append([tcol[island[0]],tcol[island[1]]])
    return intervals

def make_intervals(tcol, ycol, low, high=None):
    """wrapper function for islands and islands_to_intervals.
    Returns x-axis intervals where y-value of signal is greater than low and lesser than high if high is specified."""
    isl = islands(ycol, low, high)
    ivls = islands_to_intervals(tcol, isl)
    return ivls
    
def hysteresis(tcol, ycol, lim_on, lim_off):
    """wrapper function for islands, islands_to_intervals and IntervalHysteresis.
    Returns x-axis intervals where y-value of signal is greater than lim_on going up and lim_off going down."""
    a1 = make_intervals(tcol, ycol, lim_on)
    a2 = make_intervals(tcol, ycol, lim_off)

    hy = IntervalHysteresis(a1, a2)
    
    return hy
    
#Below defined are functions for processing intervals
#Intervals are in the forms of lists [....,[t1,t2],....]
#Where t1 and t2 are the beginning and the end of an interval
    
def IntervalIntersection(t,q):
    """Returns cross section of intervals in t and q"""
    a = []
    for pair in t:
        t1 = pair[0]
        t2 = pair[1]
        
        for pair2 in q:
            q1 = pair2[0]
            q2 = pair2[1]
            
            if (q1 < t2) and (q2 > t1):
                a1 = max(q1,t1)
                a2 = min(q2,t2)
                a.append([a1,a2])
    return a
    
def IntervalHysteresis(t,q):
    """Returns overlapping intervals with start values from t and end values from q"""
    a = []
    for pair in t:
        t1 = pair[0]
        t2 = pair[1]
        
        for pair2 in q:
            q1 = pair2[0]
            q2 = pair2[1]
            
            if (q1 < t2) and (q2 > t1):
                a1 = max(q1,t1)
                a2 = max(q2,t2)
                a.append([a1,a2])
    return a

def IntervalCleanup(b):
    """ Combines adjacent and/or overlapping intervals"""
    if len(b) <= 1:
        return b
    a = []
    a1, a2 = b[0]
    remainder = b[1:]
    while len(remainder) > 0:
        removeme=[]
        for pair in remainder:       
            q1 = pair[0]
            q2 = pair[1]
            if (q1 <= a2) and (q2 >= a1):
                a1 = min(q1,a1)
                a2 = max(q2,a2)
                removeme.append(pair)
        for pair in removeme:
            remainder.remove(pair)
        a.append([a1,a2])
        if len(remainder) > 0:
            a1, a2 = remainder[0]
            remainder = remainder[1:]
    if [a1,a2]!=a[-1]:
        a.append([a1,a2])
    return a
    
def JoinIntervals(a, step_size):
    """Merges intervals which are less than step_size apart"""
    b = [a[0]]
    for i in range(1, len(a)):
        if a[i][0] - b[-1][1] < step_size:
            b[-1][1] = a[i][1]
        else:
            b.append(a[i])
    return b

def InvertIntervals(a, frame=None):
    """Returns intervals outside of input interval. Frame sets start and stop time of intervals"""
    outint = []
    
    if len(a) == 0:
        if frame != None:
            return [frame]
        else:
            return a
    
    if frame != None:
        
        if frame[0] < a[0][0]:
            outint = [[frame[0], a[0][0]]]
    
    for i in range(1, len(a)):
        outint.append([a[i - 1][1], a[i][0]])
    
    if frame != None:
        if frame[1] > a[-1][1]:
            outint.append([a[-1][1], frame[1]])
    
    return outint
    
def IntervalDifference(a, b):
    """Returns intervals of a which do not overlap with intervals of b"""
    #if a == [[]] and b == [[]]:
    #    return [[]]
    #elif a == [[]]:
    #    return b
    #elif b == [[]]:
    #    return a
        
    try:
        frame = [min(a[0][0], b[0][0]), max(a[-1][1],b[-1][1])]
        b_inv = InvertIntervals(b, frame)
    except IndexError:
        b_inv = InvertIntervals(b)
    return IntervalIntersection(a, b_inv)
    

def focus(x_list, y_list, area):
    """returns x and y columns where x is within defined area"""
    
    x_col = sp.array(x_list)
    y_col = sp.array(y_list)
    
    selection = (x_col >= area[0]) * (x_col <= area[1])
    
    return x_col[selection], y_col[selection]
    
def pin_point(input_list, sought_value):
    """In input_list, finds nearest value to sought_value and returns its index."""
    input_col = sp.array(input_list)
    temp_list = list(map(abs, input_col - sought_value))
    nearest_index = temp_list.index(min(temp_list))
    return nearest_index
