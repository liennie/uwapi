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
        *start_trees(bot),
        *mega_cluster(bot, 0),
        *mega_cluster(bot, 1, [1, 2, 3]),
        *mega_cluster(bot, 2, [1, 2, 3]),
        *mega_cluster(bot, 3, [1, 2, 3]),
    ]


def start_trees(bot):
    return [
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
    ]


def mega_cluster(bot, idx: int, build_after: list[int] = []):
    return [
        *deeproot(bot, idx, build_after),
        *cluster(bot, 1),
        *deeproot_tree(bot),
        *cluster(bot, 5),
    ]


def deeproot(bot, idx: int, build_after: list[int] = []):
    return [
        Build(
            prototypes.Construction["deeproot"],
            requirements={Requirement.DEPOSITS},
            pos_f=lambda: bot.deposits["metal deposit"][idx].pos(),
            build_after=build_after,
        ),
    ]


def deeproot_tree(bot):
    return [
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=4,
            build_after=[1, 2, 3],
        ),
    ]


def cluster(bot, prev_pos: int):
    return [
        Build(
            prototypes.Construction["incubator"],
            prev_pos=prev_pos,
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
