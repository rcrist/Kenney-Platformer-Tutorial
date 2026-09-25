Level 2 "Dark Caves" concept drawing:
![[Pasted image 20260924111559.png]]

## Background
---
The background on this level could be a fixed image but we could use a parallax background. A fixed image is easier for now. I will as AI to create the image.

![C:\arcade_tutorials\kenney_platformer_tutorial\assets\backgrounds\dark_caves.png](file:///c%3A/arcade_tutorials/kenney_platformer_tutorial/assets/backgrounds/dark_caves.png)

That will work!
- Image size: 1672x941 px same as the level 1 background image.

## Test Tilemap
---

Level Map: level_02.json
- Map Size: 20x50 tiles (a little larger than level 1)
- Tile Size: 128x128 px

I will simply replace level 1 with level 2 until we get all levels tested.
- All object layers need to be optional during development - or even for the final level

```python title=game.py
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
    "robot4": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_yellowDrive{i}.png",
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
        self.player.scale = 0.75

        # Create the level from a Tiled tilemap
        self.level = Level()
        self.level.scene.add_sprite("Player", self.player)
        self.camera.set_limits_to_tilemap(self.level.tile_map)
        try:
            self.moving_platforms = self.level.scene["Moving Platforms"]
        except KeyError:
            self.moving_platforms = arcade.SpriteList()
        try:
            self.exit_list = self.level.scene["Exit"]
        except KeyError:
            self.exit_list = arcade.SpriteList()
        self.setup_moving_platforms()

        self.enemy_list = self.load_enemies()

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
            platforms=self.moving_platforms,
            walls=self.level.scene["Platforms"],
            gravity_constant=GRAVITY,
            ladders=self.level.scene["Ladders"],
        )

        self.camera.follow(self.player)

        self.nature_list = self.load_nature()

        self.leaf_list = arcade.SpriteList()
        self.level.scene.add_sprite_list("Leaves", sprite_list=self.leaf_list)
        self.leaves_enabled = self.level.name == "level_01"
        self.next_leaf_time = random.uniform(0.1, 0.5)

        # Tiled layers are initially drawn before sprite lists added in code.
        # Move Foreground to the end so it appears in front of the player.
        if "Foreground" in self.level.scene:
            self.level.scene.move_sprite_list_after("Foreground", "Leaves")

    def load_nature(self):
        """Replace tilemap markers with the matching animated sprites."""
        nature_classes = {
            "Grass": Grass,
            "Tree": Tree,
            "Bush": Bush,
            "Reed": Reeds,
        }
        nature_list = arcade.SpriteList()
        try:
            nature_markers = self.level.scene.get_sprite_list("Nature")
        except KeyError:
            nature_markers = ()

        for marker in nature_markers:
            nature_type = marker.properties.get("Type")
            nature_class = nature_classes.get(nature_type)
            if nature_class is None:
                raise ValueError(f"Unknown nature type in tilemap: {nature_type}")

            nature = nature_class(marker.center_x, marker.center_y - 10)
            nature.scale = 0.1
            nature_list.append(nature)

        if "Nature" in self.level.scene:
            self.level.scene.remove_sprite_list_by_name("Nature")
        self.level.scene.add_sprite_list("Nature", sprite_list=nature_list)
        return nature_list

    def setup_moving_platforms(self):
        """Configure vertical movement from the platform custom properties."""
        tile_distance = self.level.tile_map.tile_height * self.level.tile_map.scaling

        for platform in self.moving_platforms:
            properties = platform.properties
            if "Top" not in properties or "Bottom" not in properties:
                continue

            platform.boundary_top = platform.top + properties["Top"] * tile_distance
            platform.boundary_bottom = platform.bottom - properties["Bottom"] * tile_distance
            platform.change_y = MOVING_PLATFORM_SPEED

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
            enemy_type = properties["type"]

            if enemy_type not in ENEMY_TEXTURES:
                raise ValueError(f"Unknown enemy type in tilemap: {enemy_type}")

            enemy = Enemy(ENEMY_TEXTURES[enemy_type], 2)
            enemy.scale = 0.3
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

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.camera.draw_background()
        self.level.scene.draw(pixelated=True)
        self.player.draw_health_bar()
        for enemy in self.enemy_list:
            enemy.draw_health_bar()

        self.hud_camera.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.keep_player_in_level()

        if self.check_for_exit():
            return

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
        if self.leaves_enabled:
            self.update_leaves(delta_time)

    def keep_player_in_level(self):
        """Keep the player's entire sprite inside the tilemap bounds."""
        tile_map = self.level.tile_map
        map_left = tile_map.offset.x
        map_bottom = tile_map.offset.y
        map_right = map_left + tile_map.width * tile_map.tile_width * tile_map.scaling
        map_top = map_bottom + tile_map.height * tile_map.tile_height * tile_map.scaling

        if self.player.left < map_left:
            self.player.left = map_left
            self.player.change_x = 0
        elif self.player.right > map_right:
            self.player.right = map_right
            self.player.change_x = 0

        if self.player.bottom < map_bottom:
            self.player.bottom = map_bottom
            self.player.change_y = 0
        elif self.player.top > map_top:
            self.player.top = map_top
            self.player.change_y = 0

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

    def check_for_exit(self):
        """Restart the game when the player reaches an Exit marker."""
        exits_hit = arcade.check_for_collision_with_list(
            self.player,
            self.exit_list,
        )

        if any(exit_marker.properties.get("type") == "Exit" for exit_marker in exits_hit):
            print("You reached the exit!")
            self.window.show_view(GameView())
            return True

        return False

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

`Stone.tsx` from the Kenney New Platformer Pack
![[Pasted image 20260924120033.png]]

Tile size: 128x128 px

level_02.json
![[Pasted image 20260924120147.png]]

![[Pasted image 20260924120220.png|1000]]

Looks good, so far...

## Level 2 Tilemap
---
level_02.json
![[Pasted image 20260924133415.png]]

Layers
![[Pasted image 20260924133454.png]]


<video src=20260924-1935-31.2261225.mp4 controls width="1000"></video>
