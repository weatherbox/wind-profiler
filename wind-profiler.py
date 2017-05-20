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
    bit_len = (int24(l[0:3]) - 4) * 8
    packed_data = fileptr.read()
    bits = Bits(packed_data)

    data['stations'] = []
    while bits.getpos() < bit_len - 16:
        data['stations'].append(parse_station(bits))


def parse_station(bits):
    station = {}
    station['wmo_block']      = bits.readint(7)
    station['wmo_station_id'] = bits.readint(10)
    station['lat']            = bufr_0_05_002(bits.readint(15))
    station['lon']            = bufr_0_06_002(bits.readint(16))
    station['height']         = bufr_0_07_001(bits.readint(15))
    station['device']         = bits.readint(4)
    station['X']              = bits.readint(8)

    station['obs'] = []
    for x in range(station['X']):
        station['obs'].append(parse_observation(bits))

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
    layer['quality'] = bufr_0_25_192(bits.readint(8))
    layer['u']       = bufr_0_11_002(bits.readint(13))
    layer['v']       = bufr_0_11_002(bits.readint(13))
    layer['w']       = bufr_0_11_006(bits.readint(13))
    layer['s/n']     = bufr_0_21_030(bits.readint(8))

    return layer


'''
BUFR Table B
http://www.wmo.int/pages/prog/www/WMOCodes/WMO306_vI2/LatestVERSION/LatestVERSION.html
'''

def bufr_0_05_002(x):
    return (x - 9000) * 0.01

def bufr_0_06_002(x):
    return (x - 18000) * 0.01

def bufr_0_07_001(x):
    return x - 400

# 0_11_003 is same
def bufr_0_11_002(x):
    return (x - 4096) * 0.1

def bufr_0_11_006(x):
    return (x - 4096) * 0.01

def bufr_0_21_030(x):
    return x - 32

def bufr_0_25_192(x):
    if x == 128:
        return 'ok'
    elif x == 256:
        return 'missing'
    else:
        return 'not good'


class Bits():
    def __init__(self, byte):
        self.bits = bitarray()
        self.bits.frombytes(byte)
        self.pos = 0

    def getpos(self):
        return self.pos

    def readint(self, length):
        i = self.toint(self.bits[self.pos : self.pos + length])
        self.pos += length
        return i

    @staticmethod
    def toint(bits):
        #print bits
        return reduce(lambda x, y: x << 1 | y, bits.tolist())



if __name__ == '__main__':
    import sys
    print parse_wind_profiler_bufr(sys.argv[1])

