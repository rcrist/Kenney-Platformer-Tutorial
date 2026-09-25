import random

import arcade

from .nature import ASSET_ROOT, AnimatedNatureSprite


MAX_LEAVES = 20
LEAF_LEVELS = {"level_01", "level_03"}


class Leaf(AnimatedNatureSprite):
    texture_root = ASSET_ROOT
    texture_folder = "leaf"
    frame_count = 18
    first_frame = 0
    filename_digits = 2
    randomize_animation = True

    def __init__(self, x: float, y: float):
        self.seconds_per_frame = random.uniform(0.06, 0.16)
        super().__init__(x, y)
        self.scale = 2
        self.fall_speed = random.uniform(20, 45)
        self.drift_speed = random.uniform(-12, 12)

    def on_update(self, delta_time: float):
        self.center_x += self.drift_speed * delta_time
        self.center_y -= self.fall_speed * delta_time


class LeafManager:
    """Create, update, and remove the falling leaves for a level."""

    def __init__(self, level):
        self.enabled = level.name in LEAF_LEVELS
        self.leaf_list = arcade.SpriteList()
        self.next_leaf_time = random.uniform(0.1, 0.5)

        level.scene.add_sprite_list("Leaves", sprite_list=self.leaf_list)

        # Tiled layers are initially drawn before sprite lists added in code.
        # Keep the foreground in front of the leaves and player.
        if "Foreground" in level.scene:
            level.scene.move_sprite_list_after("Foreground", "Leaves")

    def update(self, delta_time, camera):
        if not self.enabled:
            return

        camera_x, camera_y = camera.position
        bottom = camera_y - camera.camera_height / 2

        for leaf in tuple(self.leaf_list):
            leaf.on_update(delta_time)
            if leaf.top < bottom:
                leaf.remove_from_sprite_lists()

        self.next_leaf_time -= delta_time
        if self.next_leaf_time > 0:
            return

        self.next_leaf_time = random.uniform(0.1, 0.5)
        if len(self.leaf_list) >= MAX_LEAVES:
            return

        left = camera_x - camera.camera_width / 2
        top = camera_y + camera.camera_height / 2
        leaf = Leaf(
            random.uniform(left, left + camera.camera_width),
            top + 8,
        )
        self.leaf_list.append(leaf)
