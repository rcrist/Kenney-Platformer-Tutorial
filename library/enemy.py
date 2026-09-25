import arcade
from enum import Enum

from .animation_player import AnimationPlayer
from .load_textures import load_textures
from .settings import ENEMY_SPEED

class Dir(Enum):
    RIGHT = 0
    LEFT = 1

class Enemy(arcade.Sprite):
    def __init__(
        self,
        file_path=None,
        num_walk_textures=None,
        *,
        idle_path=None,
        walk_paths=None,
        damage_paths=None,
        invert_facing=False,
    ):
        self.animation_player = AnimationPlayer()

        if idle_path is not None and walk_paths is not None:
            self.idle_textures = self._load_texture_files([idle_path], invert_facing)
            self.walk_textures = self._load_texture_files(walk_paths, invert_facing)
        else:
            self.idle_textures = load_textures(file_path, 1)
            self.walk_textures = load_textures(file_path, num_walk_textures)

        self.damage_textures = (
            self._load_texture_files(damage_paths, invert_facing)
            if damage_paths
            else None
        )

        super().__init__(self.walk_textures[0][Dir.RIGHT.value])
        self.current_direction = Dir.RIGHT
        self.change_x = ENEMY_SPEED
        self.patrol_left = None
        self.patrol_right = None
        self.patrol_pause_timer = 0.0
        self.next_change_x = 0
        self.max_health = 100
        self.health = 100
        self.damage_cooldown = 0.0
        self.damage_animation_time = 0.0
        self.damage_animation_elapsed = 0.0
        self.is_flying = False

    @staticmethod
    def _load_texture_files(file_paths, invert_facing=False):
        textures = []
        for file_path in file_paths:
            texture = arcade.load_texture(file_path)
            flipped_texture = texture.flip_left_right()
            if invert_facing:
                textures.append((flipped_texture, texture))
            else:
                textures.append((texture, flipped_texture))
        return textures

    def set_patrol_range(self, boundary_left, boundary_right):
        """Set the enemy's patrol limits in world coordinates."""
        self.patrol_left = boundary_left
        self.patrol_right = boundary_right

    def on_update(self, delta_time):
        self.damage_cooldown = max(0.0, self.damage_cooldown - delta_time)

        if self.damage_animation_time > 0 and self.damage_textures:
            self.damage_animation_time = max(
                0.0,
                self.damage_animation_time - delta_time,
            )
            self.damage_animation_elapsed += delta_time
            frame_duration = 0.15
            frame = min(
                int(self.damage_animation_elapsed / frame_duration),
                len(self.damage_textures) - 1,
            )
            self.texture = self.damage_textures[frame][self.current_direction.value]
            return

        if self.patrol_pause_timer > 0:
            self.patrol_pause_timer -= delta_time
            self.change_x = 0

            self.texture = self.animation_player.update_animation(
                self.idle_textures, len(self.idle_textures), self.current_direction.value
            )

            if self.patrol_pause_timer <= 0:
                self.change_x = self.next_change_x
                self.next_change_x = 0
            return

        if self.patrol_left is not None and self.patrol_right is not None:
            if self.center_x <= self.patrol_left and self.change_x < 0:
                self.center_x = self.patrol_left
                self.next_change_x = abs(ENEMY_SPEED)
                self.change_x = 0
                self.patrol_pause_timer = 1.0
            elif self.center_x >= self.patrol_right and self.change_x > 0:
                self.center_x = self.patrol_right
                self.next_change_x = -abs(ENEMY_SPEED)
                self.change_x = 0
                self.patrol_pause_timer = 1.0

        if self.change_x == 0:  # Idle state
            self.texture = self.animation_player.update_animation(
                self.idle_textures, len(self.idle_textures), self.current_direction.value
            )
        else:  # Walk state
            self.current_direction = Dir.RIGHT if self.change_x > 0 else Dir.LEFT
            self.texture = self.animation_player.update_animation(
                self.walk_textures, len(self.walk_textures), self.current_direction.value
            )

    def take_damage(self, amount):
        """Reduce health once per cooldown period."""
        if self.damage_cooldown > 0 or self.health <= 0:
            return False

        self.health = max(0, self.health - amount)
        self.damage_cooldown = 1.0
        if self.damage_textures:
            self.damage_animation_time = 0.3
            self.damage_animation_elapsed = 0.0
        return True

    def draw_health_bar(self):
        """Draw a small health bar just above the enemy."""
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
            arcade.color.RED,
        )
        
