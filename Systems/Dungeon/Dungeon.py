import random
import os
import sys
import time

# --- CONFIGURATION & CONSTANTS ---
MAP_WIDTH = 50
MAP_HEIGHT = 20
VIEWPORT_WIDTH = 50
VIEWPORT_HEIGHT = 15

# Tile characters
TILE_WALL = '#'
TILE_FLOOR = '.'
TILE_PLAYER = '@'
TILE_MONSTER_ORC = 'O'
TILE_MONSTER_GOBLIN = 'g'
TILE_MONSTER_DRAGON = 'D'
TILE_ITEM_POTION = 'P'
TILE_ITEM_SWORD = 'S'
TILE_STAIRS = '>'

# --- ENTITY CLASSES ---

class Item:
    def __init__(self, x, y, name, item_type, value):
        self.x = x
        self.y = y
        self.name = name
        self.item_type = item_type  # "heal", "equip_atk"
        self.value = value

class Monster:
    def __init__(self, x, y, name, char, hp, max_hp, atk, xp_value):
        self.x = x
        self.y = y
        self.name = name
        self.char = char
        self.hp = hp
        self.max_hp = max_hp
        self.atk = atk
        self.xp_value = xp_value

    def take_damage(self, amount):
        self.hp -= amount
        return self.hp <= 0

class Player:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.atk = 15
        self.weapon_bonus = 0
        self.level = 1
        self.xp = 0
        self.xp_needed = 100
        self.inventory = []

    def get_total_atk(self):
        return self.atk + self.weapon_bonus

    def add_xp(self, amount, log):
        self.xp += amount
        log.append(f"You gained {amount} XP!")
        if self.xp >= self.xp_needed:
            self.level_up(log)

    def level_up(self, log):
        self.xp -= self.xp_needed
        self.level += 1
        self.xp_needed = int(self.xp_needed * 1.5)
        self.max_hp += 20
        self.hp = self.max_hp
        self.atk += 5
        log.append(f"★ LEVEL UP! You reached Level {self.level}! Max HP and ATK increased! ★")

