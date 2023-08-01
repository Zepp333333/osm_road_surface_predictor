from dataclasses import dataclass


@dataclass
class BBox:
    min_long: float
    min_lat: float
    max_long: float
    max_lat: float

    def __str__(self):
        return f"{self.min_long},{self.min_lat},{self.max_long},{self.max_lat}"


def find_bbox_center(bbox: BBox) -> tuple[float, float]:
    return find_bbox_center_by_coords(
        bbox.min_long, bbox.min_lat, bbox.max_long, bbox.max_lat
    )


def find_bbox_center_by_coords(min_long, min_lat, max_long, max_lat):
    centerLong = (min_long + max_long) / 2
    centerLat = (min_lat + max_lat) / 2
    return centerLat, centerLong


sample_bbox = BBox(0, 51.5, 0.25, 51.75)
