import arcade

from .settings import UPDATES_PER_FRAME

class AnimationPlayer:
    def __init__(self):
        self.cur_texture = 0

    def update_animation(self, texture_list, num_textures, direction) -> arcade.Texture:
        # Assume this function is called in the on_update() method and updates every frame
        self.cur_texture += 1
        frame = (self.cur_texture // UPDATES_PER_FRAME) % num_textures
        texture = texture_list[frame][direction]

        return texture
