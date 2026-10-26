from typing import Any

from onshape_pawpy.client import OnshapeClient
from onshape_pawpy.request import OnshapeRequest


def get_parts(
    on_req: OnshapeRequest,
    *,
    client: OnshapeClient | None = None,
    filter_text: str = '',
    filter_case: bool = False,
) -> list[dict[str, Any]]:
    client = client or OnshapeClient()
    parts_list_path = on_req.path_params.get_ps_parts()
    res = client.get(parts_list_path, **on_req.query_params.__dict__)
    if filter_text:
        if filter_case:
            res = [_ for _ in res if filter_text in _['name']]
        else:
            res = [_ for _ in res if filter_text.lower() in _['name'].lower()]
    return res
