import arcade
import sys
from pathlib import Path

# Allow this tutorial file to be run directly from its subdirectory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from library import GameCamera, HudCamera, Player
from library.game_manager import GameManager
from library.audio_manager import PlayerSoundManager
from library.lighting import LightingManager
from library.settings import *

WINDOW_TITLE = "Kenney Platformer Tutorial"
class GameView(arcade.View):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager

        self.background_color = arcade.color.SKY_BLUE
        self.camera = GameCamera()
        self.game_manager.configure_camera(self.camera)
        self.hud_camera = HudCamera()

        # Create a player
        self.player = Player()
        self.player_sound_manager = PlayerSoundManager()
        self.player.sound_manager = self.player_sound_manager
        self.game_manager.restore_player_state(self.player, self.hud_camera)
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)

        self.level = self.game_manager.create_level()
        self.level.sound_manager = self.player_sound_manager
        self.game_manager.configure_player(self.player)
        self.level.level_setup(self.player, self.camera)

        self.enemy_list = self.level.enemy_list
        self.level.enemy_manager.sound_manager = self.player_sound_manager
        self.physics_manager = self.level.physics_manager
        self.leaf_manager = self.level.leaf_manager
        self.dust_manager = self.level.dust_manager
        self.lighting_manager = LightingManager(self.level.name, self.player)

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.lighting_manager.draw(self.draw_world)
        self.player.draw_health_bar()
        for enemy in self.enemy_list:
            enemy.draw_health_bar()

        self.hud_camera.draw()

    def draw_world(self):
        self.camera.draw_background()
        self.level.scene.draw(pixelated=True)
        self.dust_manager.draw()

    def on_update(self, delta_time):
        player_was_moving_up = self.player.change_y > 0
        self.physics_manager.update_player()
        self.level.check_for_block_hit(self.player, player_was_moving_up)
        self.player.keep_in_level(self.level.tile_map)

        if self.game_manager.check_for_player_death(self.player):
            return

        if self.level.check_for_exit(self.player):
            self.game_manager.complete_level(self.player)
            return

        self.level.collect_coins(self.player, self.hud_camera)
        self.level.collect_stars(self.player, self.hud_camera)
        self.level.collect_health(self.player)
        self.level.check_for_hazard_collision(self.player)
        if self.game_manager.check_for_player_death(self.player):
            return

        self.physics_manager.update_enemies()
        self.level.enemy_manager.check_for_enemy_collision(
            self.player,
            self.level.lock_list,
            self.physics_manager,
        )
        if self.game_manager.check_for_player_death(self.player):
            return

        for enemy in self.enemy_list:
            enemy.on_update(delta_time)

        self.level.scene.update_animation(delta_time)
        self.player.update_state(
            delta_time,
            on_moving_platform=self.physics_manager.player_on_moving_platform,
        )
        self.player_sound_manager.update(
            delta_time,
            walking=self.player.change_x != 0,
            grounded=self.physics_manager.player_is_grounded,
        )
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.dust_manager.update(
            delta_time,
            grounded=self.physics_manager.player_is_grounded,
        )
        self.camera.follow(self.player)
        self.level.enemy_manager.check_for_boss_in_viewport(self.camera)
        self.lighting_manager.update()
        self.leaf_manager.update(delta_time, self.camera)

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.W, arcade.key.UP, arcade.key.SPACE):
            if self.physics_manager.jump():
                self.dust_manager.spawn_jump()
                self.player_sound_manager.play_jump()
                     
        self.player.on_key_press(key, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        self.player.on_key_release(key, key_modifiers)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game_manager = GameManager(window, GameView)
    game_manager.show_start_screen()
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()
