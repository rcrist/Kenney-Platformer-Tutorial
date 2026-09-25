![[Pasted image 20260922085738.png]]

```python
import arcade

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_TITLE = "Ninja Game Arcade"

DARK_BLUE = (0, 50, 155)
LIGHT_BLUE = (0, 100, 255)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.SKY_BLUE
        self.movement = [False, False]  # [UP, DOWN]

        self.cloud1 = arcade.Sprite("data/images/clouds/cloud_1.png")
        self.cloud1.scale = 1.0
        self.cloud1.center_x = 160
        self.cloud1.center_y = 260     

        self.cloud_list = arcade.SpriteList()
        self.cloud_list.append(self.cloud1)

        self.rectangle = arcade.SpriteSolidColor(300, 50, arcade.color.WHITE)
        self.rectangle.scale = 1.0
        self.rectangle.position = (200, WINDOW_HEIGHT - 75)
        self.rectangle.color = DARK_BLUE

        self.rectangle_list = arcade.SpriteList()
        self.rectangle_list.append(self.rectangle)

    def reset(self):
        """Reset the game to the initial state."""
        pass

    def on_draw(self):
        self.clear()
        self.rectangle_list.draw()
        self.cloud_list.draw()

    def on_update(self, delta_time):
        self.cloud1.center_y += (self.movement[1] - self.movement[0]) * 5

        if arcade.check_for_collision(self.rectangle, self.cloud1):
            self.rectangle.color = LIGHT_BLUE
        else:
            self.rectangle.color = DARK_BLUE

    def on_key_press(self, key, key_modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.movement[1] = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.movement[0] = True

    def on_key_release(self, key, key_modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.movement[1] = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.movement[0] = False


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