from typing import Dict, List

from pymongo import GEOSPHERE, MongoClient

from coord_tools import BBox
from public_traces import GPX


class GPXStorage:
    def __init__(self, dbname="public_traces", collection_name="gpx_tracks"):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client[dbname]
        self.collection = self.db[collection_name]
        self.collection.create_index([("bbox", GEOSPHERE)])

    def store_gpx(self, bbox: BBox, gpx: GPX):
        gpx_dict = gpx.as_dict()
        gpx_dict["bbox"] = {
            "type": "Polygon",
            "coordinates": [
                [
                    [bbox.min_long, bbox.min_lat],
                    [bbox.max_long, bbox.min_lat],
                    [bbox.max_long, bbox.max_lat],
                    [bbox.min_long, bbox.max_lat],
                    [bbox.min_long, bbox.min_lat],
                ]
            ],
        }
        self.collection.insert_one(gpx_dict)

    def query_gpx(self, bbox: BBox) -> List[Dict]:
        bbox_polygon = {
            "type": "Polygon",
            "coordinates": [
                [
                    [bbox.min_long, bbox.min_lat],
                    [bbox.max_long, bbox.min_lat],
                    [bbox.max_long, bbox.max_lat],
                    [bbox.min_long, bbox.max_lat],
                    [bbox.min_long, bbox.min_lat],
                ]
            ],
        }
        return list(
            self.collection.find(
                {"bbox": {"$geoIntersects": {"$geometry": bbox_polygon}}}
            )
        )

    def query_gpx_strict(self, bbox: BBox) -> List[Dict]:  # fixme
        bbox_polygon = {
            "type": "Polygon",
            "coordinates": [
                [
                    [bbox.min_long, bbox.min_lat],
                    [bbox.max_long, bbox.min_lat],
                    [bbox.max_long, bbox.max_lat],
                    [bbox.min_long, bbox.max_lat],
                    [bbox.min_long, bbox.min_lat],
                ]
            ],
        }
        results = list(
            self.collection.find({"bbox": {"$geoWithin": {"$geometry": bbox_polygon}}})
        )

        results = [r for r in results if self._bbox_equal(r["bbox"], bbox_polygon)]

        return results

    def _bbox_equal(self, bbox1: Dict, bbox2: Dict, epsilon: float = 0.1) -> bool:
        return all(
            abs(bbox1["coordinates"][0][i][0] - bbox2["coordinates"][0][i][0]) < epsilon
            and abs(bbox1["coordinates"][0][i][1] - bbox2["coordinates"][0][i][1])
            < epsilon
            for i in range(4)
        )
