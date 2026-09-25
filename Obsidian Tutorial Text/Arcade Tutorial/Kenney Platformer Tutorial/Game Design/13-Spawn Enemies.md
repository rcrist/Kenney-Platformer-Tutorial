Remove the manually placed enemies in game.py. The Tiled tilemap has an Enemies object layer which defines spawn positions for each enemy in the level. Each spawn position has custom properties that define the patrol start and stop boundaries. They also have a type so that each can be give a unique string.  In this update, the Enemies are spawned automatically when the level is loaded using the following spawn list.

- `robot1` → blue robot
- `robot2` → green robot
- `robot3` → red robot

![[Pasted image 20260923145016.png|1000]]

```python title=game.py hl=16-20,40-41,43-51,83-103,118-119
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, HudCamera, Level, Player, Enemy
from library.settings import *
from library import Grass, Reeds, Bush, Tree

WINDOW_TITLE = "Kenney Platformer Tutorial"

ENEMY_TEXTURES = {
    "robot1": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_blueDrive{i}.png",
    "robot2": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_greenDrive{i}.png",
    "robot3": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_redDrive{i}.png",
}

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.SKY_BLUE
        self.camera = GameCamera()
        self.hud_camera = HudCamera()

        # Create a player
        self.player = Player()
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)
        self.player.scale = 0.5

        # Create the level from a Tiled tilemap
        self.level = Level()
        self.level.scene.add_sprite("Player", self.player)
        self.camera.set_limits_to_tilemap(self.level.tile_map)

        self.enemy_list = self.load_enemies()
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

        # Add animated grass to the scene
        self.nature_list = arcade.SpriteList()
        grass = Grass(100, 80)
        grass.scale = 0.1
        self.nature_list.append(grass)

        reeds = Reeds(50, 80)
        reeds.scale = 0.1
        self.nature_list.append(reeds)

        bush = Bush(256, 85)
        bush.scale = 0.1
        self.nature_list.append(bush)

        tree = Tree(300, 85)
        tree.scale = 0.1
        self.nature_list.append(tree)

        self.level.scene.add_sprite_list("Nature", sprite_list=self.nature_list)

    def load_enemies(self):
        enemy_list = arcade.SpriteList()

        for enemy_object in self.level.tile_map.object_lists["Enemies"]:
            properties = enemy_object.properties
            enemy_type = properties["type"]

            if enemy_type not in ENEMY_TEXTURES:
                raise ValueError(f"Unknown enemy type in tilemap: {enemy_type}")

            enemy = Enemy(ENEMY_TEXTURES[enemy_type], 2)
            enemy.scale = 0.2
            enemy.position = enemy_object.shape
            enemy.change_x = properties.get("change_x", ENEMY_SPEED)
            enemy.set_patrol_range(
                properties["boundary_left"],
                properties["boundary_right"],
            )
            enemy_list.append(enemy)

        return enemy_list

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.level.scene.draw(pixelated=True)

        self.hud_camera.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.collect_coins()

        for physics_engine in self.enemy_physics_engines:
            physics_engine.update()
        for enemy in self.enemy_list:
            enemy.on_update(delta_time)

        self.level.scene.update_animation(delta_time)
        self.player.update_state(delta_time)
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.camera.follow(self.player)

    def collect_coins(self):
        coins_hit = arcade.check_for_collision_with_list(
            self.player,
            self.level.scene["Coins"],
        )

        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.player.coins += 1
            self.hud_camera.set_score(self.player.coins)

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

```python title=enemy.py hl=30-33,
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

    def set_patrol_range(self, boundary_left, boundary_right):
        """Set the enemy's patrol limits in world coordinates."""
        self.patrol_left = boundary_left
        self.patrol_right = boundary_right

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