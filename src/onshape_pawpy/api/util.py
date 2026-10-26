from pathlib import Path

from dotenv import load_dotenv

from onshape_pawpy.path import OnshapeIds

PROJECT_ROOT = Path(__file__).parent.parent.parent


def _load_dotenv(path: Path = PROJECT_ROOT / '.env') -> None:
    if not path.exists():
        raise FileNotFoundError(f'.env file not found at {path}')
    load_dotenv(dotenv_path=path, override=False)


def build_path(ids: OnshapeIds, prefix: str = '', suffix: str = '') -> str:
    did, wvm, wvm_id, eid = ids
    path = f'{prefix}/d/{did}/{wvm}/{wvm_id}'
    if eid:
        path += f'/e/{eid}'
    if suffix:
        path += suffix
    print(path)
    print(path)
    print(path)
    return path
