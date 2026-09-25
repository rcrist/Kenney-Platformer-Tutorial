```python title=audio_manager.py
import arcade
import random
from pathlib import Path


AUDIO_ROOT = (
    Path(__file__).resolve().parent.parent
    / "assets/kenney_assets/audio/Impact Sounds"
)


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

    def __init__(self, volume=0.35):
        self.volume = volume
        self.footstep_timer = 0.0
        self.footsteps = self._load_sounds(
            "Audio", "footstep_grass", range(5), separator="_", number_width=3
        )
        self.jumps = self._load_sounds(
            "Retro Sounds 2/Audio", "jump", range(1, 4)
        )
        self.hurts = self._load_sounds(
            "Retro Sounds 2/Audio", "hurt", range(1, 4)
        )

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
        self.game_manager.configure_player(self.player)
        self.level.level_setup(self.player, self.camera)

        self.enemy_list = self.level.enemy_list
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

```python title=player.py
import arcade
from enum import Enum, auto
from pathlib import Path

from .settings import PLAYER_SPEED
from .animation_player import AnimationPlayer
from .load_textures import load_textures


PLAYER_HIT_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets/kenney_assets/Toon Characters/Male person/PNG/Poses"
    / "character_malePerson_hit.png"
)

class Dir(Enum):
    RIGHT = 0
    LEFT = 1

class State(Enum):
    IDLE = auto()
    WALK = auto()
    JUMP = auto()
    FALL = auto()

class Player(arcade.Sprite):
    def __init__(self):
        self.animation_player = AnimationPlayer()

        # Create idle textures facing left and right
        self.idle_textures = load_textures(
            ':resources:/images/animated_characters/male_person/malePerson_idle.png', 
            1
        )

        # Create walk animation textures for left and right
        self.walk_textures = load_textures(
            ":resources:/images/animated_characters/male_person/malePerson_walk{i}.png",
            8
        )

        # Jump textures
        self.jump_textures = load_textures(
            ":resources:/images/animated_characters/male_person/malePerson_jump.png",
            1
        )

        # Fall textures
        self.fall_textures = load_textures(
            ":resources:/images/animated_characters/male_person/malePerson_fall.png",
            1
        )

        hit_texture = arcade.load_texture(PLAYER_HIT_PATH)
        self.hit_textures = (hit_texture, hit_texture.flip_left_right())

        super().__init__(self.idle_textures[0][Dir.RIGHT.value])

        self.current_direction = Dir.RIGHT
        self.current_state = State.IDLE
        self.coins = 0
        self.max_health = 100
        self.health = 100
        self.damage_cooldown = 0.0
        self.hit_animation_time = 0.0
        self.sound_manager = None

    def on_update(self, delta_time):
        self.damage_cooldown = max(0.0, self.damage_cooldown - delta_time)

        if self.hit_animation_time > 0:
            self.hit_animation_time = max(0.0, self.hit_animation_time - delta_time)
            self.texture = self.hit_textures[self.current_direction.value]
            return

        match self.current_state:
            case State.IDLE:
                self.texture = self.animation_player.update_animation(
                    self.idle_textures, len(self.idle_textures), self.current_direction.value
                )
            case State.WALK:
                self.texture = self.animation_player.update_animation(
                    self.walk_textures, len(self.walk_textures), self.current_direction.value
                )
            case State.JUMP:
                self.texture = self.animation_player.update_animation(
                    self.jump_textures, len(self.jump_textures), self.current_direction.value
                )
            case State.FALL:
                self.texture = self.animation_player.update_animation(
                    self.fall_textures, len(self.fall_textures), self.current_direction.value
                )               
            case _:
                pass

    def take_damage(self, amount):
        """Reduce health once per cooldown period."""
        if self.damage_cooldown > 0 or self.health <= 0:
            return

        self.health = max(0, self.health - amount)
        self.damage_cooldown = 1.0
        self.hit_animation_time = 0.3
        if self.sound_manager is not None:
            self.sound_manager.play_hurt()

    def keep_in_level(self, tile_map):
        """Keep the player's entire sprite inside the tilemap bounds."""
        map_left = tile_map.offset.x
        map_bottom = tile_map.offset.y
        map_right = map_left + tile_map.width * tile_map.tile_width * tile_map.scaling
        map_top = map_bottom + tile_map.height * tile_map.tile_height * tile_map.scaling

        if self.left < map_left:
            self.left = map_left
            self.change_x = 0
        elif self.right > map_right:
            self.right = map_right
            self.change_x = 0

        if self.bottom < map_bottom:
            self.bottom = map_bottom
            self.change_y = 0
        elif self.top > map_top:
            self.top = map_top
            self.change_y = 0

    def draw_health_bar(self):
        """Draw a small health bar just above the player."""
        bar_width = 32
        bar_height = 4
        left = self.center_x - bar_width / 2
        bottom = self.top + 6
        health_ratio = self.health / self.max_health

        arcade.draw_lbwh_rectangle_filled(
            left - 1,
            bottom - 1,
            bar_width + 2,
            bar_height + 2,
            arcade.color.BLACK,
        )
        arcade.draw_lbwh_rectangle_filled(
            left,
            bottom,
            bar_width * health_ratio,
            bar_height,
            arcade.color.GREEN,
        )

    def update_state(self, delta_time, on_moving_platform=False):
        if self.change_y == 0 or on_moving_platform:
            if self.change_x == 0:
                self.current_state = State.IDLE
            elif self.change_x != 0:
                self.current_state = State.WALK
        elif self.change_y > 0:
            self.current_state = State.JUMP
        elif self.change_y < 0:
            self.current_state = State.FALL
        
    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.current_direction = Dir.LEFT
            self.change_x -= PLAYER_SPEED
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.current_direction = Dir.RIGHT
            self.change_x += PLAYER_SPEED

    def on_key_release(self, key, key_modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.change_x = 0
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.change_x = 0

```