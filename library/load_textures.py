import arcade


def load_textures(file_path, num_textures):
    textures = []

    for i in range(num_textures):
        texture = arcade.load_texture(file_path.format(i=i))
        textures.append((texture, texture.flip_left_right()))  # Index 0 = right, index 1 = left

    return textures
