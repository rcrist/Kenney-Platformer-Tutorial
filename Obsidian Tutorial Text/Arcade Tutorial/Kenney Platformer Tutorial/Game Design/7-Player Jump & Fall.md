![[Pasted image 20260923083955.png|1000]]

```python title=player.py hl=34-44,61-68,72-81
import arcade
from enum import Enum, auto

from .settings import PLAYER_SPEED
from .animation_player import AnimationPlayer
from .load_textures import load_textures

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

        super().__init__(self.idle_textures[0][Dir.RIGHT.value])

        self.current_direction = Dir.RIGHT
        self.current_state = State.IDLE

    def on_update(self, delta_time):
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

    def update_state(self, delta_time):
        if self.change_y == 0:
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

The current map has animated sprites but the animation is not working. Fixed this bug in the GameView on_update() method.

```python title=10_player_camera.py hl=49
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, Level, Player
from library.settings import *

WINDOW_TITLE = "Kenney Platformer Tutorial"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.SKY_BLUE
        self.camera = GameCamera()

        # Create a player
        self.player = Player()
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)
        self.player.scale = 0.5

        # Create the level from a Tiled tilemap
        self.level = Level()
        self.level.scene.add_sprite("Player", self.player)
        self.camera.set_limits_to_tilemap(self.level.tile_map)

        # Add physics to the game
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.level.scene["Platforms"],
            gravity_constant=GRAVITY,
            ladders=self.level.scene["Ladders"],
        )

        self.camera.follow(self.player)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.level.scene.draw(pixelated=True)

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.level.scene.update_animation(delta_time)
        self.player.update_state(delta_time)
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.camera.follow(self.player)

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            if self.physics_engine.can_jump():
                self.physics_engine.jump(PLAYER_JUMP_SPEED)
                     
        self.player.on_key_press(key, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        self.player.on_key_release(key, key_modifiers)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()

```

Ok, the flags and torches are now animated!
