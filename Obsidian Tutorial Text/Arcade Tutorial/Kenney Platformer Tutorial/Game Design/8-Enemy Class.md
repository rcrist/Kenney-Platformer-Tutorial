![[Pasted image 20260923095106.png|1000]]

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
    def __init__(self, file_path, num_walk_textures):
        self.animation_player = AnimationPlayer()

        # Idle textures
        self.idle_textures = load_textures(file_path, 1)

        # Walk textures
        self.walk_textures = load_textures(file_path, num_walk_textures)

        super().__init__(self.walk_textures[0][Dir.RIGHT.value])
        self.current_direction = Dir.RIGHT
        self.change_x = ENEMY_SPEED
        self.patrol_left = None
        self.patrol_right = None
        self.patrol_pause_timer = 0.0
        self.next_change_x = 0

    def set_patrol_range(self, distance):
        """Set patrol limits relative to the enemy's current position."""
        self.patrol_left = self.center_x - distance
        self.patrol_right = self.center_x + distance

    def on_update(self, delta_time):
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

```

```python title=game.py hl=10,32-41,43-51,70-73
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, Level, Player, Enemy
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

        self.robot_goomba1 = Enemy(
            "assets/kenney_assets/Robot Pack/PNG/Side view/robot_blueDrive{i}.png",
            2
        )
        self.robot_goomba1.scale = 0.2
        self.robot_goomba1.position = (128, 100)
        self.robot_goomba1.set_patrol_range(64)
        self.enemy_list = arcade.SpriteList()
        self.enemy_list.append(self.robot_goomba1)
        self.level.scene.add_sprite_list("Enemies", sprite_list=self.enemy_list)

        self.enemy_physics_engines = [
            arcade.PhysicsEnginePlatformer(
                enemy,
                walls=self.level.scene["Platforms"],
                gravity_constant=GRAVITY,
                ladders=self.level.scene["Ladders"],
            )
            for enemy in self.enemy_list
        ]

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
        for physics_engine in self.enemy_physics_engines:
            physics_engine.update()
        for enemy in self.enemy_list:
            enemy.on_update(delta_time)

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