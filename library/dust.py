import random

import arcade
from arcade import particles

from .player import Dir, State


DUST_COLORS = (
    (201, 184, 151, 255),
    (184, 166, 132, 255),
    (218, 207, 181, 255),
)


class DustManager:
    """Create and manage procedural Arcade particle emitters for the player."""

    RUN_INTERVAL = 0.2
    PARTICLE_COUNTS = {"run": 5, "jump": 9, "fall": 12}

    def __init__(self, player):
        self.player = player
        self.emitters = []
        self.run_timer = 0.0
        self.was_falling = False
        self.was_grounded = False
        self.textures = tuple(
            arcade.make_soft_circle_texture(diameter, color)
            for diameter, color in zip((16, 20, 24), DUST_COLORS)
        )

    def spawn_jump(self):
        self._spawn("jump")

    def update(self, delta_time, grounded):
        if grounded and not self.was_grounded and self.was_falling:
            self._spawn("fall")

        if grounded and self.player.current_state == State.WALK:
            self.run_timer -= delta_time
            if self.run_timer <= 0:
                self._spawn(
                    "run",
                    facing_left=self.player.current_direction == Dir.LEFT,
                )
                self.run_timer = self.RUN_INTERVAL
        else:
            self.run_timer = 0.0

        self.was_falling = self.player.current_state == State.FALL
        self.was_grounded = grounded

        for emitter in tuple(self.emitters):
            emitter.update(delta_time)
            if emitter.can_reap():
                self.emitters.remove(emitter)

    def draw(self):
        for emitter in self.emitters:
            emitter.draw()

    def _spawn(self, animation, facing_left=False):
        trail_offset = 0
        horizontal_direction = 0
        if animation == "run":
            trail_offset = 12 if facing_left else -12
            horizontal_direction = 1 if facing_left else -1

        def create_particle(emitter):
            if animation == "run":
                change_x = horizontal_direction * random.uniform(0.15, 0.55)
                change_y = random.uniform(0.08, 0.3)
            else:
                change_x = random.uniform(-0.55, 0.55)
                change_y = random.uniform(0.12, 0.5)

            return particles.FadeParticle(
                filename_or_texture=random.choice(self.textures),
                change_xy=(change_x, change_y),
                lifetime=random.uniform(0.35, 0.6),
                center_xy=(random.uniform(-8, 8), random.uniform(0, 4)),
                scale=random.uniform(0.35, 0.75),
                start_alpha=random.randint(110, 185),
                end_alpha=0,
            )

        self.emitters.append(
            particles.Emitter(
                center_xy=(
                    self.player.center_x + trail_offset,
                    self.player.bottom + 2,
                ),
                emit_controller=particles.EmitBurst(
                    self.PARTICLE_COUNTS[animation]
                ),
                particle_factory=create_particle,
            )
        )
