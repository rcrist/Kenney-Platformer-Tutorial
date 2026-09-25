import arcade

from .enemy import Enemy
from .settings import ENEMY_SPEED

ENEMY_TEXTURES = {
    "robot1": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_blueDrive{i}.png",
    "robot2": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_greenDrive{i}.png",
    "robot3": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_redDrive{i}.png",
    "robot4": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_yellowDrive{i}.png",
}

ROBOT_DAMAGE_TEXTURES = {
    "robot1": "blue",
    "robot2": "green",
    "robot3": "red",
    "robot4": "yellow",
}
ROBOT_TEXTURE_ROOT = "assets/kenney_assets/Robot Pack/PNG/Side view"

EXTENDED_ENEMY_ROOT = "assets/kenney_assets/Platformer Art Extended Enemies/Enemy sprites"
ALIEN_ROOT = "assets/kenney_assets/Platformer Art Extended Enemies/Alien sprites"
SAUCER_ROOT = "assets/kenney_assets/Alien UFO Pack/PNG"
ROBOWSER_ROOT = "assets/kenney_assets/Toon Characters/Robot/PNG/Poses"

EXTENDED_ENEMY_ANIMATIONS = {
    "spider": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/spider.png",
        "walk": [
            f"{EXTENDED_ENEMY_ROOT}/spider_walk1.png",
            f"{EXTENDED_ENEMY_ROOT}/spider_walk2.png",
        ],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/spider_hit.png"],
    },
    "slime": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/slime.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/slime_walk.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/slime_hit.png"],
    },
    "snail": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/snail.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/snail_walk.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/snail_hit.png"],
    },
    "fly": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/fly.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/fly_fly.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/fly_hit.png"],
    },
    "boss_block": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/slimeBlock.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/slimeBlock.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/slime_hit.png"],
    },
    "bat": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/bat.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/bat_fly.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/bat_hit.png"],
    },
    "ghost": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/ghost.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/ghost.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/ghost_hit.png"],
    },
    "boss_ghost": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/ghost.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/ghost.png"],
        "damage": [f"{EXTENDED_ENEMY_ROOT}/ghost_hit.png"],
    },
    "alien1": {
        "idle": f"{ALIEN_ROOT}/alienBeige_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienBeige_walk1.png",
            f"{ALIEN_ROOT}/alienBeige_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienBeige_hurt.png"],
    },
    "alien2": {
        "idle": f"{ALIEN_ROOT}/alienBlue_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienBlue_walk1.png",
            f"{ALIEN_ROOT}/alienBlue_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienBlue_hurt.png"],
    },
    "alien3": {
        "idle": f"{ALIEN_ROOT}/alienGreen_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienGreen_walk1.png",
            f"{ALIEN_ROOT}/alienGreen_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienGreen_hurt.png"],
    },
    "alien4": {
        "idle": f"{ALIEN_ROOT}/alienPink_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienPink_walk1.png",
            f"{ALIEN_ROOT}/alienPink_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienPink_hurt.png"],
    },
    "alien5": {
        "idle": f"{ALIEN_ROOT}/alienYellow_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienYellow_walk1.png",
            f"{ALIEN_ROOT}/alienYellow_walk2.png",
        ],
        "damage": [f"{ALIEN_ROOT}/alienYellow_hurt.png"],
    },
    "saucer1": {
        "idle": f"{SAUCER_ROOT}/shipBeige_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipBeige_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipBeige_damage1.png",
            f"{SAUCER_ROOT}/shipBeige_damage2.png",
        ],
    },
    "saucer2": {
        "idle": f"{SAUCER_ROOT}/shipBlue_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipBlue_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipBlue_damage1.png",
            f"{SAUCER_ROOT}/shipBlue_damage2.png",
        ],
    },
    "saucer3": {
        "idle": f"{SAUCER_ROOT}/shipGreen_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipGreen_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipGreen_damage1.png",
            f"{SAUCER_ROOT}/shipGreen_damage2.png",
        ],
    },
    "saucer4": {
        "idle": f"{SAUCER_ROOT}/shipPink_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipPink_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipPink_damage1.png",
            f"{SAUCER_ROOT}/shipPink_damage.png",
        ],
    },
    "saucer5": {
        "idle": f"{SAUCER_ROOT}/shipYellow_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipYellow_manned.png"],
        "damage": [
            f"{SAUCER_ROOT}/shipYellow_damage1.png",
            f"{SAUCER_ROOT}/shipYellow_damage2.png",
        ],
    },
    "robobowser": {
        "idle": f"{ROBOWSER_ROOT}/character_robot_idle.png",
        "walk": [
            f"{ROBOWSER_ROOT}/character_robot_walk{i}.png"
            for i in range(8)
        ],
        "damage": [f"{ROBOWSER_ROOT}/character_robot_hit.png"],
    },
}

DEFAULT_CONTACT_DAMAGE = 10
BOSS_CONTACT_DAMAGE = {
    "boss_ghost": 20,
    "boss_block": 20,
    "robobowser": 30,
}
BOSS_TYPES = frozenset(BOSS_CONTACT_DAMAGE)

