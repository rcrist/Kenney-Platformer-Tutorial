Music Tracks:
- Farm Frolics for the fields
- Infinite Descent for the dark cave
- Flowing Rocks for the windy forest
- Mission Plausible for Robowser's fortress

All 4 music tracks sound great.

```python title=audio_manager.py
import arcade


class MusicManager:
    """Load, loop, and switch level background music."""

    def __init__(self, volume=0.25):
        self.volume = volume
        self.current_path = None
        self.current_sound = None
        self.current_player = None
        self.sounds = {}

    def play(self, music_path):
        if music_path == self.current_path and self.current_player is not None:
            return

        self.stop()
        sound = self.sounds.get(music_path)
        if sound is None:
            sound = arcade.load_sound(music_path)
            self.sounds[music_path] = sound

        self.current_path = music_path
        self.current_sound = sound
        self.current_player = sound.play(volume=self.volume, loop=True)

    def stop(self):
        if self.current_sound is not None and self.current_player is not None:
            self.current_sound.stop(self.current_player)

        self.current_path = None
        self.current_sound = None
        self.current_player = None

```