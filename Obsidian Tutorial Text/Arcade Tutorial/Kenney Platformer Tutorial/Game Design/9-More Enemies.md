![[Pasted image 20260923112954.png|1000]]

```python title=game.py hl=42-70
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

        self.robot_goomba2 = Enemy(
            "assets/kenney_assets/Robot Pack/PNG/Side view/robot_greenDrive{i}.png",
            2
        )
        self.robot_goomba2.scale = 0.2
        self.robot_goomba2.position = (256, 100)
        self.robot_goomba2.set_patrol_range(64)
        self.enemy_list.append(self.robot_goomba2)
        self.level.scene.add_sprite_list("Enemies", sprite_list=self.enemy_list)

        self.robot_goomba3 = Enemy(
            "assets/kenney_assets/Robot Pack/PNG/Side view/robot_redDrive{i}.png",
            2
        )
        self.robot_goomba3.scale = 0.2
        self.robot_goomba3.position = (192, 100)
        self.robot_goomba3.set_patrol_range(64)
        self.enemy_list.append(self.robot_goomba3)
        self.level.scene.add_sprite_list("Enemies", sprite_list=self.enemy_list)

        self.robot_goomba4 = Enemy(
            "assets/kenney_assets/Robot Pack/PNG/Side view/robot_yellowDrive{i}.png",
            2
        )
        self.robot_goomba4.scale = 0.2
        self.robot_goomba4.position = (322, 100)
        self.robot_goomba4.set_patrol_range(64)
        self.enemy_list.append(self.robot_goomba4)
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