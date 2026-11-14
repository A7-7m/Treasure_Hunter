# Treasure Hunter: Keys & Doors (BFS + A*)

## Requirements
- Python 3.9+
- pygame

## Run
Open a terminal in this folder and run:

```bash
python -m pip install -r requirements.txt
python main.py
```

## Controls
- Arrow keys: move manually
- BFS: run Breadth-First Search from the current player position
- A*: run A* from the current player position
- PLAY: animate the selected algorithm's path
- RESET or R: reset the game
- ESC: quit

## Map legend
- S: Start
- G / ★: Treasure (Goal)
- #: Wall
- R: Red key
- r: Red locked door
- B: Blue key
- b: Blue locked door
- .: Empty floor

## AI / Search design
The search state is:

`(row, column, key_mask)`

The key mask is a compact representation:
- bit 0 (value 1): red key collected
- bit 1 (value 2): blue key collected

A state is not just a position. The same cell with different collected keys is a different search state.

### BFS
- Uses a FIFO queue (`collections.deque`).
- Explores by increasing depth.
- Marks a state visited when it is enqueued.
- Finds a path with the fewest moves because every move has equal cost.

### A*
- Uses a priority queue (`heapq`).
- `g(n)`: actual cost from the start state.
- `h(n)`: Manhattan distance to the goal.
- `f(n) = g(n) + h(n)`.
- Manhattan distance is admissible here because it ignores walls and doors, so it never overestimates the remaining number of moves.

Both algorithms use the same legal-move function, so both obey walls and locked doors and automatically collect keys when entering key cells.

## Metrics shown
- Explored states: number of states expanded by the selected algorithm.
- Path length: number of moves in the returned path.
- Search time: measured search duration in milliseconds.

## Important note for the viva
BFS and A* are both implemented and selectable in the game. They are not just described in the report. You can run each one and compare its explored-state count, path length, and runtime.
