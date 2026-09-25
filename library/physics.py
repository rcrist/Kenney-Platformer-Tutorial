import arcade

from .settings import GRAVITY, PLAYER_JUMP_SPEED


class PhysicsManager:
    """Own and operate the player and enemy physics engines."""

    def __init__(
        self,
        player,
        enemies,
        moving_platforms,
        player_walls,
        enemy_walls,
        ladders,
    ):
        self.moving_platforms = moving_platforms
        self.player_on_moving_platform = False
        self.player_is_grounded = False
        self.player_engine = arcade.PhysicsEnginePlatformer(
            player,
            platforms=moving_platforms,
            walls=player_walls,
            gravity_constant=GRAVITY,
            ladders=ladders,
        )
        self.enemy_engines = [
            arcade.PhysicsEnginePlatformer(
                enemy,
                walls=enemy_walls,
                gravity_constant=0 if enemy.is_flying else GRAVITY,
                ladders=ladders,
            )
            for enemy in enemies
        ]

    def update_player(self):
        collisions = self.player_engine.update()
        moving_platform_ids = {id(platform) for platform in self.moving_platforms}
        supporting_collisions = [
            collision
            for collision in collisions
            if self.player_engine.player_sprite.center_y >= collision.center_y
        ]
        self.player_is_grounded = self.player_engine.can_jump()
        self.player_on_moving_platform = any(
            id(collision) in moving_platform_ids
            for collision in supporting_collisions
        )

    def update_enemies(self):
        for engine in self.enemy_engines:
            engine.update()

    def jump(self):
        """Jump when the player physics engine reports that it is allowed."""
        if self.player_engine.can_jump():
            self.player_engine.jump(PLAYER_JUMP_SPEED)
            self.player_is_grounded = False
            self.player_on_moving_platform = False
            return True
        return False

    def remove_enemy(self, enemy):
        """Remove the physics engine associated with a defeated enemy."""
        self.enemy_engines = [
            engine
            for engine in self.enemy_engines
            if engine.player_sprite is not enemy
        ]
