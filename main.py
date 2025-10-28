#! /usr/bin/python

# ======================================#
# -- coding: utf-8 --                   #
# ======================================#
# Author: João Paulo Cardoso do Carmo   #
# Date: 2025-09-24                      #
# ======================================#

# ============== Imports ==============#
from fastapi.responses import JSONResponse
from Orchestrator import Orchestrator
from fastapi import FastAPI
from time import time as t
import argparse
import warnings
import uvicorn
import os

warnings.filterwarnings("ignore")

# ============== Parser ==============#
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
no_requerid = parser.add_argument_group('No Argument requerid')
no_requerid.add_argument(
    "--api", "-api",
    action="store_true",
    required=False,
    help="Flag to activate API."
)
no_requerid.add_argument(
    "--dev", "-dev",
    action="store_true",
    required=False,
    help="Flag to activate API in mode dev."
)
no_requerid.add_argument(
    "--coords_path", "-cp",
    type=str,
    default="",
    required=False,
    help="Path with file containing coordinates."
)
no_requerid.add_argument(
    "--output_path", "-op",
    type=str,
    default="",
    required=False,
    help="Insert output path."
)

args = parser.parse_args()

# ============== Get variables ==============#
api = args.api
dev = args.dev
coords_path = args.coords_path
output_path = args.output_path

# ============== Class instance ==============#
orchestrator = Orchestrator(api=api, output_path=output_path)
# ============== FastAPI app ==============#
if api:
    app = FastAPI(title="SRTM Elevation API PYAgro")

    @app.post("/pyagro_elevations")
    async def get_elevations(file: dict):
        """
        Accepts a GeoJSON/JSON file with points, returns elevations.
        """
        try:
            elevations = orchestrator.process(file)
            return {"elevations": elevations}
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Invalid file: {str(e)}"})

# ================= CLI Execution =================#
def run_cli():
    start_time = t()
    orchestrator.process(coords_path)
    print(f"\nTime of execution {(t()-start_time)/60:.2f} minutes")

if __name__ == "__main__":
    if api:
        if dev:
            print("Starting API server on http://127.0.0.1:8000")
            uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
        else:
            port = int(os.environ.get("PORT", 8000))
            uvicorn.run("main:app", host="0.0.0.0", port=port)
    else:
        run_cli()

