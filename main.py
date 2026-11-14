import pygame
import heapq
from collections import deque
from time import perf_counter

# ------------------------------------------------------------
# Treasure Hunter: Keys & Doors
# Search algorithms: BFS and A*
# State = (row, col, collected_keys_bitmask)
# ------------------------------------------------------------

pygame.init()

TILE = 54
COLS, ROWS = 12, 9
PANEL_H = 150
WIDTH, HEIGHT = COLS * TILE, ROWS * TILE + PANEL_H
FPS = 60

# Map legend:
# # = wall, . = floor, S = start, G = treasure
# R/B = red/blue key, r/b = matching locked door
LEVEL = [
    "############",
    "#S..#......#",
    "#.#.#.##...#",
    "#.#...Rr...#",
    "#.###.###..#",
    "#...#...#..#",
    "###.#.B.b..#",
    "#..........#",
    "############",
]

# Colors
BG = (22, 26, 38)
FLOOR = (235, 238, 244)
WALL = (48, 56, 76)
GRID = (205, 211, 222)
WHITE = (255, 255, 255)
BLACK = (25, 29, 39)
GOLD = (245, 190, 55)
RED = (220, 65, 75)
BLUE = (65, 130, 230)
GREEN = (55, 170, 105)
PURPLE = (130, 95, 210)
EXPLORED = (196, 218, 250)
PATH_COLOR = (255, 226, 130)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Treasure Hunter - BFS & A*")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20, bold=True)
small = pygame.font.SysFont("arial", 15)
tiny = pygame.font.SysFont("arial", 12)

def find_tile(symbol):
    for r, row in enumerate(LEVEL):
        for c, value in enumerate(row):
            if value == symbol:
                return (r, c)
    return None

START = find_tile("S")
GOAL = find_tile("G")  # Goal is placed dynamically below if absent.
# Put treasure at the far end of the map.
GOAL = (7, 10)

# Replace the floor at the goal coordinate with G.
level = [list(row) for row in LEVEL]
level[GOAL[0]][GOAL[1]] = "G"
LEVEL = ["".join(row) for row in level]

KEY_BITS = {"R": 1, "B": 2}
DOOR_BITS = {"r": 1, "b": 2}

def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS

def neighbors(state):
    """Return legal next states in Up, Left, Right, Down order."""
    r, c, keys = state
    moves = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    result = []
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if not in_bounds(nr, nc):
            continue
        cell = LEVEL[nr][nc]
        if cell == "#":
            continue
        if cell in DOOR_BITS and not (keys & DOOR_BITS[cell]):
            continue
        new_keys = keys
        if cell in KEY_BITS:
            new_keys |= KEY_BITS[cell]
        result.append((nr, nc, new_keys))
    return result
def reconstruct_path(parent, end_state):
    path = []
    current = end_state
    while current is not None:
        path.append(current)
        current = parent[current]
    return list(reversed(path))

def bfs(start_pos, goal_pos, initial_keys=0):
    """Breadth-First Search: queue (FIFO), shortest path by number of moves."""
    start = (start_pos[0], start_pos[1], initial_keys)
    queue = deque([start])
    parent = {start: None}
    visited = {start}
    explored_order = []

    while queue:
        current = queue.popleft()
        explored_order.append(current)

        if (current[0], current[1]) == goal_pos:
            return reconstruct_path(parent, current), explored_order

        for nxt in neighbors(current):
            if nxt not in visited:
                visited.add(nxt)       # Mark visited when enqueued.
                parent[nxt] = current
                queue.append(nxt)

    return [], explored_order

def heuristic(state, goal_pos):
    """Manhattan distance: |row difference| + |column difference|."""
    return abs(state[0] - goal_pos[0]) + abs(state[1] - goal_pos[1])

