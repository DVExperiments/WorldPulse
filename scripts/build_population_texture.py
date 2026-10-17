#!/usr/bin/env python3
"""One-time WorldPop raster fetch -> static globe brightness texture.

The generated PNG has a global 2:1 equirectangular extent and contains
log-scaled WorldPop population density. All calculations happen at build time,
never in a visitor's browser. A failed download is a hard error: no synthetic
raster is created or committed.
"""
from __future__ import annotations
import io
import json
import math
from pathlib import Path
import requests
import numpy as np
from PIL import Image
from rasterio.io import MemoryFile

SERVICE = 'https://worldpop.arcgis.com/arcgis/rest/services/WorldPop_Population_Density_1km/ImageServer/exportImage'
# WorldPop's global 1 km population-density ImageServer: 2000-2020; 2020 selected.
# Source coverage ends around latitude 83.63 N / -59.49 S.
BOUND = (-180.0, -59.48, 179.99, 83.62)
SIZE = (2048, 814)
OUTPUT_SIZE = (1440, 720)
OUT = Path('assets/population-density.png')
INFO = Path('assets/population-density-info.json')

def normalize_density(density):
    """Log-normalise persons/km². Zero populations remain black."""
    values = np.asarray(density, dtype=np.float32)
    values = np.where(np.isfinite(values) & (values > 0), values, 0)
    # 10,000 people per km² is fully illuminated; use smooth log response.
    return np.uint8(np.clip(np.log1p(values) / math.log1p(10000) * 255, 0, 255))

def fetch():
    params = {
        'bbox': ','.join(map(str,BOUND)), 'bboxSR': '4326',
        'imageSR': '4326','size': ','.join(map(str,SIZE)),
        'format': 'tiff','pixelType': 'F32',
        'time':'1577836800000', 'f':'image'
    }
    with requests.Session() as session:
        resp = session.get(SERVICE,params=params,timeout=150,headers={'User-Agent':'WorldPulse-GeoVisualization/1.6C.3'})
        resp.raise_for_status()
        if not (resp.content[:4] in [b'II*\x00', b'MM\x00*',b'II+\x00',b'MM\x00+']):
            raise ValueError(f'Expected TIFF data, got {resp.headers.get("content-type")} {resp.text[:200]!r}')
        with MemoryFile(resp.content) as mem:
            with mem.open() as ds:
                if ds.count != 1 or not ds.dtypes[0].startswith('float'):
                    raise ValueError(f'Expected single-band floating-point density raster; received {ds.count} bands, {ds.dtypes}')
                data=ds.read(1,masked=True).filled(0).astype(np.float32)
                print('Source raster:',data.shape, 'bands=',ds.count,'pixel type=',ds.dtypes)
                if np.count_nonzero(data > 0) < 1000 or np.nanmax(data) < 1:
                    raise ValueError('WorldPop raster has insufficient usable measurements; refusing to publish misleading image')
                return data

def build():
    data = fetch()
    encoded = normalize_density(data)
    # TIFF pixels cover BOUND. Place them in the matching world lat/lon position.
    tex = Image.new('L', OUTPUT_SIZE, 0)
    width,height=OUTPUT_SIZE
    x0=round((BOUND[0]+180)/360*width)
    x1=round((BOUND[2]+180)/360*width)
    y0=round((90-BOUND[3])/180*height)
    y1=round((90-BOUND[1])/180*height)
    roi=Image.fromarray(encoded,'L').resize((x1-x0,y1-y0),Image.Resampling.BILINEAR)
    tex.paste(roi,(x0,y0))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    tex.save(OUT,optimize=True)
    meta = {
        'source':'WorldPop 1km population density 2020',
        'source_url':'https://worldpop.arcgis.com/arcgis/rest/services/WorldPop_Population_Density_1km/ImageServer',
        'citation':'WorldPop et al. (2018), Global High Resolution Population Denominators Project, dataset year 2020, DOI: 10.5258/SOTON/WP00674',
        'license':'CC BY 4.0',
        'measure':'persons per square kilometer',
        'brightness_transform':'log1p(density)/log1p(10000), clipped to [0,1]',
        'resolution':{'width':width,'height':height},
        'role':'static decorative brightness reference; not live news'
    }
    INFO.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print('Built',OUT,'size',OUT.stat().st_size, 'bytes')

if __name__ == '__main__':
    build()
