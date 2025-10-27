#! /usr/bin/python

# ======================================#
# -- coding: utf-8 --                   #
# ======================================#
# Author:                               #
# João Paulo Cardoso do Carmo           #
# Date: 2025-09-24                      #
# ======================================#

# ============== Imports ==============#
from shapely.geometry import Point
from typing import Literal, Union
import geopandas as gpd
import pandas as pd
import json

class LoadGeo():
    def __init__(self, file_path:str, crs_degress:int=4326):
        self.type = None
        self.file_path = file_path
        self.crs_degress = crs_degress

    def just_read(self)->object:
        """Just read file

        Returns:
            object: The data read from the file.
        """
        if self.file_path.endswith((".geojson", ".shp", ".gpkg")):
            self.type = "vector"
            return gpd.read_file(self.file_path)
        elif self.file_path.endswith(".parquet"):
            self.type = "vector"
            return gpd.read_parquet(self.file_path)
        elif self.file_path.endswith(".xlsx"):
            self.type = "vector"
            return pd.read_excel(self.file_path)
        elif self.file_path.endswith(".csv"):
            self.type = "vector"
            return pd.read_csv(self.file_path)  
        elif self.file_path.endswith(".json"):
            self.type = "vector"
            with open(self.file_path, 'r') as f:
                return json.load(f)
        elif self.file_path.endswith(".txt"):
            self.type = "vector"
            with open(self.file_path, 'r') as f:
                return f.read()
        else:
            raise ValueError("Unsupported file format.")
    
    def find_utm(self, point_gframe:Union[tuple, gpd.GeoDataFrame])->int:
        """Find utm crs, with point or geodataframe in degress

        Args:
            point_gframe (Union[tuple, gpd.GeoDataFrame]): Add point or geodataframe in degress

        Returns:
            int: utm value
        """
        if isinstance(point_gframe, tuple):
            shapely_point = Point(point_gframe)
            point_gframe = gpd.GeoDataFrame(geometry=[shapely_point], crs=self.crs_degress)

        return point_gframe.estimate_utm_crs()
     
    def to_crs(self, file:object, crs_type:Literal["meters", "degress"]="meters")->object:
        """Convert file crs

        Args:
            file (object): object to convert
            crs_type (Literal[utm;, degress], optional): To convert. Defaults to "meters".

        Returns:
            object: _description_
        """
        if self.type == "vector":
            # Real crs
            is_geographic = file.crs.is_geographic
            # Convert to degress
            if crs_type == "degress" and not is_geographic:
                file = file.to_crs(self.crs_degress)
            elif crs_type == "meters" and is_geographic:
                # Find utm crs
                crs_utm = self.find_utm(file)
                file = file.to_crs(crs_utm)
        
        return file
    
    def load(self, crs_type:Literal["default", "meters", "degress"]="default"):
        # Read file
        file = self.just_read()

        # Is geographic
        if crs_type != "default":
            file = self.to_crs(file, crs_type)
        
        return file