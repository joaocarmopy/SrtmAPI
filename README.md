
---

# SRTM Elevation API - PYAgro

**Author:** João Paulo Cardoso do Carmo
**Date:** 2025-09-24

This project provides a REST API and a command-line interface (CLI) to query elevations from geographic coordinates using 30-meter SRTM (Shuttle Radar Topography Mission) data.

---

## Features

* REST API to get elevations for points (JSON with `"geometry": []`).
* CLI support for local processing of coordinate files.
* Flexible usage: run as CLI or enable API with a flag.

---

## Requirements

* Python 3.10+
* FastAPI
* Uvicorn
* Other dependencies as required (`rasterio`, `geopandas`, etc.)

Install basic dependencies:

```bash
pip install requeriments.txt
```

---

## Usage

### 1. Running as API

Activate the `--api` flag to start the FastAPI server:

```bash
python main.py --api
```

The server will be available at:

```
https://srtmapi.onrender.com
```

#### API Endpoint

```
POST /pyagro_elevations
```

**Expected JSON payload:**

```json
{
  "geometry": [
    [-47.9292, -15.7801],
    [-46.6333, -23.5505]
  ]
}
```

**Example response:**

```json
{
  "elevations": [1160, 760]
}
```

#### Example request with Python `requests`:

```python
import requests

url = "https://srtmapi.onrender.com/pyagro_elevations"

payload = {
    "geometry": [
        [-47.9292, -15.7801],
        [-46.6333, -23.5505]
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

---

### 2. Running via CLI

Without the `--api` flag, the script works as a CLI:

```bash
python main.py --coords_path path/to/coordinates.geojson --output_path path/to/output
```

* `--coords_path` or `-cp`: path to a file containing coordinates in the same `"geometry": []` format.
* `--output_path` or `-op`: path to save the output.


---

## Notes

* Only accepts JSON with `"geometry": []`. No `FeatureCollection` in API.
* Works for both single and multiple points.
* Coordinates just in EPSG:4326.
* API just to Brazil.
---
AGRI IS TECH, AGRI IS TOP, AGRI IS PYAGRO

Instagram @pYAgro_

---

