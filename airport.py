"""
(In Python 3)
"""

import urllib.request
import math
import datetime

def get_taf(icao):
    ''' (str)-> str

    Return an airport's unencoded terminal aerodrome forecast (TAF) retrieved
    from the NOAA government ftp server.

    Precondition: icao is a valid four letter ICAO identifier in uppercase

    >>> get_taf('EBCV')
    [b'2012/11/18 19:45\n', b'TAF EBCV 181541Z 1819/1907 10002KT 9999 FEW017
    SCT030 \n', b'      TEMPO 1819/1902 5000 BR SCT012 \n', b'      TEMPO
    1821/1907 3000 BR \n', b'      TEMPO 1902/1907 0500 FG BKN001 BY EBWM\n']
    '''

    urlStr = 'ftp://tgftp.nws.noaa.gov/data/forecasts/taf/stations/' + icao + '.TXT'

    try:
        fileHandle = urllib.request.urlopen(urlStr)
        taf = fileHandle.readlines()
        fileHandle.close()
    except IOError:
        print('Cannot open URL %s for reading' % urlStr)
        taf = 'error'

    return taf 

def get_shorttaf(icao):
    ''' (str)-> str

    Return an airport's unencoded short terminal aerodrome forecast (TAF)
    retrieved from the NOAA government ftp server.

    Precondition: icao is a valid four letter ICAO identifier in uppercase

    >>> get_shorttaf('EBCV')
    [b'2012/11/19 13:51\n', b'TAF TAF EBCV 191141Z 1913/1922 19008KT 5000 BR
    SCT008 BKN012 \n', b'      TEMPO 1913/1919 7000 FEW010 BKN015 PROB40 \n',
    b'      TEMPO 1919/1922 4000 BR BKN009 BY EBWM\n']
    '''

    urlStr = 'ftp://tgftp.nws.noaa.gov/data/forecasts/shorttaf/stations/' + icao + '.TXT'

    try:
        fileHandle = urllib.request.urlopen(urlStr)
        shorttaf = fileHandle.readlines()
        fileHandle.close()
    except IOError:
        print('Cannot open URL %s for reading' % urlStr)
        shorttaf = 'error'

    return shorttaf 

def get_metar(icao):
    ''' (str)-> str

    Return an airport's unencoded meteorological aviation routine (METAR) report
    retrieved from the NOAA government ftp server.

    Precondition: icao is a valid four letter ICAO identifier in uppercase

    >>> get_metar('EBCV')
    b'2012/11/06 08:38\nEBCV 060838Z VRB03KT 5000 BR SCT030 BKN040 03/03 Q1019 WHT\n'
    '''

    urlStr = 'ftp://tgftp.nws.noaa.gov/data/observations/metar/stations/' + icao + '.TXT'

    try:
        fileHandle = urllib.request.urlopen(urlStr)
        metar = fileHandle.read()
        fileHandle.close()
    except IOError:
        print('Cannot open URL %s for reading' % urlStr)
        metar = 'error'

    return metar

def read_airport_data(airport_file):
    ''' (file open for reading) -> dict of {str: ; list of str}

    Read the data from airport_file and return a dictionary where
    each key is the airports ICAO identifier and each value is a list containing
    strings representing latitude,longitude, destination ceiling and visibilities,
    (no alt) ceiling and visibilities and the min ceiling and visibilities needed
    to use as an alternate.

    Precondition: airport_file starts with a header that contains no blank lines,
    then has a blank line, and then lines containing an ICAO identifier, name,
    latitude, longitude, destination ceiling, destination visibility, no alternate
    ceiling, no alternate visibility, alternate ceiling and alternate visibility.

    >>> read_airport_data(airport_file)
    {'EBCV': ['Chievres', '50.583333', '3.833333', '200', '400', '600', '2000',
    '600', '2000'], 'EDDK': ['Cologne', '50.878365', '7.1222224', '200', '400',
    '600', '2000', '600', '2000']}
    '''

    # Skip over the header.
    line = airport_file.readline()
    while line != '\n':
        line = airport_file.readline()

    # Read the data, accumulating them in a dict.
    airport_data = {}
    for line in airport_file:
        try:
            icao, name, lat, lon, dest_ceil, dest_vis,\
            noAlt_ceil, noAlt_vis, alt_ceil, alt_vis = line.strip().split(",")
            data = {icao: [float(lat), float(lon)]}
            if icao not in airport_data:
                airport_data[icao] = [name, lat, lon, dest_ceil, dest_vis,\
                                      noAlt_ceil, noAlt_vis, alt_ceil, alt_vis]
            else:
                airport_data[icao].append(name, lat, lon, dest_ceil, dest_vis,\
                                          noAlt_ceil, noAlt_vis, alt_ceil, alt_vis)
        except ValueError:
            pass

    return airport_data

