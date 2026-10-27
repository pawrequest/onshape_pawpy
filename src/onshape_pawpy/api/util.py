from pathlib import Path
from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv
from pydantic import BaseModel, TypeAdapter

if TYPE_CHECKING:
    from onshape_pawpy.path import OnshapeIds

PROJECT_ROOT = Path(__file__).parent.parent.parent


def _load_dotenv(path: Path = PROJECT_ROOT / '.env') -> None:
    if not path.exists():
        raise FileNotFoundError(f'.env file not found at {path}')
    load_dotenv(dotenv_path=path, override=False)


def build_path(ids: OnshapeIds, prefix: str = '', suffix: str = '') -> str:
    did, wvm, wvm_id = ids[:3]
    eid = ids[3] if len(ids) > 3 else None
    path = f'{prefix}/d/{did}/{wvm}/{wvm_id}'
    if eid:
        path += f'/e/{eid}'
    if suffix:
        path += suffix
    print('Built Path : ', path)
    return path


_list_adapters: dict[type[BaseModel], TypeAdapter[Any]] = {}


def _list_adapter[M: BaseModel](model: type[M]) -> TypeAdapter[list[M]]:
    if (adapter := _list_adapters.get(model)) is None:
        adapter = _list_adapters[model] = TypeAdapter(list[model])  # pyright: ignore[reportInvalidTypeArguments]
    return adapter


def _body(body: BaseModel | None) -> dict[str, Any] | None:
    return body.model_dump(mode='json', exclude_none=True) if body else None
