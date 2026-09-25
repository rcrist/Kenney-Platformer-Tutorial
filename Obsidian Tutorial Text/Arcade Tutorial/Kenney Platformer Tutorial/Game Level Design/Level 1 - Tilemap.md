![[Pasted image 20260922150454.png|1400]]

After further consideration, I decided to use the Kenney New Platformer Pack which has tiles for ground, water, bridges, and blocks.
- Tile size: 64x64 px or 128x128 px
- 128x128 px seems to be Kenney's most popular size so I will go with that

Now, lets create our Tiled tilemap.
- Open the Tiled tile editor application
- Create a new project called `Tiled_Projects/Kenney_Platformer_Tutorial`
- Create a new map called `assets/maps/level_01.json` in the Python Arcade project folder.
	- Tile size: 128x128 px
	- Map size: 40x20 tiles

> [!HINT]
> When saving the tile map, change the file type to .json or the map will be unreadable by Arcade.

- Create a new tileset called `Tiled_Projects/Kenney_Platformer_Tutorial/Grass.tsx`. Load the Grass images from `assets\kenney_assets\New Platformer Pack\Sprites\Tiles\Double'.

![[Pasted image 20260924083445.png]]

Add the layers:
![[Pasted image 20260924080929.png]]

On the platform layer, create a grass platform across the bottom the level using the Stamp Brush to create a simple level for testing.

![[Pasted image 20260924083626.png|1000]]


We need to make our code more resilient by adding a check to see if there are any enemies on the Enemy object layer, if not, keep loading the level. Modify the `load_enemies()` method in the `GameView` class.

```python title=game.py hl=6,8
...

    def load_enemies(self):
        enemy_list = arcade.SpriteList()

        enemy_objects = self.level.tile_map.object_lists.get("Enemies", ())

        for enemy_object in enemy_objects:
            properties = enemy_object.properties
            enemy_type = properties["type"]

            if enemy_type not in ENEMY_TEXTURES:
                raise ValueError(f"Unknown enemy type in tilemap: {enemy_type}")

            enemy = Enemy(ENEMY_TEXTURES[enemy_type], 2)
            enemy.scale = 0.2
            enemy.position = enemy_object.shape
            enemy.change_x = properties.get("change_x", ENEMY_SPEED)
            enemy.set_patrol_range(
                properties["boundary_left"],
                properties["boundary_right"],
            )
            enemy_list.append(enemy)

        return enemy_list
        
```

<video src=20260924-1439-48.2280926.mp4 controls width="1000"></video>

With that small change, our test level runs and is starting to look like a real game! I love the animated grass, leaves, bushes, and trees. 

New tileset: `Items.tsx`

![[Pasted image 20260924084941.png|1000]]

New tileset: `Water.tsx`

![[Pasted image 20260924093028.png|1000]]

Platforms layer:
![[Pasted image 20260924093702.png]]

Platforms and Moving Platforms layer:
![[Pasted image 20260924093912.png]]

Add a new Exit object layer:
![[Pasted image 20260924094003.png]]

To get solid, moving platforms make the following changes:

```python title=game.py hl=7,14,20-31
...

        # Create the level from a Tiled tilemap
        self.level = Level()
        self.level.scene.add_sprite("Player", self.player)
        self.camera.set_limits_to_tilemap(self.level.tile_map)
        self.setup_moving_platforms()

...

        # Add physics to the game
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms=self.level.scene["Moving Platforms"],
            walls=self.level.scene["Platforms"],
            gravity_constant=GRAVITY,
            ladders=self.level.scene["Ladders"],
        )

    def setup_moving_platforms(self):
        """Configure vertical movement from the platform custom properties."""
        tile_distance = self.level.tile_map.tile_height * self.level.tile_map.scaling

        for platform in self.level.scene["Moving Platforms"]:
            properties = platform.properties
            if "Top" not in properties or "Bottom" not in properties:
                continue

            platform.boundary_top = platform.top + properties["Top"] * tile_distance
            platform.boundary_bottom = platform.bottom - properties["Bottom"] * tile_distance
            platform.change_y = MOVING_PLATFORM_SPEED

    def load_enemies(self):
     
...
```

```python title=settings.py hl=13
# Window constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Camera viewport constants
CAMERA_WIDTH = 640*1.5
CAMERA_HEIGHT = 360*1.5

# Player constants
PLAYER_SPEED = 5
PLAYER_JUMP_SPEED = 12
GRAVITY = 0.5
MOVING_PLATFORM_SPEED = 1

# Enemy constants
ENEMY_SPEED = 1

# Player animation speed
UPDATES_PER_FRAME = 5

```

<video src=20260924-1527-02.3752275.mp4 controls width="1000"></video>

Woohoo! We have moving platforms.

Add the Foreground layer and modify the code to display the items in the foreground in front of the player.

![[Pasted image 20260924095255.png]]

```python title=game.py hl=8-10
...

        self.leaf_list = arcade.SpriteList()
        self.level.scene.add_sprite_list("Leaves", sprite_list=self.leaf_list)
        self.next_leaf_time = random.uniform(0.1, 0.5)


        # Tiled layers are initially drawn before sprite lists added in code.
        # Move Foreground to the end so it appears in front of the player.
        self.level.scene.move_sprite_list_after("Foreground", "Leaves")

    def setup_moving_platforms(self):
    