class EnemyManager:
    """Create runtime enemies from markers in a level's tilemap."""

    def __init__(self):
        self.enemy_list = arcade.SpriteList()
        self.sound_manager = None
        self.boss_encounter_played = False

    def load_enemies(self, level):
        self.enemy_list = arcade.SpriteList()
        enemy_markers = []

        try:
            sprite_markers = level.scene.get_sprite_list("Enemies")
        except KeyError:
            sprite_markers = ()

        for marker in sprite_markers:
            enemy_markers.append((marker.properties, marker.position))

        # Tiled point markers are loaded as objects rather than Scene sprites.
        for marker in level.tile_map.object_lists.get("Enemies", ()):
            if isinstance(marker.shape, tuple) and len(marker.shape) == 2:
                enemy_markers.append((marker.properties or {}, marker.shape))

        tile_distance = level.tile_map.tile_width * level.tile_map.scaling

        for properties, marker_position in enemy_markers:
            enemy = self._create_enemy(properties, marker_position, tile_distance)
            if enemy is not None:
                self.enemy_list.append(enemy)

        if "Enemies" in level.scene:
            level.scene.remove_sprite_list_by_name("Enemies")
        level.scene.add_sprite_list("Enemies", sprite_list=self.enemy_list)
        return self.enemy_list

    def check_for_boss_in_viewport(self, camera):
        """Play the encounter cue once when a living boss enters the viewport."""
        if self.boss_encounter_played or self.sound_manager is None:
            return

        view_left = camera.position.x - camera.camera_width / 2
        view_right = camera.position.x + camera.camera_width / 2
        view_bottom = camera.position.y - camera.camera_height / 2
        view_top = camera.position.y + camera.camera_height / 2

        for enemy in self.enemy_list:
            if enemy.enemy_type not in BOSS_TYPES or enemy.health <= 0:
                continue

            boss_is_visible = (
                enemy.right >= view_left
                and enemy.left <= view_right
                and enemy.top >= view_bottom
                and enemy.bottom <= view_top
            )
            if boss_is_visible:
                self.sound_manager.play_boss_encounter()
                self.boss_encounter_played = True
                return

    def check_for_enemy_collision(self, player, lock_list, physics_manager):
        """Resolve damage and cleanup when the player touches enemies."""
        enemies_hit = arcade.check_for_collision_with_list(player, self.enemy_list)

        if not enemies_hit:
            return

        contact_damage = max(
            BOSS_CONTACT_DAMAGE.get(enemy.enemy_type, DEFAULT_CONTACT_DAMAGE)
            for enemy in enemies_hit
        )
        player.take_damage(contact_damage)
        for enemy in enemies_hit:
            damage_applied = enemy.take_damage(25)
            if damage_applied and self.sound_manager is not None:
                if enemy.health <= 0:
                    self.sound_manager.play_enemy_death()
                else:
                    self.sound_manager.play_enemy_hurt()
            if enemy.health <= 0:
                if enemy.enemy_type == "robobowser":
                    lock_list.clear()
                enemy.remove_from_sprite_lists()
                physics_manager.remove_enemy(enemy)

    @staticmethod
    def _create_enemy(properties, marker_position, tile_distance):
        enemy_type_value = properties.get("type")
        if not isinstance(enemy_type_value, str):
            print("Skipping enemy marker with no type")
            return None

        enemy_type = enemy_type_value.lower().replace("-", "_")

        if enemy_type in ENEMY_TEXTURES:
            robot_color = ROBOT_DAMAGE_TEXTURES[enemy_type]
            enemy = Enemy(
                ENEMY_TEXTURES[enemy_type],
                2,
                damage_paths=[
                    f"{ROBOT_TEXTURE_ROOT}/robot_{robot_color}Damage1.png",
                    f"{ROBOT_TEXTURE_ROOT}/robot_{robot_color}Damage2.png",
                ],
            )
            enemy.scale = 0.3
        elif enemy_type in EXTENDED_ENEMY_ANIMATIONS:
            animation = EXTENDED_ENEMY_ANIMATIONS[enemy_type]
            enemy = Enemy(
                idle_path=animation["idle"],
                walk_paths=animation["walk"],
                damage_paths=animation.get("damage"),
                invert_facing=enemy_type in ("snail", "slime", "fly"),
            )
            if enemy_type == "robobowser":
                enemy.scale = 1.5
            elif enemy_type in ("boss_ghost", "boss_block"):
                enemy.scale = 1.0
            else:
                enemy.scale = 0.5
            enemy.is_flying = enemy_type in ("bat", "fly") or enemy_type.startswith(
                "saucer"
            )
        else:
            print(f"Skipping unknown enemy type: {enemy_type}")
            return None

        enemy.enemy_type = enemy_type
        enemy.position = marker_position
        enemy.change_x = properties.get("change_x", ENEMY_SPEED)

        if "boundary_left" in properties and "boundary_right" in properties:
            enemy.set_patrol_range(
                marker_position[0] - properties["boundary_left"] * tile_distance,
                marker_position[0] + properties["boundary_right"] * tile_distance,
            )

        return enemy
