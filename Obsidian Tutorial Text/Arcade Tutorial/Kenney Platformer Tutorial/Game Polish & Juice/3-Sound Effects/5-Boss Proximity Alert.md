```python title=audio_manager.py
import arcade
import random
from pathlib import Path


KENNEY_AUDIO_ROOT = (
    Path(__file__).resolve().parent.parent
    / "assets/kenney_assets/audio"
)
AUDIO_ROOT = KENNEY_AUDIO_ROOT / "Impact Sounds"


class MusicManager:
    """Load, loop, and switch level background music."""

    def __init__(self, volume=0.25):
        self.volume = volume
        self.current_path = None
        self.current_sound = None
        self.current_player = None
        self.sounds = {}

    def play(self, music_path):
        if music_path == self.current_path and self.current_player is not None:
            return

        self.stop()
        sound = self.sounds.get(music_path)
        if sound is None:
            sound = arcade.load_sound(music_path)
            self.sounds[music_path] = sound

        self.current_path = music_path
        self.current_sound = sound
        self.current_player = sound.play(volume=self.volume, loop=True)

    def stop(self):
        if self.current_sound is not None and self.current_player is not None:
            self.current_sound.stop(self.current_player)

        self.current_path = None
        self.current_sound = None
        self.current_player = None


class PlayerSoundManager:
    """Play player sound effects and control the walking cadence."""

    FOOTSTEP_INTERVAL = 0.28
    BOSS_ALARM_INTERVAL = 0.32
    BOSS_ALARM_PULSES = 8
    BOSS_ALARM_VOICES = 3

    def __init__(self, volume=0.35):
        self.volume = volume
        self.footstep_timer = 0.0
        self.boss_alarm_timer = 0.0
        self.boss_alarm_pulses_remaining = 0
        self.boss_alarm_tone_index = 0
        self.footsteps = self._load_sounds(
            "Audio", "footstep_grass", range(5), separator="_", number_width=3
        )
        self.jumps = self._load_sounds(
            "Retro Sounds 2/Audio", "jump", range(1, 4)
        )
        self.hurts = self._load_sounds(
            "Retro Sounds 2/Audio", "hurt", range(1, 4)
        )
        self.enemy_hits = self._load_sounds(
            "Retro Sounds 2/Audio", "hit", range(1, 4)
        )
        self.enemy_deaths = self._load_sounds(
            "Retro Sounds 2/Audio", "explosion", range(1, 4)
        )
        self.coin_pickups = self._load_sounds(
            "Retro Sounds 2/Audio", "coin", range(1, 4)
        )
        self.health_pickups = [
            arcade.load_sound(
                KENNEY_AUDIO_ROOT / "Digital Audio/Audio" / f"powerUp{number}.ogg"
            )
            for number in range(1, 4)
        ]
        self.boss_alarm_tones = [
            arcade.load_sound(
                KENNEY_AUDIO_ROOT / "Digital Audio/Audio/twoTone1.ogg"
            ),
            arcade.load_sound(
                KENNEY_AUDIO_ROOT / "Digital Audio/Audio/twoTone2.ogg"
            ),
        ]

    @staticmethod
    def _load_sounds(folder, stem, numbers, separator="", number_width=0):
        sounds = []
        for number in numbers:
            suffix = f"{number:0{number_width}d}" if number_width else str(number)
            sounds.append(
                arcade.load_sound(AUDIO_ROOT / folder / f"{stem}{separator}{suffix}.ogg")
            )
        return sounds

    def update(self, delta_time, walking, grounded):
        """Play footsteps at a steady cadence while walking on the ground."""
        self._update_boss_alarm(delta_time)

        if not (walking and grounded):
            self.footstep_timer = 0.0
            return

        self.footstep_timer -= delta_time
        if self.footstep_timer <= 0:
            random.choice(self.footsteps).play(volume=self.volume * 0.65)
            self.footstep_timer = self.FOOTSTEP_INTERVAL

    def play_jump(self):
        random.choice(self.jumps).play(volume=self.volume)

    def play_hurt(self):
        random.choice(self.hurts).play(volume=self.volume)

    def play_enemy_hurt(self):
        random.choice(self.enemy_hits).play(volume=self.volume)

    def play_enemy_death(self):
        random.choice(self.enemy_deaths).play(volume=self.volume)

    def play_coin_pickup(self):
        random.choice(self.coin_pickups).play(volume=self.volume)

    def play_health_pickup(self):
        random.choice(self.health_pickups).play(volume=self.volume)

    def play_boss_encounter(self):
        """Start a loud, alternating sci-fi warning pattern."""
        self.boss_alarm_pulses_remaining = self.BOSS_ALARM_PULSES
        self.boss_alarm_tone_index = 0
        self.boss_alarm_timer = 0.0
        self._update_boss_alarm(0.0)

    def _update_boss_alarm(self, delta_time):
        if self.boss_alarm_pulses_remaining <= 0:
            return

        self.boss_alarm_timer -= delta_time
        if self.boss_alarm_timer > 0:
            return

        tone = self.boss_alarm_tones[self.boss_alarm_tone_index]
        for _ in range(self.BOSS_ALARM_VOICES):
            tone.play(volume=1.0)
        self.boss_alarm_tone_index = 1 - self.boss_alarm_tone_index
        self.boss_alarm_pulses_remaining -= 1
        self.boss_alarm_timer = self.BOSS_ALARM_INTERVAL

```

