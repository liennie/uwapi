import random
import time
from uwapi import *
import random
from . import prototypes
from dataclasses import dataclass, field
from typing import Callable
from enum import Enum


class Requirement(Enum):
    DEPOSITS = 0


def addToList(obj: dict[str, list[Entity]], key, value):
    if key in obj:
        obj[key].append(value)
    else:
        obj[key] = [value]


class Bot:
    is_configured: bool = False
    work_step: int = 0  # save some cpu cycles by splitting work over multiple steps
    own_entities: list[Entity] | None = None
    main_entity: Entity | None = None
    deposits: dict[str, list[Entity]] | None = {}

    def __init__(self):
        uw_events.on_update(self.on_update)

        self.buildings: list[Build] = [
            # treeeeees
            Build(
                prototypes.Construction["nutritree"],
                pos_f=lambda: self.main_entity.pos(),
            ),
            Build(
                prototypes.Construction["nutritree"],
                pos_f=lambda: self.main_entity.pos(),
            ),
            Build(
                prototypes.Construction["nutritree"],
                pos_f=lambda: self.main_entity.pos(),
            ),
            # deeproot
            Build(
                prototypes.Construction["deeproot"],
                requirements={Requirement.DEPOSITS},
                pos_f=lambda: self.deposits["metal deposit"][0].pos(),
            ),
            # cluster 1
            Build(
                prototypes.Construction["incubator"],
                prev_pos=1,
                build_after=[1],
                recipe=lambda: prototypes.Recipe["wardkin"],
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
                recipe=lambda: prototypes.Recipe["wardkin"],
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

        self.recipes = [
            (i, self.buildings[i].recipe)
            for i in range(len(self.buildings))
            if self.buildings[i].recipe is not None
        ]

        self.req_funcs = {
            Requirement.DEPOSITS: self.get_deposits,
        }

    def attack_nearest_enemies(self):
        attack_unist = [
            x
            for x in self.own_entities
            if x.proto().data.get("dps", 0) > 0 and x.id != self.main_entity.id
        ]
        if not attack_unist:
            return

        # for unit in attack_unist:
        #     group_size = self._created_units.get(unit.Id, None)

        #     if group_size is None:
        #         if dict_len <3:
        #             group_size = 2
        #         elif dict_len < 25:
        #             group_size = 10
        #         else:
        #             group_size = 15

        #         if group_size < 15:
        #             self._created_units[unit.Id] = group_size

        #     group_radius = 200
        #     if len(self.nearby_units(unit, enemy_whitelist_ids, 500)) > 0:
        #         group_radius = 75

        #     if self.group_size(unit, attack_unist_ids, group_radius) >= group_size:
        #         self.attack_nearest_enemies(unit, enemy_units)
        #     elif len(self.nearby_units(unit, enemy_whitelist_ids, 300)) > 0:
        #         self.attack_nearest_enemies(unit, enemy_units)
        #     else:
        #         self.regroup(unit, attack_unist, group_radius)

        enemy_units = [
            x for x in uw_world.entities().values() if x.enemy() and x.Unit is not None
        ]
        if not enemy_units:
            return

        for own in attack_unist:
            if len(uw_commands.orders(own.id)) == 0:
                enemy = min(
                    enemy_units,
                    key=lambda x: uw_map.distance_estimate(own.pos(), x.pos()),
                )
                uw_commands.order(own.id, uw_commands.fight_to_entity(enemy.id))

    def configure(self):
        # auto start the game if available
        if (
            self.is_configured
            and uw_game.game_state() == GameState.Session
            and uw_world.is_admin()
        ):
            time.sleep(3)  # give the observer enough time to connect
            uw_admin.start_game()
            return
        # is configuring possible?
        if (
            self.is_configured
            or uw_game.game_state() != GameState.Session
            or uw_world.my_player_id() == 0
        ):
            return
        self.is_configured = True
        uw_game.log_info("configuration start")
        uw_game.set_player_name("Neviem")
        uw_game.player_join_force(0)  # create new force
        uw_game.set_force_color(1, 0.6, 1)
        uw_game.set_force_race(4152033917)  # biomass
        if uw_world.is_admin():
            # uw_admin.set_map_selection("planets/tetrahedron.uwmap")
            uw_admin.set_map_selection("special/risk.uwmap")
            uw_admin.add_ai()
            uw_admin.set_automatic_suggested_camera_focus(True)
        uw_game.log_info("configuration done")

    def get_own_enities(self):
        self.own_entities = [
            x for x in uw_world.entities().values() if x.own() and x.Unit is not None
        ]

    def get_main_building(self):
        for entity in self.own_entities:
            if (
                entity.type() == PrototypeType.Unit
                and entity.proto().name == "overlord"
            ):
                self.main_entity = entity
                return

        self.main_entity = None
        return

    def get_deposits(self):
        for entity in uw_world.entities().values():
            if entity.Proto is None:
                continue

            proto_name = entity.proto().name
            addToList(self.deposits, proto_name, entity)

            # sort deposits by distance
            for deposit_type in self.deposits.keys():
                self.deposits[deposit_type] = sorted(
                    self.deposits[deposit_type],
                    key=lambda x: uw_map.distance_estimate(
                        self.main_entity.pos(), x.pos()
                    ),
                )

    def get_incubators(self):
        self.incubators = [
            entity for entity in self.own_entities if entity.proto().name == "incubator"
        ]

    def entity_is_this_proto(self, entity: Entity, proto: int) -> bool:
        return entity.own() and entity.proto().name == uw_prototypes.get(proto).name

    def entity_is_built(self, entity: Entity, proto: int) -> bool:
        return self.entity_is_this_proto(entity, proto) and entity.Life is not None

    def building_is_built(self, i: int) -> bool:
        build = self.buildings[i]
        if build.pos < 0:
            return False

        return any(
            self.entity_is_built(
                uw_world.entity(id),
                build.proto,
            )
            for id in uw_world.overview_entities(build.pos)
        )

    def building_is_being_built(self, i: int) -> bool:
        build = self.buildings[i]
        if build.pos < 0:
            return False

        return any(
            self.entity_is_this_proto(
                uw_world.entity(id),
                build.proto,
            )
            and uw_world.entity(id).Life is None
            for id in uw_world.overview_entities(build.pos)
        )

    def building_is_placed(self, i: int) -> bool:
        build = self.buildings[i]
        if build.pos < 0:
            return False

        return any(
            self.entity_is_this_proto(
                uw_world.entity(id),
                build.proto,
            )
            for id in uw_world.overview_entities(build.pos)
        )

    def set_building_recipe(self, i: int, recipe: int):
        build = self.buildings[i]
        if build.pos < 0:
            return

        for id in uw_world.overview_entities(build.pos):
            entity = uw_world.entity(id)
            if self.entity_is_this_proto(
                entity,
                build.proto,
            ):
                if entity.Recipe is None or entity.Recipe.recipe != recipe:
                    uw_commands.set_recipe(id, recipe)

    def can_be_built(self, i: int) -> bool:
        build = self.buildings[i]
        return (
            not self.building_is_placed(i)
            and (build.prev_pos <= 0 or self.buildings[build.prev_pos].pos >= 0)
            and all(self.building_is_built(i - prev) for prev in build.build_after)
        )

    def fulfill_requirements(self, requirements: set[Requirement]):
        for req in requirements:
            self.req_funcs[req]()

    def on_update(self, stepping: bool):
        self.configure()
        if not stepping:
            return

        self.work_step += 1
        match (
            self.work_step % 10
        ):  # save some cpu cycles by splitting work over multiple steps
            case 1:
                self.get_own_enities()
                self.get_main_building()
                self.get_incubators()

                for i in range(len(self.buildings)):
                    if self.can_be_built(i):
                        build = self.buildings[i]

                        self.fulfill_requirements(build.requirements)

                        pos = (
                            self.buildings[i - build.prev_pos].pos
                            if build.prev_pos > 0
                            else build.pos_f()
                        )
                        placement = uw_world.find_construction_placement(
                            build.proto, pos
                        )
                        uw_game.log_info(
                            f"trying to build {uw_prototypes.get(build.proto).name} next to {pos} at {placement}"
                        )
                        uw_commands.place_construction(build.proto, placement)
                        build.pos = placement
                        break

                for i, recipe in self.recipes:
                    self.set_building_recipe(i, recipe())

            # case 2:
            #     self.attack_nearest_enemies()

            # case 7:
            #     self.attack_nearest_enemies()

    def run(self):
        uw_game.log_info("bot-py start")

        # Unnatural Worlds/bin/profiling.htm?port={port} # log: profiling server listens on port {}
        # uw_game.performance_profiling(True)

        if not uw_game.try_reconnect():
            uw_game.set_connect_start_gui(True, "--observer 2")
            if not uw_game.connect_environment():
                # automatically select map and start the game from here in the code
                if False:
                    uw_game.connect_new_server(0, "", "--allowUwApiAdmin 1")
                else:
                    uw_game.connect_new_server()
        uw_game.log_info("bot-py done")


@dataclass
class Build:
    proto: int = 0
    requirements: set[Requirement] = field(default_factory=set)
    prev_pos: int = -1
    pos_f: Callable[[], int] | None = None
    build_after: list[int] = field(default_factory=list)
    recipe: Callable[[], int] | None = None

    pos: int = -1
