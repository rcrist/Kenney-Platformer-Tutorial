![[Pasted image 20260922090054.png]]

```python
import arcade

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_TITLE = "Arcade Tutorial"


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = (14, 219, 248)  # RGB value for sky color

        self.cloud1 = arcade.Sprite("data/images/clouds/cloud_1.png")
        self.cloud1.scale = 1.0
        self.cloud1.center_x = 160
        self.cloud1.center_y = 260     

        self.cloud_list = arcade.SpriteList()
        self.cloud_list.append(self.cloud1)

    def on_draw(self):
        self.clear()
        self.cloud_list.draw()


def main():
    """ Main function """
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()
    game = GameView()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()

```