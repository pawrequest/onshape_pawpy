import re
from dataclasses import dataclass
from typing import Protocol, Literal, Self


class OnshapePathError(BaseException): ...


@dataclass
class OnshapePath:
    doc_id: str
    kind: Literal['w', 'v', 'm']
    kind_id: str
    element_id: str = ''
    export_type: str = 'stl'

    @classmethod
    def from_url(cls, url: str, **kwargs) -> Self:
        match = ONSHAPE_PATH_PARAMS_REGEX.search(url.strip())
        if not match:
            raise ValueError(f'Not a valid Onshape element URL: {url!r}')
        from_url = match.groupdict()
        return cls(**from_url, **kwargs)

    def get_ps_parts(self: OnshapePath):
        return rf'/parts/d/{self.doc_id}/{self.kind}/{self.kind_id}'

    def get_export(self: OnshapePath):
        if not self.element_id:
            raise OnshapePathError('element_id is required for export')
        return rf'/partstudios/d/{self.doc_id}/{self.kind}/{self.kind_id}/e/{self.element_id}/{self.export_type}'


ONSHAPE_PATH_PARAMS_REGEX = re.compile(
    r'/documents/(?P<doc_id>[0-9a-f]+)/(?P<kind>[wvm])/(?P<kind_id>[0-9a-f]+)/e/(?P<element_id>[0-9a-f]+)'
)
