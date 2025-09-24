from dataclasses import dataclass, field
from typing import Callable
from enum import Enum
from . import prototypes


class Requirement(Enum):
    DEPOSITS = 0


@dataclass
class Build:
    proto: int = 0
    requirements: set[Requirement] = field(default_factory=set)
    prev_pos: int = -1
    pos_f: Callable[[], int] | None = None
    build_after: list[int] = field(default_factory=list)
    recipe: Callable[[], int] | None = None

    pos: int = -1


def create_order(bot) -> list[Build]:
    return [
        # treeeeees
        Build(
            prototypes.Construction["nutritree"],
            pos_f=lambda: bot.main_entity.pos(),
        ),
        Build(
            prototypes.Construction["nutritree"],
            pos_f=lambda: bot.main_entity.pos(),
        ),
        Build(
            prototypes.Construction["nutritree"],
            pos_f=lambda: bot.main_entity.pos(),
        ),
        # deeproot
        Build(
            prototypes.Construction["deeproot"],
            requirements={Requirement.DEPOSITS},
            pos_f=lambda: bot.deposits["metal deposit"][0].pos(),
        ),
        # cluster 1
        Build(
            prototypes.Construction["incubator"],
            prev_pos=1,
            build_after=[1],
            recipe=lambda: bot.incubator_recipe(),
        ),
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=1,
            build_after=[2],
        ),
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=2,
            build_after=[3],
        ),
        # deeproot tree
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=4,
            build_after=[1, 2, 3],
        ),
        # cluster 2
        Build(
            prototypes.Construction["incubator"],
            prev_pos=5,
            build_after=[1],
            recipe=lambda: bot.incubator_recipe(),
        ),
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=1,
            build_after=[2],
        ),
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=2,
            build_after=[3],
        ),
    ]
