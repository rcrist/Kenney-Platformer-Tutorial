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


def load_nature(level):
    """Replace a level's tilemap markers with animated nature sprites."""
    nature_classes = {
        "Grass": Grass,
        "Tree": Tree,
        "Bush": Bush,
        "Reed": Reeds,
    }
    nature_list = arcade.SpriteList()

    try:
        nature_markers = level.scene.get_sprite_list("Nature")
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

    if "Nature" in level.scene:
        level.scene.remove_sprite_list_by_name("Nature")
    level.scene.add_sprite_list("Nature", sprite_list=nature_list)
    return nature_list
