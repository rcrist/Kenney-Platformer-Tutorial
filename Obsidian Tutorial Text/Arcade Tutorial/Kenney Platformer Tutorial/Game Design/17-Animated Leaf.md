![[Pasted image 20260923153856.png|1000]]

The leaves are too simple but will work for now. TODO: Find a better leaf model.

```python title=nature.py hl=2,7-8,14,17-18,20,25,27-33,35-38,40-44,71-88
from pathlib import Path
import random

import arcade


ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
NATURE_TEXTURE_ROOT = ASSET_ROOT / "NatureAssets"


class AnimatedNatureSprite(arcade.Sprite):
    """Base class for nature sprites that loop through numbered textures."""

    texture_root = NATURE_TEXTURE_ROOT
    texture_folder: str
    frame_count = 16
    first_frame = 1
    filename_digits = 4
    seconds_per_frame = 0.12
    randomize_animation = False

    def __init__(self, x: float, y: float):
        super().__init__()

        texture_dir = self.texture_root / self.texture_folder
        self.textures = [
            arcade.load_texture(
                texture_dir / f"{frame:0{self.filename_digits}}.png"
            )
            for frame in range(
                self.first_frame,
                self.first_frame + self.frame_count,
            )
        ]
        self.current_frame = (
            random.randrange(self.frame_count) if self.randomize_animation else 0
        )
        self.texture = self.textures[self.current_frame]
        self.position = x, y
        self.animation_time = (
            random.uniform(0, self.seconds_per_frame)
            if self.randomize_animation
            else 0.0
        )

    def update_animation(self, delta_time: float = 1 / 60):
        self.animation_time += delta_time

        if self.animation_time >= self.seconds_per_frame:
            self.animation_time = 0.0
            self.current_frame = (self.current_frame + 1) % len(self.textures)
            self.texture = self.textures[self.current_frame]


class Grass(AnimatedNatureSprite):
    texture_folder = "grass_2"


class Reeds(AnimatedNatureSprite):
    texture_folder = "grass_3"


class Bush(AnimatedNatureSprite):
    texture_folder = "bush_1"


class Tree(AnimatedNatureSprite):
    texture_folder = "tree_1"


class Leaf(AnimatedNatureSprite):
    texture_root = ASSET_ROOT
    texture_folder = "leaf"
    frame_count = 18
    first_frame = 0
    filename_digits = 2
    randomize_animation = True

    def __init__(self, x: float, y: float):
        self.seconds_per_frame = random.uniform(0.06, 0.16)
        super().__init__(x, y)
        self.scale = 2
        self.fall_speed = random.uniform(20, 45)
        self.drift_speed = random.uniform(-12, 12)

    def on_update(self, delta_time: float):
        self.center_x += self.drift_speed * delta_time
        self.center_y -= self.fall_speed * delta_time

```

```python title=library/__init__.py hl=7
from .camera import GameCamera
from .hud_camera import HudCamera
from .level import Level
from .player import Player
from .enemy import Enemy
from .settings import *
from .nature import Bush, Grass, Leaf, Reeds, Tree
from .animation_player import AnimationPlayer

```

```python title=game.py hl=2,13,16,85-87,136,138-158
import arcade
import random
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, HudCamera, Level, Player, Enemy
from library.settings import *
from library import Grass, Reeds, Bush, Tree, Leaf

WINDOW_TITLE = "Kenney Platformer Tutorial"
MAX_LEAVES = 20

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

        tree = Tree(300, 110)
        tree.scale = 0.2
        self.nature_list.append(tree)

        self.level.scene.add_sprite_list("Nature", sprite_list=self.nature_list)

        self.leaf_list = arcade.SpriteList()
        self.level.scene.add_sprite_list("Leaves", sprite_list=self.leaf_list)
        self.next_leaf_time = random.uniform(0.1, 0.5)

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
        self.player.draw_health_bar()
        for enemy in self.enemy_list:
            enemy.draw_health_bar()

        self.hud_camera.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.collect_coins()

        for physics_engine in self.enemy_physics_engines:
            physics_engine.update()
        self.check_for_enemy_collision()

        for enemy in self.enemy_list:
            enemy.on_update(delta_time)

        self.level.scene.update_animation(delta_time)
        self.player.update_state(delta_time)
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.camera.follow(self.player)
        self.update_leaves(delta_time)

    def update_leaves(self, delta_time):
        camera_x, camera_y = self.camera.position
        bottom = camera_y - CAMERA_HEIGHT / 2

        for leaf in tuple(self.leaf_list):
            leaf.on_update(delta_time)
            if leaf.top < bottom:
                leaf.remove_from_sprite_lists()

        self.next_leaf_time -= delta_time
        if self.next_leaf_time <= 0:
            self.next_leaf_time = random.uniform(0.1, 0.5)

            if len(self.leaf_list) < MAX_LEAVES:
                left = camera_x - CAMERA_WIDTH / 2
                top = camera_y + CAMERA_HEIGHT / 2
                leaf = Leaf(
                    random.uniform(left, left + CAMERA_WIDTH),
                    top + 8,
                )
                self.leaf_list.append(leaf)

    def collect_coins(self):
        coins_hit = arcade.check_for_collision_with_list(
            self.player,
            self.level.scene["Coins"],
        )

        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.player.coins += 1
            self.hud_camera.set_score(self.player.coins)

    def check_for_enemy_collision(self):
        enemies_hit = arcade.check_for_collision_with_list(
            self.player,
            self.enemy_list,
        )

        if enemies_hit:
            self.player.take_damage(10)
            for enemy in enemies_hit:
                enemy.take_damage(25)
                if enemy.health <= 0:
                    enemy.remove_from_sprite_lists()

            self.enemy_physics_engines = [
                physics_engine
                for physics_engine in self.enemy_physics_engines
                if physics_engine.player_sprite.health > 0
            ]

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