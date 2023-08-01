from typing import Optional

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from coord_tools import BBox, find_bbox_center, sample_bbox
from public_traces import GPX, public_traces_api

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
    gpx_list = []
    for gpx_page in public_traces_api.query_with_pagination(f"trackpoints?bbox={bbox}"):
        gpx_list.extend(GPX.list_of_gpx_from_xml(gpx_page))
    print(gpx_list)
    return [track.as_dict() for track in gpx_list]
