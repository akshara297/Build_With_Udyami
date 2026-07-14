import random
import os
import time
import sys

# --- SIMULATION CONFIGURATION ---
WIDTH = 50
HEIGHT = 20
TICK_RATE = 0.2  # Seconds between cycles

# Cell State Visuals
CHAR_EMPTY = '.'
CHAR_GRASS = '#'
CHAR_HERBIVORE = 'o'
CHAR_PREDATOR = 'X'

# --- ECOSYSTEM ENGINE ---

class EcosystemSandbox:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        # Initialize grid with random distributions
        self.grid = [[CHAR_EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.generation = 0
        self.running = True
        self.seed_world()

    def seed_world(self):
        for y in range(self.height):
            for x in range(self.width):
                roll = random.random()
                if roll < 0.25:
                    self.grid[y][x] = CHAR_GRASS
                elif roll < 0.32:
                    self.grid[y][x] = CHAR_HERBIVORE
                elif roll < 0.35:
                    self.grid[y][x] = CHAR_PREDATOR
                else:
                    self.grid[y][x] = CHAR_EMPTY

    def count_neighbors(self, cx, cy):
        """Counts all adjacent neighbors using a toroidal grid (wrapping borders)"""
        counts = {CHAR_EMPTY: 0, CHAR_GRASS: 0, CHAR_HERBIVORE: 0, CHAR_PREDATOR: 0}
        
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                # Toroidal wrap-around behavior
                ny = (cy + dy) % self.height
                nx = (cx + dx) % self.width
                
                neighbor_state = self.grid[ny][nx]
                counts[neighbor_state] += 1
                
        return counts

    def evaluate_next_cycle(self):
        # Create a blank double buffer grid to store the next state simultaneously
        next_grid = [[CHAR_EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                current = self.grid[y][x]
                neighbors = self.count_neighbors(x, y)
                
                # --- RULE RULES LAYER ---
                if current == CHAR_EMPTY:
                    # Grass spreads to empty soil
                    if neighbors[CHAR_GRASS] >= 3:
                        next_grid[y][x] = CHAR_GRASS
                    else:
                        next_grid[y][x] = CHAR_EMPTY
                        
                elif current == CHAR_GRASS:
                    # Herbivores consume grass
                    if neighbors[CHAR_HERBIVORE] >= 1:
                        next_grid[y][x] = CHAR_HERBIVORE
                    # Grass grows thicker or stays stable
                    elif neighbors[CHAR_GRASS] >= 6:
                        next_grid[y][x] = CHAR_EMPTY  # Dies from overcrowding
                    else:
                        next_grid[y][x] = CHAR_GRASS
                        
                elif current == CHAR_HERBIVORE:
                    # Predators eat herbivores
                    if neighbors[CHAR_PREDATOR] >= 1:
                        next_grid[y][x] = CHAR_PREDATOR
                    # Starvation due to lack of local food sources
                    elif neighbors[CHAR_GRASS] == 0 and random.random() < 0.3:
                        next_grid[y][x] = CHAR_EMPTY
                    # Starvation due to overpopulation stress
                    elif neighbors[CHAR_HERBIVORE] >= 5:
                        next_grid[y][x] = CHAR_EMPTY
                    else:
                        next_grid[y][x] = CHAR_HERBIVORE
                        
                elif current == CHAR_PREDATOR:
                    # Predators starve without prey resources
                    if neighbors[CHAR_HERBIVORE] == 0 and random.random() < 0.4:
                        next_grid[y][x] = CHAR_EMPTY
                    # Predators fight each other for territory if overcrowded
                    elif neighbors[CHAR_PREDATOR] >= 4:
                        next_grid[y][x] = CHAR_EMPTY
                    else:
                        next_grid[y][x] = CHAR_PREDATOR

        self.grid = next_grid
        self.generation += 1

    def calculate_metrics(self):
        grass, herb, pred, empty = 0, 0, 0, 0
        for y in range(self.height):
            for x in range(self.width):
                state = self.grid[y][x]
                if state == CHAR_GRASS: grass += 1
                elif state == CHAR_HERBIVORE: herb += 1
                elif state == CHAR_PREDATOR: pred += 1
                else: empty += 1
        return grass, herb, pred, empty

    def render(self):
        # Multiplatform clear terminal trick
        os.system('cls' if os.name == 'nt' else 'clear')
        
        grass, herb, pred, empty = self.calculate_metrics()
        
        print(f"=== ECOSYSTEM LABS CELLULAR AUTOMATA (GEN: {self.generation}) ===")
        print("-" * self.width)
        
        # Render current map buffer
        for y in range(self.height):
            row = "".join(self.grid[y])
            print(row)
            
        print("-" * self.width)
        print(f" ( # ) Grass Cover:  {grass:<6} | ( o ) Herbivores: {herb:<6}")
        print(f" ( X ) Predators:    {pred:<6} | ( . ) Open Soil:  {empty:<6}")
        print(" Press Ctrl+C to terminate the simulation run.")

    def run_loop(self):
        try:
            while self.running:
                self.render()
                self.evaluate_next_cycle()
                time.sleep(TICK_RATE)
        except KeyboardInterrupt:
            print("\nSimulation halted safely by operator.")

# --- INITIALIZATION LINK ---

if __name__ == "__main__":
    sandbox = EcosystemSandbox()
    sandbox.run_loop()

import os
import sys
import math
import time

# --- ENGINE CONFIGURATION ---
SCREEN_WIDTH = 60
SCREEN_HEIGHT = 20

FOV = math.pi / 4  # Field of View (45 degrees)
DEPTH = 16.0       # Maximum rendering distance

# 16x16 Dungeon Layout Grid
MAP_HEIGHT = 16
MAP_WIDTH = 16
MAP = (
    "################"
    "#..............#"
    "#..###....###..#"
    "#..#........#..#"
    "#..#........#..#"
    "#..............#"
    "#......##......#"
    "#......##......#"
    "#..............#"
    "###..######..###"
    "#........#.....#"
    "#........#.....#"
    "#...######.....#"
    "#..............#"
    "#..............#"
    "################"
)

class RaycasterEngine:
    def __init__(self):
        # Initial Player coordinates and looking angle
        self.player_x = 2.0
        self.player_y = 2.0
        self.player_a = 0.0  # Angle in radians
        self.running = True

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        screen = []
        
        # Raycasting loop for each horizontal column on screen
        for x in range(SCREEN_WIDTH):
            # Calculate the ray angle projected into the FOV space
            ray_angle = (self.player_a - FOV / 2.0) + (x / SCREEN_WIDTH) * FOV
            
            distance_to_wall = 0.0
            hit_wall = False
            boundary_edge = False

            # Unit vectors representing direction of the ray
            eye_x = math.sin(ray_angle)
            eye_y = math.cos(ray_angle)

            # Incrementally step ray outwards until it finds a wall collision
            while not hit_wall and distance_to_wall < DEPTH:
                distance_to_wall += 0.1
                
                # Compute coordinates of the test point
                test_x = int(self.player_x + eye_x * distance_to_wall)
                test_y = int(self.player_y + eye_y * distance_to_wall)
                
                # Check if ray has exited bounds
                if test_x < 0 or test_x >= MAP_WIDTH or test_y < 0 or test_y >= MAP_HEIGHT:
                    hit_wall = True
                    distance_to_wall = DEPTH
                else:
                    # Check if test cell coordinates lands on a wall tile
                    if MAP[test_y * MAP_WIDTH + test_x] == '#':
                        hit_wall = True
                        
                        # Perfect edge shading logic to outline block corners
                        p = []
                        for tx in range(2):
                            for ty in range(2):
                                vx = float(test_x) + tx - self.player_x
                                vy = float(test_y) + ty - self.player_y
                                d = math.sqrt(vx*vx + vy*vy)
                                dot = (eye_x * vx / d) + (eye_y * vy / d)
                                p.append((d, dot))
                        
                        # Sort closest corners
                        p.sort(key=lambda t: t[0])
                        bound = 0.01
                        if math.acos(p[0][1]) < bound or math.acos(p[1][1]) < bound:
                            boundary_edge = True

            # Calculate height proportions for ceiling and floor based on perspective distance
            ceiling = int((SCREEN_HEIGHT / 2.0) - SCREEN_HEIGHT / float(distance_to_wall if distance_to_wall > 0.1 else 0.1))
            floor = SCREEN_HEIGHT - ceiling

            # Render structural column segments
            for y in range(SCREEN_HEIGHT):
                if y <= ceiling:
                    screen.append(' ') # Sky/Ceiling
                elif y > ceiling and y <= floor:
                    # Shading wall characters based on distance metrics
                    if boundary_edge:          shade = '|' # Corner boundaries
                    elif distance_to_wall <= DEPTH / 4.0: shade = '█' # Ultra close
                    elif distance_to_wall <= DEPTH / 3.0: shade = '▓' # Close
                    elif distance_to_wall <= DEPTH / 2.0: shade = '▒' # Mid-ground
                    elif distance_to_wall <= DEPTH:       shade = '░' # Distant
                    else:                                 shade = ' ' 
                    screen.append(shade)
                else:
                    # Floor shading based on proximity mapping
                    b = 1.0 - (((y - SCREEN_HEIGHT / 2.0)) / (SCREEN_HEIGHT / 2.0))
                    if b < 0.25:   floor_char = 'x'
                    elif b < 0.5:  floor_char = '='
                    elif b < 0.75: floor_char = '-'
                    elif b < 0.9:  floor_char = '.'
                    else:          floor_char = ' '
                    screen.append(floor_char)

        # Output frame buffer content into screen matrix strings
        self.clear_screen()
        print(f"=== 3D ASCII ENGINE === | X: {self.player_x:.2f} Y: {self.player_y:.2f} Angle: {self.player_a:.2f}")
        
        for row in range(SCREEN_HEIGHT):
            start = row * SCREEN_WIDTH
            end = start + SCREEN_WIDTH
            print("".join(screen[start:end]))
            
        print("Controls: W/S (Move), A/D (Rotate) | Q (Quit)")

    def process_input(self):
        # Cross-platform interactive unbuffered keystroke interceptors
        try:
            if os.name == 'nt':
                import msvcrt
                char = msvcrt.getch().decode('utf-8').lower()
            else:
                import tty, termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    char = sys.stdin.read(1).lower()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            char = input("Move: ").strip().lower()

        if char == 'q':
            self.running = False
            return

        # Rotation tracking updates
        if char == 'a':
            self.player_a -= 0.15
        if char == 'd':
            self.player_a += 0.15

        # Forward / Backward vector transformations
        if char == 'w':
            self.player_x += math.sin(self.player_a) * 0.4
            self.player_y += math.cos(self.player_a) * 0.4
            # Collision bounding guard against walls
            if MAP[int(self.player_y) * MAP_WIDTH + int(self.player_x)] == '#':
                self.player_x -= math.sin(self.player_a) * 0.4
                self.player_y -= math.cos(self.player_a) * 0.4

        if char == 's':
            self.player_x -= math.sin(self.player_a) * 0.4
            self.player_y -= math.cos(self.player_a) * 0.4
            # Collision bounding guard against walls
            if MAP[int(self.player_y) * MAP_WIDTH + int(self.player_x)] == '#':
                self.player_x += math.sin(self.player_a) * 0.4
                self.player_y += math.cos(self.player_a) * 0.4

    def run_engine_loop(self):
        while self.running:
            self.render()
            self.process_input()

if __name__ == "__main__":
    engine = RaycasterEngine()
    engine.run_engine_loop()

