import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from coord_tools import BBox, find_bbox_center, sample_bbox
from public_traces import GPXTrace, public_traces_api

logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,  # fixme - make stricter
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root(request: Request):
    lat, lon = find_bbox_center(sample_bbox)
    initial_coordinates = {"lat": lat, "lon": lon}
    return templates.TemplateResponse(
        "index.html", {"request": request, "initial_coordinates": initial_coordinates}
    )


@app.get("/gpx")
async def read_gpx(
    min_lat: Optional[float] = None,
    min_long: Optional[float] = None,
    max_lat: Optional[float] = None,
    max_long: Optional[float] = None,
):
    bbox = BBox(min_lat=min_lat, min_long=min_long, max_lat=max_lat, max_long=max_long)
    logger.info(f"Downloading data for area {bbox}.")
    gpx_pages = []
    async for gpx_page in public_traces_api.query_with_pagination(
        f"trackpoints?bbox={bbox}"
    ):
        gpx_pages.append(gpx_page)

    gpx = GPXTrace(gpx_pages, bbox)
    return [track.as_dict() for track in gpx.tracks]
