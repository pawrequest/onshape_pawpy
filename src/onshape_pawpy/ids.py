from typing import NamedTuple

from onshape_sdk import build_wvm_path, parse_onshape_url


class OnshapeIds(NamedTuple):
    """IDs parsed from an Onshape document URL."""

    did: str  # document ID
    wvm_type: str  # 'w' (workspace), 'v' (version), or 'm' (microversion)
    wvm_id: str  # workspace / version / microversion ID
    eid: str | None = None  # element ID

    @classmethod
    def from_url(cls, url: str) -> 'OnshapeIds':
        parsed = parse_onshape_url(url)
        return cls(**parsed)

    def build_path(self):
        return build_wvm_path(*self)


class OnshapePathTup(OnshapeIds):
    prefix: str = ''
    suffix: str = ''
