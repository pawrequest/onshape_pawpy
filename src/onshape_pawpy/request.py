from dataclasses import dataclass, field

from onshape_pawpy.query import OnshapeQueryParams
from onshape_pawpy.path import OnshapePath


@dataclass
class OnshapeRequest:
    path_params: OnshapePath
    query_params: OnshapeQueryParams = field(default_factory=OnshapeQueryParams)
    output_name: str = 'OnshapeExport'

    @property
    def extension(self):
        return '.zip' if not self.query_params.grouping else '.stl'  # grouped =/= zipped

    @property
    def filename(self):
        return f'{self.output_name}{self.extension}'
