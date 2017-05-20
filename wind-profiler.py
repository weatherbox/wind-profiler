# -*- coding: utf-8 -*-
import struct
from bitarray import bitarray

def parse_wind_profiler_bufr(file):
    '''
    Wind Profiler BUFR
    http://www.data.jma.go.jp/add/suishin/jyouhou/pdf/97.pdf
    '''
    data = {}

    with open(file, 'rb') as fileptr:
        data['header'] = parse_header(fileptr)
        fileptr.seek(8, 1)  # section 0
        fileptr.seek(18, 1) # section 1
        fileptr.seek(56, 1) # section 3

        parse_section4(fileptr, data)

    return data

def parse_header(fileptr):
    return fileptr.read(18)


def parse_section4(fileptr, data):
    fileptr.seek(4, 1)
    packed_data = fileptr.read() 

    bits = bitarray()
    bits.frombytes(packed_data)

    pos = 0
    parse_station(bits, pos)


def parse_station(bits, pos):
    print readint(bits, pos, 7)


def readint(bits, pos, length):
    return toint(bits[pos : pos + length])

def toint(bits):
    return reduce(lambda x, y: x << 1 | y, bits.tolist())



if __name__ == '__main__':
    import sys
    print parse_wind_profiler_bufr(sys.argv[1])

