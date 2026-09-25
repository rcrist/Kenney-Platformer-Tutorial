Add a walk animation when the player moves left or right. Arcade built-in resources includes walk animation sprites for our player.

The walk animation images are at `:resources:/images/animated_characters/male_person/malePerson_walk0.png` to `:resources:/images/animated_characters/male_person/malePerson_walk7.png`.

We will load all 8 images into a list, create a flipped list for player direction, set the animation speed and identify the current animation based on the frame time.

![[Pasted image 20260922120758.png|1000]]

```python title=player.py hl=18-22,28-46
import arcade
from enum import Enum, auto

from .settings import PLAYER_SPEED, UPDATES_PER_FRAME

class Dir(Enum):
    RIGHT = 0
    LEFT = 1

class Player(arcade.Sprite):
    def __init__(self):
        self.cur_texture = 0

        # Create idle textures facing left and right
        idle_texture = arcade.load_texture(':resources:/images/animated_characters/male_person/malePerson_idle.png')
        self.idle_textures = [idle_texture, idle_texture.flip_left_right()] # Index 0 = right, index 1 = left

        # Create the walk animation textures for left and right
        self.walk_textures = []
        for i in range(8):
            texture = arcade.load_texture(f":resources:/images/animated_characters/male_person/malePerson_walk{i}.png")
            self.walk_textures.append((texture, texture.flip_left_right()))

        super().__init__(idle_texture)

        self.current_direction = Dir.RIGHT

    def on_update(self, delta_time):
        # Idle animation
        if self.change_x == 0:
            match self.current_direction:
                case Dir.LEFT:
                    self.texture = self.idle_textures[1]
                case Dir.RIGHT:
                    self.texture = self.idle_textures[0]
                case _:
                    self.texture = self.idle_textures[0]

        # Walk animation
        if self.change_x != 0:
            self.cur_texture += 1
            if self.cur_texture > 7 * UPDATES_PER_FRAME:  # Animation end detector
                self.cur_texture = 0

            frame = self.cur_texture // UPDATES_PER_FRAME  # Selects the current anim frame
            self.texture = self.walk_textures[frame][self.current_direction.value]
        
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

