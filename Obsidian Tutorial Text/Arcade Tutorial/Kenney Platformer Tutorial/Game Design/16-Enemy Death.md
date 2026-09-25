![[Pasted image 20260923152255.png|1000]]

```python title=game.py hl=152-153,158
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