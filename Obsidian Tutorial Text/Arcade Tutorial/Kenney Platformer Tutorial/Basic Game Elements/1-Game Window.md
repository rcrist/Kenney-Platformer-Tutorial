![[Pasted image 20260922094113.png|1000]]

```python title=1_game_window.py
import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Kenney Platformer Tutorial - Game Window"

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.SKY_BLUE

    def on_draw(self):
        self.clear()

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.center_window()

    game = GameView()
    window.show_view(game)
    arcade.run()  # Runs the Arcade game loop

if __name__ == "__main__":
    main()
    
```

I will follow some of the [Python Style Guide](https://peps.python.org/pep-0008/) except for extra spaces between classes, functions, and code blocks.
