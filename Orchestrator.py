#! /usr/bin/python
# ======================================#
# -- coding: utf-8 --                   #
# ======================================#
# Author: João Paulo Cardoso do Carmo   #
# Date: 2025-10-24                      #
# ======================================#

from src.GetElevations import GetElevations
from shapely.geometry import Point
from src.LoadGeo import LoadGeo
from typing import Union
from pathlib import Path
import geopandas as gpd
import os

THIS_PATH = Path(__file__).parent.absolute()

class Orchestrator:
    def __init__(self, api: bool = False,  output_path: str = "", name_output: str = "elevation"):
        """
        Orchestrator to manage SRTM elevation extraction.

        Args:
            api (bool): If True, returns results directly for API.
            output_path (str): Folder to save results when api=False.
            name_output (str): Column name for elevations in output file.
        """
        self.api = api
        self.output_path = output_path
        self.name_output = name_output

        # Initialize directories
        self.srtm_path = os.path.join(THIS_PATH, "files", "SRTM.gpkg")
        self.images_folder = os.path.join(THIS_PATH, "files", "images")

        # Create output directory if needed
        if self.output_path:
            os.makedirs(self.output_path, exist_ok=True)

    def _load_data(self, coords_json:Union[str, dict]):
        """Load SRTM grid and coordinates GeoDataFrames."""
        srtm = LoadGeo(self.srtm_path).load(crs_type="degress")
        coords = None
        if isinstance(coords_json, str):
            coords = LoadGeo(coords_json).load(crs_type="degress")
        else:
            coords_dict = coords_json.get("geometry")
            coords = gpd.GeoDataFrame(geometry=[Point(tuple(xy)) for xy in coords_dict], crs=4326)
            
        if coords is None:
            raise ValueError("No coordinates provided.")
        return srtm, coords

    def _save_output(self, coords_gdf):
        """Save the coordinates with elevations to GeoJSON."""
        out_file = os.path.join(self.output_path, f"{self.name_output}.geojson")
        coords_gdf.to_file(out_file)
        print(f"Saved elevations to: {out_file}")

    def process(self, coords_json:Union[str, dict]):
        """
        Main processing method: extracts elevations and either returns them or saves output.
        """
        # Load SRTM and coordinates
        srtm, coords = self._load_data(coords_json)

        # Compute elevations
        get_elev = GetElevations(srtm, coords, self.images_folder)
        elevations = get_elev.get()

        if self.api:
            # Return elevations for API response
            return elevations
        else:
            # Save results locally
            coords[self.name_output] = elevations
            self._save_output(coords)
            return None

if __name__ == "__main__":
    coords_path = r"C:\Users\joao.carmo\Desktop\SrtmAPI\json.json"
    output_folder = r"C:\Users\joao.carmo\Desktop\SrtmAPI\output"

    orchestrator = Orchestrator(coords_json=coords_path, output_path=output_folder)
    orchestrator.process()
