"""
https://wiki.openstreetmap.org/wiki/API_v0.6#GPS_traces
"""

from datetime import datetime
from typing import Generator, List, Self
from xml.etree import ElementTree as ET

from OSMPythonTools.api import Api


class PublicTracesApi(Api):
    max_pages_to_retrieve = 5

    def _rawToResult(
        self,
        data: str,
        queryString: str,
        params: dict,
        kwargs: dict,
        cacheMetadata: dict = None,
        shallow: bool = False,
    ):
        return data

    def query_with_pagination(
        self, query_str: str, max_pages_to_retrieve: int | None = None
    ) -> Generator[str, None, None]:
        page_num = 0
        while page_num < (max_pages_to_retrieve or self.max_pages_to_retrieve):
            print(f"requesting page {page_num}")
            page_content = self.query(
                query_str + f"&page={page_num}",
            )
            if not page_content:
                break
            yield page_content
            page_num += 1


class TrackPoint:
    def __init__(self, lat: float, lon: float, time: datetime) -> None:
        self.lat = lat
        self.lon = lon
        self.time = time

    def as_dict(self) -> dict:
        return {"lat": self.lat, "lon": self.lon, "time": self.time.isoformat()}


class TrackSegment:
    def __init__(self, track_points: List[TrackPoint]) -> None:
        self.track_points = track_points

    def as_dict(self) -> dict:
        return {"track_points": [point.as_dict() for point in self.track_points]}


class GPX:
    gpx_namespace = {"gpx": "http://www.topografix.com/GPX/1/0"}

    def __init__(
        self, name: str, desc: str, url: str, track_segments: List[TrackSegment]
    ) -> None:
        self.name = name
        self.desc = desc
        self.url = url
        self.track_segments = track_segments

    @classmethod
    def from_xml(cls, trk: ET.Element) -> Self:
        name = cls.get_track_attribute(trk, "name")
        desc = cls.get_track_attribute(trk, "desc")
        url = cls.get_track_attribute(trk, "url")
        track_segments = []

        for trkseg in trk.findall("gpx:trkseg", cls.gpx_namespace):
            track_points = []

            for trkpt in trkseg.findall("gpx:trkpt", cls.gpx_namespace):
                lat = float(trkpt.get("lat"))
                lon = float(trkpt.get("lon"))
                # fixme:
                # File
                # "/Users/sergey/projects/osm_road_surface_predictor/app.py", line
                # 55, in read_gpx
                # gpx_list.extend(GPX.list_of_gpx_from_xml(gpx_page))
                # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^
                # File
                # "/Users/sergey/projects/osm_road_surface_predictor/public_traces.py", line  # noqa: E501
                # 106, in list_of_gpx_from_xml
                # gpx_list.append(cls.from_xml(trk))
                # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^
                # File
                # "/Users/sergey/projects/osm_road_surface_predictor/public_traces.py", line  # noqa: E501
                # 83, in from_xml
                # time_str = trkpt.find("gpx:time", cls.gpx_namespace).text
                # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^  # noqa: E501
                # AttributeError: 'NoneType'
                # objecthas no attribute 'text'
                time_str = trkpt.find("gpx:time", cls.gpx_namespace).text
                time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")

                track_points.append(TrackPoint(lat, lon, time))

            track_segments.append(TrackSegment(track_points))

        return cls(name, desc, url, track_segments)

    @classmethod
    def get_track_attribute(cls, trk, attribute_name: str) -> str | None:
        try:
            return trk.find("gpx:" + attribute_name, cls.gpx_namespace).text
        except AttributeError:
            return None

    @classmethod
    def list_of_gpx_from_xml(cls, xml_string: str) -> List[Self]:
        root = ET.fromstring(xml_string)

        gpx_list = []

        for trk in root.findall("gpx:trk", cls.gpx_namespace):
            gpx_list.append(cls.from_xml(trk))

        return gpx_list

    def as_dict(self):
        return {
            "name": self.name,
            "desc": self.desc,
            "url": self.url,
            "track_segments": [segment.as_dict() for segment in self.track_segments],
        }

    @staticmethod
    def point_as_dict(point: TrackPoint):
        return {"lat": point.lat, "lon": point.lon, "time": point.time.isoformat()}


public_traces_api = PublicTracesApi()
