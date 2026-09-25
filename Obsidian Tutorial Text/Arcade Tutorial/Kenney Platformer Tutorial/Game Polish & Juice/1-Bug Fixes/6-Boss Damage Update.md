Currently, all bosses give 10 damage points to the player.

Change to:
- Level 2 - Ghost Boss - 20
- Level 3 - Slime Block Boss - 20
- Level 4 - Robowser - 30 (You are going to need a health pickup to beat this bad boy.)

```python title=enemy_manager.py
import arcade

from .enemy import Enemy
from .settings import ENEMY_SPEED

ENEMY_TEXTURES = {
    "robot1": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_blueDrive{i}.png",
    "robot2": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_greenDrive{i}.png",
    "robot3": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_redDrive{i}.png",
    "robot4": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_yellowDrive{i}.png",
}

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
    },
    "slime": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/slime.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/slime_walk.png"],
    },
    "snail": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/snail.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/snail_walk.png"],
    },
    "fly": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/fly.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/fly_fly.png"],
    },
    "boss_block": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/slimeBlock.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/slimeBlock.png"],
    },
    "bat": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/bat.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/bat_fly.png"],
    },
    "ghost": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/ghost.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/ghost.png"],
    },
    "boss_ghost": {
        "idle": f"{EXTENDED_ENEMY_ROOT}/ghost.png",
        "walk": [f"{EXTENDED_ENEMY_ROOT}/ghost.png"],
    },
    "alien1": {
        "idle": f"{ALIEN_ROOT}/alienBeige_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienBeige_walk1.png",
            f"{ALIEN_ROOT}/alienBeige_walk2.png",
        ],
    },
    "alien2": {
        "idle": f"{ALIEN_ROOT}/alienBlue_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienBlue_walk1.png",
            f"{ALIEN_ROOT}/alienBlue_walk2.png",
        ],
    },
    "alien3": {
        "idle": f"{ALIEN_ROOT}/alienGreen_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienGreen_walk1.png",
            f"{ALIEN_ROOT}/alienGreen_walk2.png",
        ],
    },
    "alien4": {
        "idle": f"{ALIEN_ROOT}/alienPink_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienPink_walk1.png",
            f"{ALIEN_ROOT}/alienPink_walk2.png",
        ],
    },
    "alien5": {
        "idle": f"{ALIEN_ROOT}/alienYellow_stand.png",
        "walk": [
            f"{ALIEN_ROOT}/alienYellow_walk1.png",
            f"{ALIEN_ROOT}/alienYellow_walk2.png",
        ],
    },
    "saucer1": {
        "idle": f"{SAUCER_ROOT}/shipBeige_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipBeige_manned.png"],
    },
    "saucer2": {
        "idle": f"{SAUCER_ROOT}/shipBlue_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipBlue_manned.png"],
    },
    "saucer3": {
        "idle": f"{SAUCER_ROOT}/shipGreen_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipGreen_manned.png"],
    },
    "saucer4": {
        "idle": f"{SAUCER_ROOT}/shipPink_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipPink_manned.png"],
    },
    "saucer5": {
        "idle": f"{SAUCER_ROOT}/shipYellow_manned.png",
        "walk": [f"{SAUCER_ROOT}/shipYellow_manned.png"],
    },
    "robobowser": {
        "idle": f"{ROBOWSER_ROOT}/character_robot_idle.png",
        "walk": [
            f"{ROBOWSER_ROOT}/character_robot_walk{i}.png"
            for i in range(8)
        ],
    },
}

DEFAULT_CONTACT_DAMAGE = 10
BOSS_CONTACT_DAMAGE = {
    "boss_ghost": 20,
    "boss_block": 20,
    "robobowser": 30,
}

class EnemyManager:
    """Create runtime enemies from markers in a level's tilemap."""

    def __init__(self):
        self.enemy_list = arcade.SpriteList()

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
            enemy.take_damage(25)
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
            enemy = Enemy(ENEMY_TEXTURES[enemy_type], 2)
            enemy.scale = 0.3
        elif enemy_type in EXTENDED_ENEMY_ANIMATIONS:
            animation = EXTENDED_ENEMY_ANIMATIONS[enemy_type]
            enemy = Enemy(
                idle_path=animation["idle"],
                walk_paths=animation["walk"],
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

```