...
```

Foreground + Background layers
![[Pasted image 20260924095634.png]]

Foreground, Background and Coins Layers
![[Pasted image 20260924095739.png]]

Play the game and confirm:
- Player can collect coins
- Bushes on the Foreground layer are drawn in front of the player
- Items on the Background layer are drawn behind the player

I want to place the actual images of animated bushes, grass, trees on a layer so I can see what they look like in the scene. We'll need to remove the manually placed objects and spawn them from a new object layer called Nature.

1. Create a new tileset called Nature
2. Create a new object layer called Nature
3. Set the position of each animated item in the scene
4. Modify the code to spawn the animated items from the Nature layer

Nature Tileset:
![[Pasted image 20260924100411.png|1000]]

Note that I used the first image in the animation set for each item.

Hmmm, these images are 512x512 px which is very big compared to the other tilesets. I think we should create smaller images for Tiled with size of 128x128 which is the same size as our tileset. I will tell AI to change the size. The new images are stored in `assets/NatureAssets/nature`.

![[Pasted image 20260924102447.png|1000]]

```python title=game.py
...

    def load_nature(self):
        """Replace tilemap markers with the matching animated sprites."""
        nature_classes = {
            "Grass": Grass,
            "Tree": Tree,
            "Bush": Bush,
            "Reed": Reeds,
        }
        nature_list = arcade.SpriteList()
        nature_markers = self.level.scene.get_sprite_list("Nature")

        for marker in nature_markers:
            nature_type = marker.properties.get("Type")
            nature_class = nature_classes.get(nature_type)
            if nature_class is None:
                raise ValueError(f"Unknown nature type in tilemap: {nature_type}")

            nature = nature_class(marker.center_x, marker.center_y - 10)
            nature.scale = 0.1
            nature_list.append(nature)

        self.level.scene.remove_sprite_list_by_name("Nature")
        self.level.scene.add_sprite_list("Nature", sprite_list=nature_list)
        return nature_list
        
...
```

Lets use the same technique to add Kenny `Goomba` Robots to the scene.

`Robots.tsx`
![[Pasted image 20260924103014.png|1000]]

Robot "type" is define in the ENEMY TEXTURES dictionary.

```python
ENEMY_TEXTURES = {
    "robot1": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_blueDrive{i}.png",
    "robot2": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_greenDrive{i}.png",
    "robot3": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_redDrive{i}.png",
    "robot4": "assets/kenney_assets/Robot Pack/PNG/Side view/robot_yellowDrive{i}.png",
}
```

Custom properties:
![[Pasted image 20260924104507.png]]

Where the boundaries are defined in tiles of 128x128 px.

Enemies Layer:
![[Pasted image 20260924104623.png]]

This is how we load our enemies and set their patrol range.
```python title=game.py
...

    def load_enemies(self):
        """Replace tilemap enemy markers with runtime enemy sprites."""
        enemy_list = arcade.SpriteList()
        enemy_markers = self.level.scene.get_sprite_list("Enemies")
        tile_distance = self.level.tile_map.tile_width * self.level.tile_map.scaling

        for marker in enemy_markers:
            properties = marker.properties
            enemy_type = properties["type"]

            if enemy_type not in ENEMY_TEXTURES:
                raise ValueError(f"Unknown enemy type in tilemap: {enemy_type}")

            enemy = Enemy(ENEMY_TEXTURES[enemy_type], 2)
            enemy.scale = 0.3
            enemy.position = marker.position
            enemy.change_x = properties.get("change_x", ENEMY_SPEED)

            if "boundary_left" in properties and "boundary_right" in properties:
                enemy.set_patrol_range(
                    marker.center_x - properties["boundary_left"] * tile_distance,
                    marker.center_x + properties["boundary_right"] * tile_distance,
                )

            enemy_list.append(enemy)

        self.level.scene.remove_sprite_list_by_name("Enemies")
        self.level.scene.add_sprite_list("Enemies", sprite_list=enemy_list)
        return enemy_list
        
...
```

![[Pasted image 20260924104804.png|1000]]

Well, it isn't perfect but we now have a playable level where the player can explore the world, collect coins, interact with robots, and find the exit. Wait! We need to do something when the player reaches the exit.

Exit object custom properties:
![[Pasted image 20260924105533.png]]

```python title=game.py hl=7-8,27-39
...

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.keep_player_in_level()

        if self.check_for_exit():
            return

        self.collect_coins()

        for physics_engine in self.enemy_physics_engines:
            physics_engine.update()
        self.check_for_enemy_collision()

        for enemy in self.enemy_list:
            enemy.on_update(delta_time)

        self.level.scene.update_animation(delta_time)
        self.player.update_state(delta_time)
        self.player.on_update(delta_time)  # Sets the player direction and animation
        self.camera.follow(self.player)
        self.update_leaves(delta_time)
        
...

    def check_for_exit(self):
        """Restart the game when the player reaches an Exit marker."""
        exits_hit = arcade.check_for_collision_with_list(
            self.player,
            self.level.scene["Exit"],
        )

        if any(exit_marker.properties.get("type") == "Exit" for exit_marker in exits_hit):
            print("You reached the exit!")
            self.window.show_view(GameView())
            return True

        return False

    def check_for_enemy_collision(self):
    
...
```

Run the game and confirm:
- When the player reaches the exit
	- The game resets
	- "You reached the exit!" is printed on the terminal console

Now we are ready to transition to Level 2, if we had one!

