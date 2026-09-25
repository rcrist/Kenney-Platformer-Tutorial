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
