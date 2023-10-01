"""
https://wiki.openstreetmap.org/wiki/API_v0.6#GPS_traces
"""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Generator

import gpxpy
from geopy.distance import geodesic
from gpxpy.gpx import GPX, GPXTrack, GPXTrackSegment
from OSMPythonTools.api import Api

from coord_tools import BBox

MIN_TRACK_POINTS = 10


class PublicTracesApi(Api):  # fixme - convert to async
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

    async def query_with_pagination(
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


class AsDictMixin:
    def as_dict(self):
        return asdict(self)


@dataclass
class TrackPoint(AsDictMixin):
    lat: float
    lon: float
    time: datetime
    speed_kph: float | None = None


@dataclass
class TrackSegment(AsDictMixin):
    track_points: list[TrackPoint]


@dataclass
class Track(AsDictMixin):
    name: str
    desc: str
    url: str
    track_segments: list[TrackSegment]
    average_speed_kph: float | None = None
    track_max_speed_kph: float | None = None


class GPXTrace:
    def __init__(self, gpx_pages: list[str], bbox: BBox) -> None:
        self.bbox = bbox
        self.gpxs = [gpxpy.parse(gpx_str) for gpx_str in gpx_pages]

        pre_processed_tracks = []
        for gpx in self.gpxs:
            for track in gpx.tracks:
                pre_processed_tracks.append(self.convert_gpx_to_track(track))

        processed_tracks = self.remove_invalid_tracks(pre_processed_tracks)
        processed_tracks_with_speed = [
            self.add_speed_to_track(track) for track in processed_tracks
        ]

        self.tracks = [
            self.add_avg_max_speed_to_track(track)
            for track in processed_tracks_with_speed
        ]

    @staticmethod
    def remove_invalid_tracks(tracks: list[Track]) -> list[Track]:
        """remove tracks which points do not have time or too few points"""
        valid_tracks = []
        for track in tracks:
            for segment in track.track_segments:
                if (
                    all([point.time for point in segment.track_points])
                    and len(segment.track_points) >= MIN_TRACK_POINTS
                ):
                    valid_tracks.append(track)
        return valid_tracks

    @staticmethod
    def build_track_segment(segment: GPXTrackSegment) -> TrackSegment:
        return TrackSegment(
            [
                TrackPoint(point.latitude, point.longitude, point.time)
                for point in segment.points
            ]
        )

    def add_speed_to_track(self, track: Track) -> Track:
        for segment in track.track_segments:
            for i in range(len(segment.track_points)):
                if i == 0:
                    continue

                curr_point = segment.track_points[i]
                prev_point = segment.track_points[i - 1]

                speed = self.calculate_speed_between_to_points(
                    curr_point=curr_point, prev_point=prev_point
                )

                curr_point.speed_kph = speed

            # assume that the first point has the same speed as the second point
            try:
                segment.track_points[0].speed_kph = segment.track_points[1].speed_kph
            except IndexError:
                pass

        return track

    @staticmethod
    def calculate_speed_between_to_points(
        curr_point: TrackPoint, prev_point: TrackPoint
    ) -> float:
        curr_coord = (curr_point.lat, curr_point.lon)
        prev_coord = (prev_point.lat, prev_point.lon)
        curr_time = curr_point.time.replace(tzinfo=timezone.utc)
        prev_time = prev_point.time.replace(tzinfo=timezone.utc)
        distance = geodesic(curr_coord, prev_coord).meters  # distance in meters
        time_delta = (
            curr_time - prev_time
        ).total_seconds()  # time difference in seconds
        if time_delta == 0:
            return 0.0
        speed = (distance / time_delta) * 3.6  # speed in km/h
        return speed

    @staticmethod
    def add_avg_max_speed_to_track(track_with_speed: Track) -> Track:
        total_speed = 0.0
        total_points = 0
        max_speed = 0.0

        for segment in track_with_speed.track_segments:
            for point in segment.track_points:
                total_speed += point.speed_kph or 0.0
                total_points += 1
                max_speed = max(max_speed, point.speed_kph or 0.0)

        average_speed = total_speed / total_points if total_points > 0 else 0.0

        track_with_speed.average_speed_kph = average_speed
        track_with_speed.track_max_speed_kph = max_speed
        return track_with_speed

    def convert_gpx_to_track(self, gpx_track: GPXTrack) -> Track:
        return Track(
            name=gpx_track.name,
            desc=gpx_track.description,
            url=gpx_track.link,
            track_segments=[
                self.build_track_segment(segment) for segment in gpx_track.segments
            ],
        )


public_traces_api = PublicTracesApi()
