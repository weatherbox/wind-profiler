# -*- coding: utf-8 -*-
import windprofiler
import pandas as pd
import math


def main(file, n):
    data = windprofiler.parse_wind_profiler_bufr(file)
    station = data['stations'][n]

    print station['wmo_block'] * 1000 + station['wmo_station_id']

    d = {}
    
    m = 0
    mi = 0
    for i, obs in enumerate(station['obs']):
        l = len(obs['layers'])
        if l > m:
            m = l
            mi = i
        

    base = station['obs'][mi]
    print '%d-%02d-%02d %02d:%02d' % (base['year'], base['month'], base['day'], base['hour'], base['minute'])

    h = [l['h'] for l in base['layers']]
    h.reverse()

    for obs in station['obs']:
        ldata = ['-'] * m
        for i, layer in enumerate(obs['layers']):
            if layer['quality'] == 'ok':
                w = get_wind_dir_speed(layer['u'], layer['v'])
                wstr = '%d / %.1f' % (int(w[0]), w[1])
                ldata[i] = wstr

        ldata.reverse()
        d[str(obs['minute'])] = ldata

    df = pd.DataFrame(d, index=h)
    print df

def get_wind_dir(u, v):
    wdir = math.pi / 2 - math.atan2(-v, -u)
    if wdir < 0: wdir += 2 * math.pi
    return math.degrees(wdir)

def get_wind_speed(u, v):
    return math.sqrt(u * u + v * v)

def get_wind_dir_speed(u, v):
    return get_wind_dir(u, v), get_wind_speed(u,v)

if __name__ == '__main__':
    import sys
    main(sys.argv[1], int(sys.argv[2]))


