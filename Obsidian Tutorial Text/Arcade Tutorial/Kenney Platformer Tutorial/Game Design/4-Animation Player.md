![[Pasted image 20260922140017.png|1000]]

```python title=animation_player.py
import arcade

from .settings import UPDATES_PER_FRAME

class AnimationPlayer:
    def __init__(self):
        self.cur_texture = 0

    def update_animation(self, texture_list, num_textures, direction) -> arcade.Texture:
        # Assume this function is called in the on_update() method and updates every frame
        self.cur_texture += 1
        frame = (self.cur_texture // UPDATES_PER_FRAME) % num_textures
        texture = texture_list[frame][direction]

        return texture

```

```python title=player.py hl=5,13,15-18,30-38
import arcade
from enum import Enum

from .settings import PLAYER_SPEED
from .animation_player import AnimationPlayer

class Dir(Enum):
    RIGHT = 0
    LEFT = 1

class Player(arcade.Sprite):
    def __init__(self):
        self.animation_player = AnimationPlayer()

        # Create idle textures facing left and right
        self.idle_textures = []
        idle_texture = arcade.load_texture(':resources:/images/animated_characters/male_person/malePerson_idle.png')
        self.idle_textures.append((idle_texture, idle_texture.flip_left_right()))  # Index 0 = right, index 1 = left

        # Create walk animation textures for left and right
        self.walk_textures = []
        for i in range(8):
            texture = arcade.load_texture(f":resources:/images/animated_characters/male_person/malePerson_walk{i}.png")
            self.walk_textures.append((texture, texture.flip_left_right()))

        super().__init__(idle_texture)

        self.current_direction = Dir.RIGHT

    def on_update(self, delta_time):
        if self.change_x == 0:
            self.texture = self.animation_player.update_animation(
                self.idle_textures, len(self.idle_textures), self.current_direction.value
            )
        else:
            self.texture = self.animation_player.update_animation(
                self.walk_textures, len(self.walk_textures), self.current_direction.value
            )
        
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