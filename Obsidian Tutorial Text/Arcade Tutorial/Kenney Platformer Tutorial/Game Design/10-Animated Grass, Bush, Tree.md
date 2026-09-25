![[Pasted image 20260923133656.png|1000]]

```python title=animated_sprites/grass.py
import arcade
from pathlib import Path


GRASS_TEXTURE_DIR = Path(__file__).resolve().parent.parent / "assets/NatureAssets/grass_2"

class Grass(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.textures = [
            arcade.load_texture(GRASS_TEXTURE_DIR / f"{i:04}.png")
            for i in range(1, 17)
        ]

        self.current_frame = 0
        self.texture = self.textures[0]

        self.center_x = x
        self.center_y = y

        self.animation_time = 0.0

    def update_animation(self, delta_time = 1 / 60):
        self.animation_time += delta_time

        if self.animation_time >= 0.12:
            self.animation_time = 0.0

            self.current_frame += 1
            self.current_frame %= len(self.textures)

            self.texture = self.textures[self.current_frame]

```

```python title=animated_sprites/reeds.py
import arcade
from pathlib import Path


GRASS_TEXTURE_DIR = Path(__file__).resolve().parent.parent / "assets/NatureAssets/grass_3"

class Reeds(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.textures = [
            arcade.load_texture(GRASS_TEXTURE_DIR / f"{i:04}.png")
            for i in range(1, 17)
        ]

        self.current_frame = 0
        self.texture = self.textures[0]

        self.center_x = x
        self.center_y = y

        self.animation_time = 0.0

    def update_animation(self, delta_time = 1 / 60):
        self.animation_time += delta_time

        if self.animation_time >= 0.12:
            self.animation_time = 0.0

            self.current_frame += 1
            self.current_frame %= len(self.textures)

            self.texture = self.textures[self.current_frame]

```

```python title=bush.py
import arcade
from pathlib import Path


GRASS_TEXTURE_DIR = Path(__file__).resolve().parent.parent / "assets/NatureAssets/bush_1"

class Bush(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.textures = [
            arcade.load_texture(GRASS_TEXTURE_DIR / f"{i:04}.png")
            for i in range(1, 17)
        ]

        self.current_frame = 0
        self.texture = self.textures[0]

        self.center_x = x
        self.center_y = y

        self.animation_time = 0.0

    def update_animation(self, delta_time = 1 / 60):
        self.animation_time += delta_time

        if self.animation_time >= 0.12:
            self.animation_time = 0.0

            self.current_frame += 1
            self.current_frame %= len(self.textures)

            self.texture = self.textures[self.current_frame]

```

```python title=animated_sprites/tree.py
import arcade
from pathlib import Path


GRASS_TEXTURE_DIR = Path(__file__).resolve().parent.parent / "assets/NatureAssets/tree_1"

class Tree(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.textures = [
            arcade.load_texture(GRASS_TEXTURE_DIR / f"{i:04}.png")
            for i in range(1, 17)
        ]

        self.current_frame = 0
        self.texture = self.textures[0]

        self.center_x = x
        self.center_y = y

        self.animation_time = 0.0

    def update_animation(self, delta_time = 1 / 60):
        self.animation_time += delta_time

        if self.animation_time >= 0.12:
            self.animation_time = 0.0

            self.current_frame += 1
            self.current_frame %= len(self.textures)

            self.texture = self.textures[self.current_frame]

```

```python title=game.py hl=12,93-111
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, Level, Player, Enemy
from library.settings import *
from animated_sprites import Grass, Reeds, Bush, Tree

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

---
There is a lot of duplicated code in these four classes. Here is a consolidated module so I follow the  "Don't Repeat Yourself" software guideline.

```python title=library/nature.py
from pathlib import Path

import arcade


TEXTURE_ROOT = Path(__file__).resolve().parent.parent / "assets" / "NatureAssets"


class AnimatedNatureSprite(arcade.Sprite):
    """Base class for nature sprites that loop through numbered textures."""

    texture_folder: str
    frame_count = 16
    seconds_per_frame = 0.12

    def __init__(self, x: float, y: float):
        super().__init__()

        texture_dir = TEXTURE_ROOT / self.texture_folder
        self.textures = [
            arcade.load_texture(texture_dir / f"{frame:04}.png")
            for frame in range(1, self.frame_count + 1)
        ]
        self.current_frame = 0
        self.texture = self.textures[0]
        self.position = x, y
        self.animation_time = 0.0

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

```

```python title=library/__init__.py
from .camera import GameCamera
from .level import Level
from .player import Player
from .enemy import Enemy
from .settings import *
from .nature import Bush, Grass, Reeds, Tree

```

```python title=game.py hl=12
import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, Level, Player, Enemy
from library.settings import *
from library import Grass, Reeds, Bush, Tree

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