def astar(start_pos, goal_pos, initial_keys=0):
    """A*: priority queue ordered by f(n) = g(n) + h(n)."""
    start = (start_pos[0], start_pos[1], initial_keys)
    frontier = []
    counter = 0
    heapq.heappush(frontier, (heuristic(start, goal_pos), 0, counter, start))

    came_from = {start: None}
    g_cost = {start: 0}
    closed = set()
    explored_order = []

    while frontier:
        f, current_g, _, current = heapq.heappop(frontier)

        if current in closed:
            continue
        closed.add(current)
        explored_order.append(current)

        if (current[0], current[1]) == goal_pos:
            return reconstruct_path(came_from, current), explored_order

        for nxt in neighbors(current):
            tentative_g = current_g + 1
            if tentative_g < g_cost.get(nxt, float("inf")):
                g_cost[nxt] = tentative_g
                came_from[nxt] = current
                counter += 1
                new_f = tentative_g + heuristic(nxt, goal_pos)
                heapq.heappush(frontier, (new_f, tentative_g, counter, nxt))

    return [], explored_order

def draw_text(text, x, y, color=WHITE, use_font=small):
    image = use_font.render(text, True, color)
    screen.blit(image, (x, y))

def draw_button(rect, label, active=True):
    color = (66, 111, 185) if active else (85, 88, 98)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (215, 225, 240), rect, 2, border_radius=8)
    txt = font.render(label, True, WHITE)
    screen.blit(txt, txt.get_rect(center=rect.center))

buttons = {
    "BFS": pygame.Rect(18, ROWS*TILE + 12, 115, 38),
    "A*": pygame.Rect(143, ROWS*TILE + 12, 115, 38),
    "RESET": pygame.Rect(268, ROWS*TILE + 12, 115, 38),
    "PLAY": pygame.Rect(393, ROWS*TILE + 12, 115, 38),
}

player = START
collected = 0
path = []
explored = []
path_index = 0
animation = False
animation_timer = 0
mode = "Manual"
message = "Collect keys, open matching doors, and reach the treasure!"
moves = 0
search_time = 0.0

def reset_game():
    global player, collected, path, explored, path_index, animation
    global mode, message, moves, search_time
    player = START
    collected = 0
    path = []
    explored = []
    path_index = 0
    animation = False
    mode = "Manual"
    message = "Collect keys, open matching doors, and reach the treasure!"
    moves = 0
    search_time = 0.0

def run_search(which):
    global path, explored, path_index, animation, mode, message, search_time
    start_time = perf_counter()
    if which == "BFS":
        path, explored = bfs(player, GOAL, collected)
    else:
        path, explored = astar(player, GOAL, collected)
    search_time = (perf_counter() - start_time) * 1000
    path_index = 0
    animation = bool(path)
    mode = which
    if path:
        message = f"{which} found a path! Press PLAY to animate it."
    else:
        message = f"{which}: no path found from the current state."

def try_move(dr, dc):
    global player, collected, moves, message
    nr, nc = player[0] + dr, player[1] + dc
    if not in_bounds(nr, nc):
        return
    cell = LEVEL[nr][nc]
    if cell == "#":
        message = "Blocked by a wall."
        return
    if cell in DOOR_BITS and not (collected & DOOR_BITS[cell]):
        message = "Locked door! Find its matching key first."
        return
    player = (nr, nc)
    moves += 1
    if cell in KEY_BITS:
        collected |= KEY_BITS[cell]
        message = f"Key collected! Current keys: {key_text(collected)}"
    elif (nr, nc) == GOAL:
        message = "You found the treasure! Congratulations!"
    else:
        message = "Keep exploring!"

def key_text(mask):
    names = []
    if mask & 1:
        names.append("RED")
    if mask & 2:
        names.append("BLUE")
    return ", ".join(names) if names else "none"