# --- GAME MAP CLASS ---

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[TILE_WALL for _ in range(width)] for _ in range(height)]
        self.rooms = []
        self.monsters = []
        self.items = []
        self.stairs_x = -1
        self.stairs_y = -1

    def generate_map(self, depth):
        self.tiles = [[TILE_WALL for _ in range(self.width)] for _ in range(self.height)]
        self.rooms = []
        self.monsters = []
        self.items = []

        min_size = 5
        max_size = 10
        max_rooms = 8

        for _ in range(max_rooms):
            w = random.randint(min_size, max_size)
            h = random.randint(min_size, max_size)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            new_room = Room(x, y, w, h)
            
            # Check for overlaps
            failed = False
            for other_room in self.rooms:
                if new_room.intersects(other_room):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)

                if len(self.rooms) > 0:
                    # Connect to the previous room
                    prev_x, prev_y = self.rooms[-1].center()
                    new_x, new_y = new_room.center()

                    if random.choice([True, False]):
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.rooms.append(new_room)

        # Place stairs in the last room
        if self.rooms:
            sx, sy = self.rooms[-1].center()
            self.stairs_x, self.stairs_y = sx, sy
            self.tiles[sy][sx] = TILE_STAIRS

        # Populate rooms with life and loot
        for i, room in enumerate(self.rooms):
            if i == 0:
                continue # Skip player spawn room
            self.populate_room(room, depth)

    def create_room(self, room):
        for y in range(room.y1 + 1, room.y2):
            for x in range(room.x1 + 1, room.x2):
                self.tiles[y][x] = TILE_FLOOR

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[y][x] = TILE_FLOOR

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[y][x] = TILE_FLOOR

    def populate_room(self, room, depth):
        # Monster spawning
        num_monsters = random.randint(0, 2)
        for _ in range(num_monsters):
            mx = random.randint(room.x1 + 1, room.x2 - 1)
            my = random.randint(room.y1 + 1, room.y2 - 1)
            
            if not any(m.x == mx and m.y == my for m in self.monsters):
                roll = random.random()
                if roll < 0.6:
                    # Goblin
                    monster = Monster(mx, my, "Goblin", TILE_MONSTER_GOBLIN, 15 + depth * 3, 15 + depth * 3, 5 + depth, 20)
                elif roll < 0.9:
                    # Orc
                    monster = Monster(mx, my, "Orc", TILE_MONSTER_ORC, 30 + depth * 5, 30 + depth * 5, 8 + depth, 45)
                else:
                    # Dragon (Mini-boss)
                    monster = Monster(mx, my, "Dragon", TILE_MONSTER_DRAGON, 60 + depth * 10, 60 + depth * 10, 15 + depth * 2, 120)
                self.monsters.append(monster)

        # Item spawning
        if random.random() < 0.4:
            ix = random.randint(room.x1 + 1, room.x2 - 1)
            iy = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(i.x == ix and i.y == iy for i in self.items):
                if random.choice([True, False]):
                    item = Item(ix, iy, "Health Potion", "heal", 30 + depth * 5)
                else:
                    item = Item(ix, iy, "Iron Sword", "equip_atk", 5 + depth * 2)
                self.items.append(item)

    def is_blocked(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.tiles[y][x] == TILE_WALL


class Room:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersects(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


# --- ENGINE CORE ---

class GameEngine:
    def __init__(self):
        self.player = Player()
        self.map_depth = 1
        self.game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
        self.log = ["Welcome to the Dungeon! Use WASD to move/attack.", "Find the stairs (>) to go deeper."]
        self.running = True
        self.init_floor()

    def init_floor(self):
        self.game_map.generate_map(self.map_depth)
        # Spawn player in the center of the first room
        px, py = self.game_map.rooms[0].center()
        self.player.x = px
        self.player.y = py

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        self.clear_screen()
        print(f"=== DUNGEON CRAWLER (FLOOR {self.map_depth}) ===")
        
        # Build rendering screen with overlaying entities
        display_grid = [[self.game_map.tiles[y][x] for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]

        # Overlay items
        for item in self.game_map.items:
            display_grid[item.y][item.x] = TILE_ITEM_POTION if item.item_type == "heal" else TILE_ITEM_SWORD

        # Overlay monsters
        for monster in self.game_map.monsters:
            display_grid[monster.y][monster.x] = monster.char

        # Overlay Player
        display_grid[self.player.y][self.player.x] = TILE_PLAYER

        # Print Viewport
        for y in range(MAP_HEIGHT):
            row_str = "".join(display_grid[y])
            print(row_str)

        # Print UI Stats
        print("=" * MAP_WIDTH)
        print(f" HP: {self.player.hp}/{self.player.max_hp}  |  ATK: {self.player.get_total_atk()} (Base:{self.player.atk} + Equip:{self.player.weapon_bonus})")
        print(f" Level: {self.player.level}  |  XP: {self.player.xp}/{self.player.xp_needed}")
        
        # Print Inventory
        inv_names = [item.name for item in self.player.inventory]
        print(f" Inventory: {', '.join(inv_names) if inv_names else '[Empty]'}")
        print("=" * MAP_WIDTH)
        
        # Print Log (Keep last 3 messages)
        for msg in self.log[-3:]:
            print(f" * {msg}")
        print("=" * MAP_WIDTH)

    def handle_input(self):
        try:
            # Simple terminal cross-platform input capturing
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
            # Fallback
            char = input("Move (W/A/S/D) / Use Item (U) / Quit (Q): ").strip().lower()

        if char == 'q':
            self.running = False
            return

        dx, dy = 0, 0
        if char == 'w': dy = -1
        elif char == 's': dy = 1
        elif char == 'a': dx = -1
        elif char == 'd': dx = 1
        elif char == 'u':
            self.use_item_menu()
            return
        else:
            return # Invalid turn input, don't execute a frame

        self.move_player(dx, dy)
        self.update_monsters()

    def move_player(self, dx, dy):
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if self.game_map.is_blocked(new_x, new_y):
            return

        # Check for combat encounter
        target_monster = None
        for m in self.game_map.monsters:
            if m.x == new_x and m.y == new_y:
                target_monster = m
                break

        if target_monster:
            # Fight!
            damage = self.player.get_total_atk()
            killed = target_monster.take_damage(damage)
            self.log.append(f"You strike the {target_monster.name} for {damage} damage!")
            
            if killed:
                self.log.append(f"You killed the {target_monster.name}!")
                self.player.add_xp(target_monster.xp_value, self.log)
                self.game_map.monsters.remove(target_monster)
            return

        # Check for item pickup
        target_item = None
        for item in self.game_map.items:
            if item.x == new_x and item.y == new_y:
                target_item = item
                break

        if target_item:
            self.player.inventory.append(target_item)
            self.log.append(f"Picked up: {target_item.name}!")
            self.game_map.items.remove(target_item)

        # Execute Movement
        self.player.x = new_x
        self.player.y = new_y

        # Check if stepped on stairs
        if self.player.x == self.game_map.stairs_x and self.player.y == self.game_map.stairs_y:
            self.map_depth += 1
            self.log.append(f"You descend deeper into Floor {self.map_depth}...")
            self.init_floor()

    def update_monsters(self):
        # Basic hostile monster AI
        for m in self.game_map.monsters:
            dist_x = abs(self.player.x - m.x)
            dist_y = abs(self.player.y - m.y)

            # If adjacent, attack the player
            if dist_x <= 1 and dist_y <= 1 and (dist_x != dist_y or dist_x == 1):
                damage = m.atk
                self.player.hp -= damage
                self.log.append(f"The {m.name} hits you for {damage} damage!")
                if self.player.hp <= 0:
                    self.log.append("⚡ You have died! GAME OVER ⚡")
                    self.running = False
            else:
                # Move closer to the player
                dx = 1 if self.player.x > m.x else (-1 if self.player.x < m.x else 0)
                dy = 1 if self.player.y > m.y else (-1 if self.player.y < m.y else 0)

                # Prioritize horizontal or vertical movement
                if dx != 0 and not self.game_map.is_blocked(m.x + dx, m.y) and not any(other.x == m.x + dx and other.y == m.y for other in self.game_map.monsters):
                    m.x += dx
                elif dy != 0 and not self.game_map.is_blocked(m.x, m.y + dy) and not any(other.x == m.x and other.y == m.y + dy for other in self.game_map.monsters):
                    m.y += dy

    def use_item_menu(self):
        if not self.player.inventory:
            self.log.append("You have no items to use.")
            return

        self.clear_screen()
        print("=== INVENTORY ===")
        for index, item in enumerate(self.player.inventory):
            print(f" [{index}] {item.name} ({item.item_type.upper()}: +{item.value})")
        print("=================")
        print("Press the number key of the item to use, or any other key to cancel.")
        
        try:
            if os.name == 'nt':
                import msvcrt
                char = msvcrt.getch().decode('utf-8')
            else:
                import tty, termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    char = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
            selection = int(char)
            if 0 <= selection < len(self.player.inventory):
                item = self.player.inventory.pop(selection)
                if item.item_type == "heal":
                    self.player.hp = min(self.player.max_hp, self.player.hp + item.value)
                    self.log.append(f"Used {item.name}. Restored {item.value} HP!")
                elif item.item_type == "equip_atk":
                    # Equip the weapon
                    self.player.weapon_bonus = item.value
                    self.log.append(f"Equipped {item.name}. Attack increased by {item.value}!")
            else:
                self.log.append("Invalid selection.")
        except ValueError:
            self.log.append("Action canceled.")

# --- ENTRY POINT ---

if __name__ == "__main__":
    game = GameEngine()
    while game.running:
        game.render()
        game.handle_input()
    
    # Final game screen
    game.render()
    print("\nThanks for playing!")
