Whew! We now have a playable game world with a player that can explore and interact with it.

Here is a summary of what we accomplished:

| Development Step        | Description                                                                                                                                                                                   |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[1-Game Window]]       | Create an Arcade game window, defined the window size, title, and centered the window on the computer screen. Set the background color and started the game loop.                             |
| [[2-Sprite]]            | Added a player sprite from the Arcade predefined resources. Set the player position to the center of the window. Set the draw loop to draw the player pixel art each loop.                    |
| [[3-Collision Example]] | Create a cloud sprite and a blue rectangle sprite. Moved the cloud sprite position with the up and down keys. Change the blue rectangle to light blue when it collides with the cloud sprite. |
| [[3-Game Camera]]       | Create a viewport camera that displays a portion of the screen at the full window resolution.                                                                                                 |
| [[4-Library]]           | Exported settings, player, and camera code to a library package with 3 new modules. Set the path so the root node can be found. Showed how to use game.py (main.py) in the root directory.    |
| [[5-Player Control]]    | Gave the player horizontal position control so the user can move the player left and right on the screen using the keyboard.                                                                  |
| [[6-Player Direction]]  | Created flipped textures for the idle texture and changed the direction that the player is facing when moving left or right.                                                                  |
| [[7-Player Animation]]  | Add player walk animation.                                                                                                                                                                    |
| [[8-Level Map]]         | Created a new level module that loads the Tiled tilemap into a "scene". Added the player to the scene and confirmed that the level is displayed on the screen.                                |
| [[9-Game Physics]]      | Set the gravity constant and defined the platform physics layers that collide with the player.                                                                                                |
| [[10-Player Camera]]    | Modified the camera to follow the player limited by the boundaries of the level map.                                                                                                          |

This is only the basic game elements for a 2D platformer game in Python Arcade. There is much more to come.
