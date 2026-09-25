import arcade
import random
from pathlib import Path


KENNEY_AUDIO_ROOT = (
    Path(__file__).resolve().parent.parent
    / "assets/kenney_assets/audio"
)
AUDIO_ROOT = KENNEY_AUDIO_ROOT / "Impact Sounds"


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


class PlayerSoundManager:
    """Play player sound effects and control the walking cadence."""

    FOOTSTEP_INTERVAL = 0.28
    BOSS_ALARM_INTERVAL = 0.32
    BOSS_ALARM_PULSES = 8
    BOSS_ALARM_VOICES = 3

    def __init__(self, volume=0.35):
        self.volume = volume
        self.footstep_timer = 0.0
        self.boss_alarm_timer = 0.0
        self.boss_alarm_pulses_remaining = 0
        self.boss_alarm_tone_index = 0
        self.footsteps = self._load_sounds(
            "Audio", "footstep_grass", range(5), separator="_", number_width=3
        )
        self.jumps = self._load_sounds(
            "Retro Sounds 2/Audio", "jump", range(1, 4)
        )
        self.hurts = self._load_sounds(
            "Retro Sounds 2/Audio", "hurt", range(1, 4)
        )
        self.enemy_hits = self._load_sounds(
            "Retro Sounds 2/Audio", "hit", range(1, 4)
        )
        self.enemy_deaths = self._load_sounds(
            "Retro Sounds 2/Audio", "explosion", range(1, 4)
        )
        self.coin_pickups = self._load_sounds(
            "Retro Sounds 2/Audio", "coin", range(1, 4)
        )
        self.health_pickups = [
            arcade.load_sound(
                KENNEY_AUDIO_ROOT / "Digital Audio/Audio" / f"powerUp{number}.ogg"
            )
            for number in range(1, 4)
        ]
        self.boss_alarm_tones = [
            arcade.load_sound(
                KENNEY_AUDIO_ROOT / "Digital Audio/Audio/twoTone1.ogg"
            ),
            arcade.load_sound(
                KENNEY_AUDIO_ROOT / "Digital Audio/Audio/twoTone2.ogg"
            ),
        ]

    @staticmethod
    def _load_sounds(folder, stem, numbers, separator="", number_width=0):
        sounds = []
        for number in numbers:
            suffix = f"{number:0{number_width}d}" if number_width else str(number)
            sounds.append(
                arcade.load_sound(AUDIO_ROOT / folder / f"{stem}{separator}{suffix}.ogg")
            )
        return sounds

    def update(self, delta_time, walking, grounded):
        """Play footsteps at a steady cadence while walking on the ground."""
        self._update_boss_alarm(delta_time)

        if not (walking and grounded):
            self.footstep_timer = 0.0
            return

        self.footstep_timer -= delta_time
        if self.footstep_timer <= 0:
            random.choice(self.footsteps).play(volume=self.volume * 0.65)
            self.footstep_timer = self.FOOTSTEP_INTERVAL

    def play_jump(self):
        random.choice(self.jumps).play(volume=self.volume)

    def play_hurt(self):
        random.choice(self.hurts).play(volume=self.volume)

    def play_enemy_hurt(self):
        random.choice(self.enemy_hits).play(volume=self.volume)

    def play_enemy_death(self):
        random.choice(self.enemy_deaths).play(volume=self.volume)

    def play_coin_pickup(self):
        random.choice(self.coin_pickups).play(volume=self.volume)

    def play_health_pickup(self):
        random.choice(self.health_pickups).play(volume=self.volume)

    def play_boss_encounter(self):
        """Start a loud, alternating sci-fi warning pattern."""
        self.boss_alarm_pulses_remaining = self.BOSS_ALARM_PULSES
        self.boss_alarm_tone_index = 0
        self.boss_alarm_timer = 0.0
        self._update_boss_alarm(0.0)

    def _update_boss_alarm(self, delta_time):
        if self.boss_alarm_pulses_remaining <= 0:
            return

        self.boss_alarm_timer -= delta_time
        if self.boss_alarm_timer > 0:
            return

        tone = self.boss_alarm_tones[self.boss_alarm_tone_index]
        for _ in range(self.BOSS_ALARM_VOICES):
            tone.play(volume=1.0)
        self.boss_alarm_tone_index = 1 - self.boss_alarm_tone_index
        self.boss_alarm_pulses_remaining -= 1
        self.boss_alarm_timer = self.BOSS_ALARM_INTERVAL
