import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from onshape_pawpy.client import OnshapeClient, load_dotenv

Unit = Literal['meter', 'centimeter', 'millimeter', 'inch', 'foot', 'yard']


def get_client():
    load_dotenv()
    return OnshapeClient()


@dataclass
class OnshapeQueryParams:
    units: Unit = 'millimeter'
    scale: int = 1
    grouping: bool = False
    zipped: bool | None = None

    def __post_init__(self):
        if self.zipped is not None:
            self.grouping = not self.zipped
        return self


@dataclass
class OnshapePathParams:
    doc_id: str
    kind: Literal['w', 'v', 'm']
    kind_id: str
    element_id: str
    export_type: str = 'stl'

    @property
    def partstudio_export_path(self) -> str:
        return rf'/partstudios/d/{self.doc_id}/{self.kind}/{self.kind_id}/e/{self.element_id}/{self.export_type}'

    @classmethod
    def from_url(cls, url: str, **kwargs) -> 'OnshapePathParams':
        match = ONSHAPE_PATH_PARAMS_REGEX.search(url.strip())
        if not match:
            raise ValueError(f'Not a valid Onshape element URL: {url!r}')
        from_url = match.groupdict()
        return cls(**from_url, **kwargs)


@dataclass
class OnshapeRequest:
    output_name: str = 'OnshapeExport'
    path_params: OnshapePathParams = field(default_factory=OnshapePathParams)
    query_params: OnshapeQueryParams = field(default_factory=OnshapeQueryParams)

    @property
    def extension(self):
        return '.zip' if not self.query_params.grouping else '.stl'  # grouped =/= zipped


def export_part_studio(on_req: OnshapeRequest, output_dir: Path):
    c = get_client()
    api_path = on_req.path_params.partstudio_export_path
    res = c.get(api_path, **on_req.query_params.__dict__)
    output_path = output_dir / f'{on_req.output_name}{on_req.extension}'
    # output_path = output_dir / f'{on_req.output_name}{on_req.extension}'
    saved = save_content(res.content, output=output_path)
    return res


def save_content(content: bytes, output: Path):
    with open(output, 'wb') as f:
        f.write(content)
    return True


ONSHAPE_PATH_PARAMS_REGEX = re.compile(
    r'/documents/(?P<doc_id>[0-9a-f]+)/(?P<kind>[wvm])/(?P<kind_id>[0-9a-f]+)/e/(?P<element_id>[0-9a-f]+)'
)


def export_document(document_url: str, output_name: str, export_dir: Path, zipped: bool = False):
    export_dir.mkdir(parents=True, exist_ok=True)
    query = OnshapeQueryParams(zipped=zipped, units='millimeter', scale=1)
    path_params = OnshapePathParams.from_url(document_url)
    on_request = OnshapeRequest(
        path_params=path_params,
        query_params=query,
        output_name=output_name,
    )
    res = export_part_studio(on_request, output_dir=export_dir)
    print(res)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Export an Onshape part studio.')
    parser.add_argument('url', help='Onshape element URL')
    parser.add_argument(
        '-d',
        '--export-dir',
        type=Path,
        default=Path.cwd(),
        help='output directory',
    )
    parser.add_argument(
        '-n',
        '--name',
        default='OnshapeExport',
        help='output file name (no extension)',
    )
    parser.add_argument(
        '-z',
        '--zipped',
        action='store_true',
        help='export as separate parts in a zip',
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None):
    args = parse_args(argv)
    export_document(args.url, export_dir=args.export_dir, output_name=args.name, zipped=args.zipped)


if __name__ == '__main__':
    main()
