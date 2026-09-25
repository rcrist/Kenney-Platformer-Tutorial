import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Kenney Platformer Tutorial"
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 360

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.SKY_BLUE
        self.camera = arcade.Camera2D(
            viewport=arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            projection=arcade.LBWH(0, 0, CAMERA_WIDTH, CAMERA_HEIGHT),
            position=(0,0),
        )

        self.player = arcade.Sprite(':resources:/images/animated_characters/male_person/malePerson_idle.png')
        self.player.position = (CAMERA_WIDTH/2, CAMERA_HEIGHT/2)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.player_list.draw(pixelated=True)

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()
