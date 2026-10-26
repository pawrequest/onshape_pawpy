import argparse
from pathlib import Path
from pprint import pprint

from onshape_pawpy.client import OnshapeClient
from onshape_pawpy.path import OnshapePath
from onshape_pawpy.parts import get_parts
from onshape_pawpy.query import OnshapeQueryParams
from onshape_pawpy.request import OnshapeRequest


# EndpointFn = Callable[[OnshapePaths], str]


# def do_smth(
#     on_req: OnshapeRequest,
#     *,
#     client: OnshapeClient | None = None,
#     endpoint_fn: EndpointFn,
# ):
#     client = client or get_client()
#     return client.get(path=endpoint_fn(on_req.path_params), **on_req.query_params.__dict__)


# parts2 = partial(do_smth, endpoint_fn=OnshapePaths.get_ps_parts)


def export_part_studio(
    on_req: OnshapeRequest, output_dir: Path, client: OnshapeClient | None = None
):
    output_dir.mkdir(parents=True, exist_ok=True)
    client = client or OnshapeClient()
    api_path = on_req.path_params.get_export()
    res = client.get(api_path, **on_req.query_params.__dict__)
    save_content(res.content, output=output_dir / on_req.filename)
    return res


def save_content(content: bytes, output: Path):
    with open(output, 'wb') as f:
        f.write(content)
    return True


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
        '-f',
        '--filter-text',
        default=None,
        help='filter parts by name',
    )
    parser.add_argument(
        '-z',
        '--zipped',
        action='store_true',
        help='export as separate parts in a zip',
    )
    parser.add_argument(
        '-p',
        '--part-ids',
        nargs='+',
        help='part IDs to export',
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None):
    args = parse_args(argv)
    query = OnshapeQueryParams(zipped=args.zipped, units='millimeter', scale=1)
    path = OnshapePath.from_url(args.url)
    on_request = OnshapeRequest(
        path_params=path,
        query_params=query,
        output_name=args.name,
    )

    # parts = get_parts(on_request, filter_text=FRAME)
    parts = get_parts(on_request, filter_text=args.filter_text)
    part_ids = [_.get('partId', '') for _ in parts]
    on_request.query_params.partIds = ','.join(part_ids)
    export_part_studio(on_request, output_dir=args.export_dir)
    pprint(on_request.__dict__)


if __name__ == '__main__':
    main()
