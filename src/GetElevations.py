#! /usr/bin/python
# ======================================#
# -- coding: utf-8 --                   #
# ======================================#
# Author: João Paulo Cardoso do Carmo   #
# Date: 2025-10-24                      #
# ======================================#
import geopandas as gpd
import pandas as pd
import rasterio
import os

class GetElevations:
    def __init__(self, srtm_reference: gpd.GeoDataFrame, coords: gpd.GeoDataFrame, images_folder: str):
        """
        Main class to retrieve elevation values for given coordinates based on SRTM raster data.

        Args:
            srtm_reference (gpd.GeoDataFrame): GeoDataFrame containing SRTM grid polygons.
            coords (gpd.GeoDataFrame): gpd.GeoDataFrame with point coordinates.
            images_folder (str): Path to folder containing raster (.hgt) files or a single raster file.
        """
        self.srtm_reference = srtm_reference
        self.images_folder = images_folder
        self.crs_degrees = 4326
        self.coords = coords
        
        self.is_dir = os.path.isdir(images_folder)

    @staticmethod
    def value_from_src(coords: list[tuple[float, float]], src: rasterio.io.DatasetReader) -> list[float]:
        """
        Extract raster values for given coordinates.

        Args:
            coords (list): List of (lon, lat) tuples.
            src (rasterio.io.DatasetReader): Raster dataset.

        Returns:
            list: List of elevation values.
        """
        return [float(val[0]) for val in src.sample(coords)]

    def get(self) -> list:
        """
        Retrieve elevation values for each coordinate.

        Behavior:
            - If `images_folder` is a directory: identify which SRTM grid contains each point.
              Then open the respective raster and sample the elevation values.
            - If `images_folder` is a file: sample all points directly from that raster.

        Returns:
            list: Elevation values in the same order as the input coordinates.
        """
        if self.is_dir:
            return self._process_directory()
        else:
            return self._process_single_raster()

    def _process_single_raster(self) -> list:
        """
        Process a single raster file for all coordinates.

        Returns:
            list: Elevation values.
        """
        if not os.path.exists(self.images_folder):
            raise FileNotFoundError(f"Raster file not found: {self.images_folder}")

        coords_list = [(geom.x, geom.y) for geom in self.coords.geometry]
        with rasterio.open(self.images_folder) as src:
            values = self.value_from_src(coords_list, src)

        return values

    def _process_directory(self) -> list:
        """
        Process multiple rasters in a directory, matching points with their containing SRTM grid.

        Returns:
            list: Elevation values in original order.
        """
        # Spatial join: assign each point to the corresponding SRTM grid
        joined = gpd.sjoin(self.coords, self.srtm_reference, how="left", predicate="within")

        # Warn about points not contained in any grid
        if joined["id"].isna().any():
            print("⚠️ Warning: Some points are not contained within any SRTM grid.")

        # Preserve original order
        joined = joined.reset_index(drop=False).rename(columns={"index": "original_index"})

        elevations = [None] * len(joined)

        # Process points grouped by grid
        for idx, subset in joined.groupby("id"):
            if pd.isna(idx):
                continue
            
            # Get raster path
            raster_path = os.path.join(self.images_folder, f"{idx}.gpkg")

            if not os.path.exists(raster_path):
                print(f"⚠️ Raster not found: {raster_path}")
                continue

            coords_list = [(geom.x, geom.y) for geom in subset.geometry]

            with rasterio.open(raster_path) as src:
                vals = self.value_from_src(coords_list, src)

            for orig_idx, val in zip(subset["original_index"], vals):
                elevations[orig_idx] = val

        return elevations
