New Level 3 Concept Image
![[Pasted image 20260924153006.png|634]]

## AI Generated Background Image
---
![[Pasted image 20260924153143.png|750]]

## Test Level
---
![[Pasted image 20260924154706.png|1000]]

Tileset is from Kenny > Platformer Assets Tile Extensions > PNG Grass

Level 03 - Tilemap
Map Size: 60x20 Tiles (10 tiles wider than Level 02)
Tile Size: 70x70 px

![[Pasted image 20260925060601.png]]


<video src=20260925-1206-32.1621165.mp4 controls width="1000"></video>

```python title=game.py
...

    def load_enemies(self):
        """Replace tilemap enemy markers with runtime enemy sprites."""
        enemy_list = arcade.SpriteList()
        try:
            enemy_markers = self.level.scene.get_sprite_list("Enemies")
        except KeyError:
            enemy_markers = ()
        tile_distance = self.level.tile_map.tile_width * self.level.tile_map.scaling

        for marker in enemy_markers:
            properties = marker.properties
            enemy_type_value = properties.get("type")
            if not isinstance(enemy_type_value, str):
                print("Skipping enemy marker with no type")
                continue

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
                enemy.scale = 1.0 if enemy_type in ("boss_ghost", "boss_block") else 0.5
                enemy.is_flying = enemy_type in ("bat", "fly")
            else:
                print(f"Skipping unknown enemy type: {enemy_type}")
                continue

            enemy.position = marker.position
            enemy.change_x = properties.get("change_x", ENEMY_SPEED)

            if "boundary_left" in properties and "boundary_right" in properties:
                enemy.set_patrol_range(
                    marker.center_x - properties["boundary_left"] * tile_distance,
                    marker.center_x + properties["boundary_right"] * tile_distance,
                )

            enemy_list.append(enemy)

        if "Enemies" in self.level.scene:
            self.level.scene.remove_sprite_list_by_name("Enemies")
        self.level.scene.add_sprite_list("Enemies", sprite_list=enemy_list)
        return enemy_list

...
```

```python title=enemy.py
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
        invert_facing=False,
    ):
        self.animation_player = AnimationPlayer()

        if idle_path is not None and walk_paths is not None:
            self.idle_textures = self._load_texture_files([idle_path], invert_facing)
            self.walk_textures = self._load_texture_files(walk_paths, invert_facing)
        else:
            self.idle_textures = load_textures(file_path, 1)
            self.walk_textures = load_textures(file_path, num_walk_textures)

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
            return

        self.health = max(0, self.health - amount)
        self.damage_cooldown = 1.0

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
        

```