```python title=enemy_manager.py
import arcade
import math

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
BOSS_ENCOUNTER_DISTANCE = 350

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

    def check_for_boss_proximity(self, player):
        """Play the encounter cue once when the player approaches a living boss."""
        if self.boss_encounter_played or self.sound_manager is None:
            return

        for enemy in self.enemy_list:
            if enemy.enemy_type not in BOSS_TYPES or enemy.health <= 0:
                continue

            distance = math.hypot(
                player.center_x - enemy.center_x,
                player.center_y - enemy.center_y,
            )
            if distance <= BOSS_ENCOUNTER_DISTANCE:
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

```

```python title=game.py
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, HudCamera, Player
from library.game_manager import GameManager
from library.audio_manager import PlayerSoundManager
from library.lighting import LightingManager
from library.settings import *

WINDOW_TITLE = "Kenney Platformer Tutorial"
class GameView(arcade.View):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager

        self.background_color = arcade.color.SKY_BLUE
        self.camera = GameCamera()
        self.game_manager.configure_camera(self.camera)
        self.hud_camera = HudCamera()

        # Create a player
        self.player = Player()
        self.player_sound_manager = PlayerSoundManager()
        self.player.sound_manager = self.player_sound_manager
        self.game_manager.restore_player_state(self.player, self.hud_camera)
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)

        self.level = self.game_manager.create_level()
        self.level.sound_manager = self.player_sound_manager
        self.game_manager.configure_player(self.player)
        self.level.level_setup(self.player, self.camera)

        self.enemy_list = self.level.enemy_list
        self.level.enemy_manager.sound_manager = self.player_sound_manager
        self.physics_manager = self.level.physics_manager
        self.leaf_manager = self.level.leaf_manager
        self.dust_manager = self.level.dust_manager
        self.lighting_manager = LightingManager(self.level.name, self.player)

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.lighting_manager.draw(self.draw_world)
        self.player.draw_health_bar()
        for enemy in self.enemy_list:
            enemy.draw_health_bar()

        self.hud_camera.draw()

    def draw_world(self):
        self.camera.draw_background()
        self.level.scene.draw(pixelated=True)
        self.dust_manager.draw()

    def on_update(self, delta_time):
        player_was_moving_up = self.player.change_y > 0
        self.physics_manager.update_player()
        self.level.check_for_block_hit(self.player, player_was_moving_up)
        self.player.keep_in_level(self.level.tile_map)

        if self.game_manager.check_for_player_death(self.player):
            return

        if self.level.check_for_exit(self.player):
            self.game_manager.complete_level(self.player)
            return

        self.level.collect_coins(self.player, self.hud_camera)
        self.level.collect_stars(self.player, self.hud_camera)
        self.level.collect_health(self.player)
        self.level.check_for_hazard_collision(self.player)
        if self.game_manager.check_for_player_death(self.player):
            return

        self.physics_manager.update_enemies()
        self.level.enemy_manager.check_for_boss_proximity(self.player)
        self.level.enemy_manager.check_for_enemy_collision(
            self.player,
            self.level.lock_list,
            self.physics_manager,
        )
        if self.game_manager.check_for_player_death(self.player):
            return

        for enemy in self.enemy_list:
            enemy.on_update(delta_time)

        self.level.scene.update_animation(delta_time)
        self.player.update_state(
            delta_time,
            on_moving_platform=self.physics_manager.player_on_moving_platform,
        )
        self.player_sound_manager.update(
            delta_time,
            walking=self.player.change_x != 0,
            grounded=self.physics_manager.player_is_grounded,
        )
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.dust_manager.update(
            delta_time,
            grounded=self.physics_manager.player_is_grounded,
        )
        self.camera.follow(self.player)
        self.lighting_manager.update()
        self.leaf_manager.update(delta_time, self.camera)

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            if self.physics_manager.jump():
                self.dust_manager.spawn_jump()
                self.player_sound_manager.play_jump()
                     
        self.player.on_key_press(key, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        self.player.on_key_release(key, key_modifiers)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game_manager = GameManager(window, GameView)
    game_manager.show_start_screen()
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()

```