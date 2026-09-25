![[Pasted image 20260922140017.png|1000]]

```python title=load_textures.py
import arcade


def load_textures(file_path, num_textures):
    textures = []

    for i in range(num_textures):
        texture = arcade.load_texture(file_path.format(i=i))
        textures.append((texture, texture.flip_left_right()))  # Index 0 = right, index 1 = left

    return textures

```

```python title=player.py hl=6,16-20,22-26,28
import arcade
from enum import Enum

from .settings import PLAYER_SPEED
from .animation_player import AnimationPlayer
from .load_textures import load_textures

class Dir(Enum):
    RIGHT = 0
    LEFT = 1

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

        super().__init__(self.idle_textures[0][Dir.RIGHT.value])

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