def draw_game():
    screen.fill(BG)

    # Map tiles
    for r in range(ROWS):
        for c in range(COLS):
            cell = LEVEL[r][c]
            rect = pygame.Rect(c*TILE, r*TILE, TILE, TILE)
            color = FLOOR
            if cell == "#":
                color = WALL
            elif cell == "R":
                color = (255, 225, 225)
            elif cell == "B":
                color = (225, 235, 255)
            elif cell == "r":
                color = (170, 65, 75)
            elif cell == "b":
                color = (60, 100, 180)
            elif cell == "G":
                color = (255, 242, 190)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID, rect, 1)

            center = rect.center
            if cell == "S":
                draw_text("S", rect.x + 20, rect.y + 15, GREEN, font)
            elif cell == "G":
                draw_text("★", rect.x + 16, rect.y + 13, GOLD, font)
            elif cell == "R":
                pygame.draw.circle(screen, RED, center, 13)
                draw_text("R", rect.x + 20, rect.y + 15, WHITE, tiny)
            elif cell == "B":
                pygame.draw.circle(screen, BLUE, center, 13)
                draw_text("B", rect.x + 20, rect.y + 15, WHITE, tiny)
            elif cell == "r":
                pygame.draw.rect(screen, RED, (rect.x+15, rect.y+8, 24, 38), border_radius=4)
                draw_text("R", rect.x+22, rect.y+18, WHITE, small)
            elif cell == "b":
                pygame.draw.rect(screen, BLUE, (rect.x+15, rect.y+8, 24, 38), border_radius=4)
                draw_text("B", rect.x+22, rect.y+18, WHITE, small)

    # Explored states (unique positions for display)
    for state in explored:
        r, c, _ = state
        center = (c*TILE + TILE//2, r*TILE + TILE//2)
        pygame.draw.circle(screen, EXPLORED, center, 5)

    # Path overlay
    for state in path:
        r, c, _ = state
        rect = pygame.Rect(c*TILE+13, r*TILE+13, TILE-26, TILE-26)
        pygame.draw.rect(screen, PATH_COLOR, rect, border_radius=5)

    # Player
    px, py = player[1]*TILE + TILE//2, player[0]*TILE + TILE//2
    pygame.draw.circle(screen, PURPLE, (px, py), 17)
    pygame.draw.circle(screen, WHITE, (px, py), 17, 2)

    # Bottom information panel
    panel_y = ROWS*TILE
    pygame.draw.rect(screen, (30, 36, 52), (0, panel_y, WIDTH, PANEL_H))
    for name, rect in buttons.items():
        draw_button(rect, name)

    draw_text(f"Mode: {mode}", 18, panel_y+60, WHITE, small)
    draw_text(f"Keys: {key_text(collected)}", 155, panel_y+60, WHITE, small)
    draw_text(f"Moves: {moves}", 360, panel_y+60, WHITE, small)
    draw_text(f"Explored states: {len(explored)}", 18, panel_y+82, (190, 210, 240), small)
    draw_text(f"Path length: {max(0, len(path)-1)}", 210, panel_y+82, (190, 210, 240), small)
    draw_text(f"Search time: {search_time:.3f} ms", 360, panel_y+82, (190, 210, 240), small)
    draw_text(message[:75], 18, panel_y+112, GOLD, tiny)

    pygame.display.flip()

running = True
while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                try_move(-1, 0)
            elif event.key == pygame.K_DOWN:
                try_move(1, 0)
            elif event.key == pygame.K_LEFT:
                try_move(0, -1)
            elif event.key == pygame.K_RIGHT:
                try_move(0, 1)
            elif event.key == pygame.K_r:
                reset_game()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if buttons["BFS"].collidepoint(pos):
                run_search("BFS")
            elif buttons["A*"].collidepoint(pos):
                run_search("A*")
            elif buttons["RESET"].collidepoint(pos):
                reset_game()
            elif buttons["PLAY"].collidepoint(pos):
                if path:
                    animation = True
                    message = "Animating the selected search path..."

    if animation and path:
        animation_timer += dt
        if animation_timer >= 250:
            animation_timer = 0
            if path_index < len(path)-1:
                path_index += 1
                state = path[path_index]
                player = (state[0], state[1])
                collected = state[2]
                moves += 1
            else:
                animation = False
                if player == GOAL:
                    message = f"{mode} completed: treasure reached!"

    draw_game()

pygame.quit()
