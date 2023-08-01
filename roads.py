from dataclasses import dataclass

from OSMPythonTools.overpass import Overpass, overpassQueryBuilder


@dataclass
class BBox:
    min_long: float
    min_lat: float
    max_long: float
    max_lat: float


def download_roads(bbox: BBox):
    overpass = Overpass()
    query = overpassQueryBuilder(
        bbox=[bbox.min_lat, bbox.min_long, bbox.max_lat, bbox.max_long],
        elementType=["way", "relation"],
        selector=[
            '~"highway"~"motorway|trunk|primary|secondary|tertiary|residential|cycleway"'
        ],
        out="body",
    )
    return overpass.query(query)