def compute_distance_latlon(lat1, lon1, lat2, lon2):
    ''' (float, float, float, float) -> float

    Returns distance in nautical miles given the latitude and longitude of any
    two points in degrees.

    >>> compute_distance_latlon(50.583333, 3.833333, 50.89.717, 4.483602)
    31.072563198536763
    '''

    # Convert degrees to radians
    lat1 = lat1 * math.pi / 180 
    lon1 = lon1 * math.pi / 180
    lat2 = lat2 * math.pi / 180
    lon2 = lon2 * math.pi / 180
    
    # Distance formula from: williams.best.vwh.net/avform.htm#Dist
    distance = math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) *\
                     math.cos(lat2) * math.cos(lon1-lon2)) * 6371 *\
                     0.5399568 # Look this up later
       
    return distance

def compute_distance_icao(icao1, icao2, data):
    ''' (str, str, dict) -> float

    Return distance in nautical miles given the icao identifiers of two airports
    and the airport data dictionary.

    >>> compute_distance_icao('EBCV', 'EBBR', data)
    31.072563198536763
    '''

    lat1 = float(data[icao1][1])
    lon1 = float(data[icao1][2])
    lat2 = float(data[icao2][1])
    lon2 = float(data[icao2][2])

    distance = compute_distance_latlon(lat1, lon1, lat2, lon2)
    return distance

def process_file(filename):
    ''' (str) -> dict

    Returns a dictionary containing data read from a file. First opens
    the file, then passes it to read_aiport_data() to build the dictionary,
    then closes the file.

    >>> process_file('airport_data.csv')
    {'ETIH': ['Illesheim', '49.466667', '10.383333', '400', '1600',
    '1500', '3200', '1500', '3200']}
    '''

    input_file = open(filename, 'r')
    data = read_airport_data(input_file)
    input_file.close()
    return data

def process_line(line):
    ''' (bytes) -> str

    Returns the TAF/METAR line converted from bytes to str and strips off
    lead and trail whitespace.

    >>>process_line(b'      AMDS AFT 2710 NEXT 2804\n')
    'AMDS AFT 2710 NEXT 2804'
    '''

    #line = str(line.strip()).strip("b'") or even better
    line = bytes.decode(line).strip()
    return line

def get_datetime(line):
    ''' (str) -> datetime.datetime

    Returns a date and time

    >>> get_time('2012/11/27 10:54')
    datetime.datetime(2012, 11, 27, 10, 54)
    '''

    year   = int(line[:4])
    month  = int(line[5:7])
    day    = int(line[8:10])
    hour   = int(line[11:13])
    minute = int(line[14:16])

    date_time = datetime.datetime(year, month, day, hour, minute)
    return date_time

def get_latest_report(icao):
    ''' (str) -> list

    Return the most current report after comparing the short and long tafs.

    >>> get_latest_report('KPWM')
    [b'2012/11/27 18:45\n', b'TAF KPWM 271739Z 2718/2818 VRB05KT P6SM OVC050\n']
    '''

    taf = get_taf(icao)
    shorttaf = get_shorttaf(icao)
    
    if taf == 'error':
        return shorttaf
    elif shorttaf == 'error':
        return taf
    elif taf[0] > shorttaf[0]:
        return taf
    else:
        return shorttaf

def search_string(string):
    ''' (str) -> str

    Returns a time interval in date/time format

    >>> search_string('b'TAF TAF EBCV 051615Z 0519/0607 30005KT 8000 BKN015 \n')
    0519/0607
    '''

    place = 0
    for i in string:
        if i == '/':
            place = i
    group = string[i+11:i+20]

    return group

    
