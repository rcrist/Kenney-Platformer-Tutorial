Now that the 4 levels are built we can finalize the project:
- Refactor and optimize the code
- Fix code bugs
- Add particle effects
- Add sound effects

Refactor order:
1.  [x] Enemy catalog and factory - Enemy Manager
2.  [x] Level/layer setup helpers - Level Manager
3.  [x] Leaf system - Leaf Class
4.  [x] Physics construction 
5.  [x] Collision functions or system

`game.py` is now 94 lines long.

| Development Step             | Description                                                         |
| ---------------------------- | ------------------------------------------------------------------- |
| [[1-AI Code Review]]         | AI code review and refactor recommendations                         |
| [[2-Enemy Manager]]          | Manages all the enemy level detection and spawing                   |
| [[3-Game Manager]]           | Manager level transitions and level specific behaviors              |
| [[4-Leaf]]                   | Dedicate leaf class                                                 |
| [[5-Physics]]                | Physics creation function library                                   |
| [[6-Nature Update]]          | Updated to add nature spawing                                       |
| [[7-Player Update]]          | Updated to set the player limits to the level boundaries            |
| [[8-Level Update For Setup]] | Moved all level setup code to level.py                              |
| [[9-Collision Checks]]       | Moved all `check_for` type methods to enemy_manager.py and level.py |