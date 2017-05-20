# -*- coding: utf-8 -*-
import struct
from bitarray import bitarray
from pprint import pprint

def parse_wind_profiler_bufr(file):
    '''
    Wind Profiler BUFR
    http://www.data.jma.go.jp/add/suishin/jyouhou/pdf/97.pdf
    '''
    data = {}

    with open(file, 'rb') as fileptr:
        data['header'] = parse_header(fileptr)

        # section 0
        if fileptr.read(4) != 'BUFR':
            raise Error('cannot parse')
        fileptr.seek(4, 1)

        pass_section(fileptr) # 1
        pass_section(fileptr) # 3

        parse_section4(fileptr, data)

    return data


def parse_header(fileptr):
    return fileptr.read(18)

def pass_section(fileptr):
    head = struct.unpack('3B', fileptr.read(3))
    length = int24(head)
    fileptr.seek(length - 3, 1)


def int24(l):
    return (l[0] * 256 + l[1]) * 256 + l[2]


def parse_section4(fileptr, data):
    l = struct.unpack('4B', fileptr.read(4))
    print int24(l[0:3])
    packed_data = fileptr.read()
    bits = Bits(packed_data)

    parse_station(bits)


def parse_station(bits):
    station = {}
    station['wmo_block']      = bits.readint(7)
    station['wmo_station_id'] = bits.readint(10)
    station['lat']            = bits.readint(16)
    station['lon']            = bits.readint(15)
    station['height']         = bits.readint(15)
    station['device']         = bits.readint(4)
    station['X']              = bits.readint(8)

    station['obs'] = []
    for x in range(station['X']):
        station['obs'].append(parse_observation(bits))

    pprint(station)
    return station

def parse_observation(bits):
    obs = {}
    obs['year']     = bits.readint(12)
    obs['month']    = bits.readint(4)
    obs['day']      = bits.readint(6)
    obs['hour']     = bits.readint(5)
    obs['minute']   = bits.readint(6)
    obs['time']     = bits.readint(5)
    obs['duration'] = bits.readint(12)
    obs['Y']        = bits.readint(8)

    obs['layers'] = []
    for y in range(obs['Y']):
        obs['layers'].append(parse_layer(bits))

    return obs

def parse_layer(bits):
    layer = {}
    layer['h']       = bits.readint(15)
    layer['quality'] = bits.readint(8)
    layer['u']       = bits.readint(13)
    layer['v']       = bits.readint(13)
    layer['w']       = bits.readint(13)
    layer['s/n']     = bits.readint(8)

    return layer


class Bits():
    def __init__(self, byte):
        self.bits = bitarray()
        self.bits.frombytes(byte)
        self.pos = 0

    def readint(self, length):
        i = self.toint(self.bits[self.pos : self.pos + length])
        self.pos += length
        return i

    @staticmethod
    def toint(bits):
        #print bits
        return reduce(lambda x, y: x << 1 | y, bits.tolist())

    @staticmethod
    def tointn(bits):
        #print bits
        bitlist = bits.tolist()
        value = reduce(lambda x, y: x << 1 | y, bitlist[1:])
        if bitlist[0] == 1:
            value *= -1
        return value



if __name__ == '__main__':
    import sys
    print parse_wind_profiler_bufr(sys.argv[1])

