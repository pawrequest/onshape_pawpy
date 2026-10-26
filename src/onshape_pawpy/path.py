import re
from typing import Literal, NamedTuple

from onshape_pawpy.api.exceptions import OnshapePathError

ONSHAPE_VIEW_KIND = Literal['w', 'v', 'm']


ONSHAPE_PATH_PARAMS_REGEX = re.compile(
    r'/documents/(?P<doc_id>[0-9a-f]+)/(?P<kind>[wvm])/(?P<kind_id>[0-9a-f]+)/e/(?P<element_id>[0-9a-f]+)'
)


class OnshapeIds(NamedTuple):
    """IDs parsed from an Onshape document URL."""

    did: str  # document ID
    wvm: str  # 'w' (workspace), 'v' (version), or 'm' (microversion)
    wvmid: str  # workspace / version / microversion ID
    eid: str | None = None  # element ID

    @classmethod
    def from_url(cls, url: str, **kwargs):
        match = ONSHAPE_PATH_PARAMS_REGEX.search(url.strip())
        if not match:
            raise ValueError(f'Not a valid Onshape element URL: {url!r}')
        from_url = match.groups()
        return cls(*from_url, **kwargs)

    def get_ps_parts(self):
        return rf'/parts/d/{self.did}/{self.wvm}/{self.wvmid}'

    def get_export(self, export_type: str = 'stl'):
        if not self.eid:
            raise OnshapePathError('element_id is required for export')
        return rf'/partstudios/d/{self.did}/{self.wvm}/{self.wvmid}/e/{self.eid}/{export_type}'
