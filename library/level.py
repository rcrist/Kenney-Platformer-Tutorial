import arcade
from pathlib import Path

from .dust import DustManager
from .enemy_manager import EnemyManager
from .leaf import LeafManager
from .nature import load_nature
from .physics import PhysicsManager
from .settings import MOVING_PLATFORM_SPEED


PRINCESS_IDLE_PATH = (
    "assets/kenney_assets/Toon Characters/Female person/PNG/Poses/"
    "character_femalePerson_idle.png"
)
STAR_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets/kenney_assets/New Platformer Pack/Sprites/Tiles/Default/star.png"
)
BLOCK_TILE_IDS = {1, 16, 19}


class Level:
    def __init__(self, map_path="assets/maps/level_01.json"):
        self.sound_manager = None
        # Optional layer-specific settings (e.g., spatial hashing for collisions)
        layer_options = {
            "Platforms": {"use_spatial_hash": True},
            "Locks": {"use_spatial_hash": True},
        }

        # Load the JSON map file exported from the Tiled map editor
        self.map_path = Path(map_path)
        self.name = self.map_path.stem
        self.tile_map = arcade.load_tilemap(
            # ":resources:/tiled_maps/map_with_ladders.json",
            self.map_path,
            scaling=0.5,
            layer_options=layer_options,
        )
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

    def level_setup(self, player, camera):
        """Build the runtime objects and systems associated with this level."""
        self.scene.add_sprite("Player", player)
        camera.set_limits_to_tilemap(self.tile_map)

        self.moving_platforms = self.get_layer("Moving Platforms")
        self.exit_list = self.get_layer("Exit")
        self.hazard_list = self.get_layer("Hazards")
        self.ladder_list = self.get_layer("Ladders")
        self.lock_list = self.get_layer("Locks")
        self.coin_list = self.get_layer("Coins")
        self.health_list = self.get_layer("Health")

        self.setup_exits()
        self.setup_moving_platforms()

        self.enemy_manager = EnemyManager()
        self.enemy_list = self.enemy_manager.load_enemies(self)
        self.physics_manager = PhysicsManager(
            player,
            self.enemy_list,
            moving_platforms=self.moving_platforms,
            player_walls=[self.scene["Platforms"], self.lock_list],
            enemy_walls=self.scene["Platforms"],
            ladders=self.ladder_list,
        )

        camera.follow(player)
        self.nature_list = load_nature(self)
        self.leaf_manager = LeafManager(self)
        self.star_list = arcade.SpriteList()
        self.revealed_block_ids = set()
        self.scene.add_sprite_list("Stars", sprite_list=self.star_list)
        self.dust_manager = DustManager(player)

    def get_layer(self, name):
        """Return a scene layer or an empty sprite list when it is optional."""
        try:
            return self.scene[name]
        except KeyError:
            return arcade.SpriteList()

    def collect_coins(self, player, hud_camera):
        """Collect coins touched by the player and update the HUD score."""
        coins_hit = arcade.check_for_collision_with_list(player, self.coin_list)

        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            player.coins += 1
            hud_camera.set_score(player.coins)
            if self.sound_manager is not None:
                self.sound_manager.play_coin_pickup()

    def collect_health(self, player):
        """Consume touched health pickups and restore up to 25 health each."""
        health_pickups = arcade.check_for_collision_with_list(
            player,
            self.health_list,
        )

        for health_pickup in health_pickups:
            health_pickup.remove_from_sprite_lists()
            player.health = min(player.max_health, player.health + 25)
            if self.sound_manager is not None:
                self.sound_manager.play_health_pickup()

    def collect_stars(self, player, hud_camera):
        """Collect revealed stars and award ten coins for each one."""
        stars_hit = arcade.check_for_collision_with_list(player, self.star_list)

        for star in stars_hit:
            star.remove_from_sprite_lists()
            player.coins += 10
            hud_camera.set_score(player.coins)

    def check_for_exit(self, player):
        """Return whether the player has touched a valid exit marker."""
        exits_hit = arcade.check_for_collision_with_list(player, self.exit_list)
        exit_types = {"exit", "princes", "princess"}
        return any(
            str(exit_marker.properties.get("type", "")).lower() in exit_types
            for exit_marker in exits_hit
        )

    def check_for_hazard_collision(self, player):
        """Apply the configured damage for hazards touched by the player."""
        hazards_hit = arcade.check_for_collision_with_list(player, self.hazard_list)

        for hazard in hazards_hit:
            damage = hazard.properties.get("Value")
            if damage is not None:
                player.take_damage(damage)

    def check_for_block_hit(self, player, was_moving_up):
        """Reveal a star when the player bumps a Block from underneath."""
        if self.name != "level_01" or not was_moving_up:
            return

        for block in self.moving_platforms:
            block_type = str(
                block.properties.get("type", block.properties.get("Type", ""))
            ).lower()
            is_block = (
                block_type == "block"
                or block.properties.get("tile_id") in BLOCK_TILE_IDS
            )
            if not is_block or id(block) in self.revealed_block_ids:
                continue

            overlaps_horizontally = player.right > block.left and player.left < block.right
            touches_underside = abs(player.top - block.bottom) <= 4
            if not (overlaps_horizontally and touches_underside):
                continue

            star = arcade.Sprite(STAR_PATH)
            star.center_x = block.center_x
            star.bottom = block.top
            self.star_list.append(star)
            self.revealed_block_ids.add(id(block))
            break

    def setup_moving_platforms(self):
        """Configure vertical movement from platform custom properties."""
        tile_distance = self.tile_map.tile_height * self.tile_map.scaling

        for platform in self.moving_platforms:
            properties = platform.properties
            if "Top" not in properties or "Bottom" not in properties:
                continue

            platform.boundary_top = platform.top + properties["Top"] * tile_distance
            platform.boundary_bottom = platform.bottom - properties["Bottom"] * tile_distance
            platform.change_y = MOVING_PLATFORM_SPEED

    def setup_exits(self):
        """Replace princess exit markers with the stationary princess art."""
        princess_texture = None

        for exit_marker in self.exit_list:
            exit_type = str(exit_marker.properties.get("type", "")).lower()
            if exit_type not in ("princes", "princess"):
                continue

            if princess_texture is None:
                princess_texture = arcade.load_texture(PRINCESS_IDLE_PATH)
            exit_marker.texture = princess_texture
            exit_marker.change_x = 0
            exit_marker.change_y = 0
