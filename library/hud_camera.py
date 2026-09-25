import arcade

from .settings import WINDOW_HEIGHT, WINDOW_WIDTH


class HudCamera(arcade.Camera2D):
    """Screen-space camera responsible for drawing the game's HUD."""

    def __init__(self):
        super().__init__(
            viewport=arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            projection=arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            position=(0, 0),
        )

        self.score_text = arcade.Text(
            "Coins: 0",
            20,
            WINDOW_HEIGHT - 20,
            arcade.color.WHITE,
            font_size=20,
            bold=True,
            anchor_y="top",
        )

    def set_score(self, score: int):
        self.score_text.text = f"Coins: {score}"

    def draw(self):
        self.use()
        self.score_text.draw()
