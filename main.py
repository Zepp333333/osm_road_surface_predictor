from coord_tools import sample_bbox
from public_traces import GPX, PublicTracesApi

api = PublicTracesApi()

if __name__ == "__main__":
    gpx_list = []
    for gpx_page in api.query_with_pagination(f"trackpoints?bbox={sample_bbox}"):
        gpx_list.extend(GPX.extract_list_of_gpx_from_xml(gpx_page))
