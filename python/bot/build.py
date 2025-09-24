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
        *start_trees_3(bot),
        *mega_cluster_3(bot, 0),
        *mega_cluster_3(bot, 1, [1, 2, 3], combined=True),
        *small_cluster_3(bot, 18, [1, 2, 3]),
        *small_cluster_3(bot, 2, [4, 5, 6]),
        # *small_cluster_3(bot, 4, [1, 2, 3]),
        # *small_cluster_3(bot, 1, [1, 2, 3]),
        *mega_cluster_3(bot, 2, [1, 2, 3]),
        *mega_cluster_3(bot, 3, [1, 2, 3], combined=True),
        *small_cluster_3(bot, 2, [1, 2, 3]),
        *small_cluster_3(bot, 5, [1, 2, 3]),
        *small_cluster_3(bot, 4, [1, 2, 3]),
        *small_cluster_3(bot, 1, [1, 2, 3]),
        *small_cluster_3(bot, 2, [1, 2, 3]),
        *small_cluster_3(bot, 5, [1, 2, 3]),
        *small_cluster_3(bot, 4, [1, 2, 3]),
        *small_cluster_3(bot, 1, [1, 2, 3]),
    ]


def start_trees_3(bot):
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


def mega_cluster_3(bot, idx: int, build_after: list[int] = [], combined=False):
    return [
        *deeproot_1(bot, idx, build_after),
        *cluster_3(bot, 1, build_after=[1]),
        *deeproot_tree_1(bot, build_after=[1, 2, 3]),
        *cluster_3(bot, 5, build_after=[1], sunbeam=combined),
    ]


def deeproot_1(bot, idx: int, build_after: list[int] = []):
    return [
        Build(
            prototypes.Construction["deeproot"],
            requirements={Requirement.DEPOSITS},
            pos_f=lambda: bot.deposits["metal deposit"][idx].pos(),
            build_after=build_after,
        ),
    ]


def deeproot_tree_1(bot, build_after: list[int] = []):
    return [
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=4,
            build_after=build_after,
        ),
    ]


def cluster_3(bot, prev_pos: int, build_after: list[int] = [], sunbeam=False):
    return [
        Build(
            prototypes.Construction["incubator"],
            prev_pos=prev_pos,
            build_after=build_after,
            recipe=lambda: (
                bot.incubator_recipe() if not sunbeam else bot.incubator2_recipe()
            ),
        ),
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=1,
            build_after=[i + 1 for i in build_after],
        ),
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=2,
            build_after=[i + 2 for i in build_after],
        ),
    ]


def small_cluster_3(bot, prev_pos: int, build_after: list[int] = []):
    return [
        Build(
            prototypes.Construction["phytomorph"],
            prev_pos=prev_pos,
            build_after=build_after,
            recipe=lambda: bot.phytomorph_recipe(),
        ),
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=1,
            build_after=[i + 1 for i in build_after],
        ),
        Build(
            prototypes.Construction["nutritree"],
            prev_pos=2,
            build_after=[i + 2 for i in build_after],
        ),
    ]
