from dataclasses import dataclass, field
from typing import Literal


@dataclass
class OnshapeQueryParams:
    units: Unit = 'millimeter'
    scale: int = 1
    grouping: bool | None = None  # provide only None or one of these
    zipped: bool | None = None
    partIds: str = ''  # comma sep
    part_ids: list[str] = field(default_factory=list[str])

    def __post_init__(self):
        match self.grouping, self.zipped:
            case None, None:
                self.grouping = True
                self.zipped = False
            case bool(), bool():
                raise ValueError('Provide Only one of zipped and grouped')
            case None, bool():
                self.grouping = not self.zipped
            case bool(), None:
                self.zipped = not self.grouping
            case _:
                raise ValueError('Unexpected input')


Unit = Literal['meter', 'centimeter', 'millimeter', 'inch', 'foot', 'yard']
