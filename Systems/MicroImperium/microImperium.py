import random
import os
import sys
import math
import time

# --- CONSTANTS & CONFIGURATION ---
GALAXY_WIDTH = 40
GALAXY_HEIGHT = 15
MAX_FACTIONS = 4
MAX_TURNS = 100

SYSTEM_NAMES = ["Sol", "Alpha C", "Vega", "Sirius", "Proxima", "Rigel", "Betelgeuse", "Polaris", "Antares", "Aldebaran", "Capella", "Arcturus"]
PLANET_TYPES = ["Terran", "Desert", "Ocean", "Arid", "Barren", "Frozen", "Gas Giant"]
SHIP_TYPES = {
    "Scout":      {"cost": 50,  "hp": 30,  "shields": 10,  "atk": 5,  "range": 5},
    "Corvette":   {"cost": 120, "hp": 70,  "shields": 30,  "atk": 15, "range": 3},
    "Cruiser":    {"cost": 300, "hp": 200, "shields": 100, "atk": 45, "range": 2},
    "Dreadnought":{"cost": 750, "hp": 500, "shields": 300, "atk": 110,"range": 1}
}

# --- DATA STRUCTURES ---

class Ship:
    def __init__(self, name, faction_id, x, y):
        self.name = name
        self.faction_id = faction_id
        self.x = x
        self.y = y
        self.type_data = SHIP_TYPES[name]
        self.hp = self.type_data["hp"]
        self.max_hp = self.type_data["hp"]
        self.shields = self.type_data["shields"]
        self.max_shields = self.type_data["shields"]
        self.atk = self.type_data["atk"]
        self.range = self.type_data["range"]
        self.has_moved = False

    def take_damage(self, amount):
        if self.shields >= amount:
            self.shields -= amount
        else:
            amount -= self.shields
            self.shields = 0
            self.hp -= amount
        return self.hp <= 0

    def recharge(self):
        self.shields = min(self.max_shields, self.shields + int(self.max_shields * 0.25))


class StarSystem:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.planet_type = random.choice(PLANET_TYPES)
        self.minerals = random.randint(10, 50) if self.planet_type != "Barren" else random.randint(5, 15)
        self.owner_id = None  # None = Unclaimed
        self.population = 0
        self.max_population = random.randint(5, 20) if self.planet_type in ["Terran", "Ocean", "Arid"] else random.randint(1, 4)

    def process_production(self):
        if self.owner_id is None:
            return 0
        # Population generates wealth/minerals
        return int(self.population * 5 + self.minerals * 0.5)

    def grow_population(self):
        if self.owner_id is not None and self.population < self.max_population:
            if random.random() < 0.4:
                self.population += 1


class Faction:
    def __init__(self, faction_id, name, color_char, is_player=False):
        self.faction_id = faction_id
        self.name = name
        self.color_char = color_char
        self.is_player = is_player
        self.credits = 400
        self.ships = []
        self.eliminated = False

    def get_total_assets(self, systems):
        owned_systems = [s for s in systems if s.owner_id == self.faction_id]
        return len(owned_systems), len(self.ships)

# --- ENGINE ENGINE ---

class MicroImperiumEngine:
    def __init__(self):
        self.systems = []
        self.factions = []
        self.turn = 1
        self.combat_logs = []
        self.running = True
        
        self.init_galaxy()
        self.init_factions()

    def init_galaxy(self):
        # Seed distinct procedural positions
        used_coords = set()
        for name in SYSTEM_NAMES:
            while True:
                x = random.randint(2, GALAXY_WIDTH - 3)
                y = random.randint(2, GALAXY_HEIGHT - 3)
                if (x, y) not in used_coords and not any(abs(sx - x) < 3 and abs(sy - y) < 2 for sx, sy in used_coords):
                    used_coords.add((x, y))
                    self.systems.append(StarSystem(name, x, y))
                    break

    def init_factions(self):
        # Create user faction
        self.factions.append(Faction(0, "Terran Federation", "P", is_player=True))
        # Create AI rival factions
        self.factions.append(Faction(1, "Zarkon Swarm", "Z"))
        self.factions.append(Faction(2, "Xenon Collective", "X"))
        self.factions.append(Faction(3, "Orion Republic", "O"))

        # Distribute starting home worlds evenly
        for i, faction in enumerate(self.factions):
            home_system = self.systems[i]
            home_system.owner_id = faction.faction_id
            home_system.population = home_system.max_population // 2 + 1
            # Give initial exploration fleet
            faction.ships.append(Ship("Scout", faction.faction_id, home_system.x, home_system.y))
            faction.ships.append(Ship("Corvette", faction.faction_id, home_system.x, home_system.y))

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_map(self):
        self.clear()
        print(f"=== MICRO-IMPERIUM ENGINE === | TURN: {self.turn}/{MAX_TURNS}")
        print("-" * (GALAXY_WIDTH + 2))

        # Dynamic Grid Allocation Map
        grid = [[" " for _ in range(GALAXY_WIDTH)] for _ in range(GALAXY_HEIGHT)]

        # Overlay Star Systems
        for sys_obj in self.systems:
            char = "S"
            if sys_obj.owner_id is not None:
                char = self.factions[sys_obj.owner_id].color_char
            grid[sys_obj.y][sys_obj.x] = char

        # Overlay Fleets (Overwrites system view matrix if co-located)
        for faction in self.factions:
            if faction.eliminated: continue
            for ship in faction.ships:
                # If multiple fleets occupy, show exclamation warning
                if grid[ship.y][ship.x] != " " and grid[ship.y][ship.x] != faction.color_char and grid[ship.y][ship.x] != "S":
                    grid[ship.y][ship.x] = "!"
                else:
                    grid[ship.y][ship.x] = faction.color_char.lower() if faction.is_player else faction.color_char

        for row in grid:
            print("|" + "".join(row) + "|")
        print("-" * (GALAXY_WIDTH + 2))

    def render_hud(self):
        p_faction = self.factions[0]
        sys_owned, ships_owned = p_faction.get_total_assets(self.systems)
        print(f" FACTION: {p_faction.name} | CAPITAL FUNDS: {p_faction.credits} M-Cr")
        print(f" COLONIES CONTROLLED: {sys_owned} | TOTAL FLEET UNITS: {ships_owned}")
        print("=" * (GALAXY_WIDTH + 2))
        print(" Action Options: [M] Fleet Command | [B] Structural Build | [E] Pass Turn | [Q] Retract Game")
        print("-" * (GALAXY_WIDTH + 2))
        
        # Display Combat Log Alerts
        if self.combat_logs:
            for log in self.combat_logs[-3:]:
                print(f" ALERT: {log}")
            print("-" * (GALAXY_WIDTH + 2))

    def run_loop(self):
        while self.running:
            self.check_victory_conditions()
            if not self.running: break

            self.render_map()
            self.render_hud()
            
            choice = input("Dispatch directive: ").strip().lower()
            if choice == 'm':
                self.player_movement_menu()
            elif choice == 'b':
                self.player_build_menu()
            elif choice == 'e':
                self.process_ai_turns()
                self.process_economy_phase()
                self.turn += 1
                if self.turn > MAX_TURNS:
                    self.running = False
            elif choice == 'q':
                self.running = False

    def player_movement_menu(self):
        p_ships = [s for s in self.factions[0].ships if not s.has_moved]
        if not p_ships:
            print("No active ready fleets available this step cycle.")
            time.sleep(1)
            return

        print("\nSelect Fleet Component to Command:")
        for idx, ship in enumerate(p_ships):
            print(f" [{idx}] {ship.name} at Vector ({ship.x}, {ship.y}) [HP:{ship.hp}/{ship.max_hp}]")
        print(" [-1] Return to Main Strategy Desk")

        try:
            sel = int(input("Selection Index: "))
            if sel == -1 or sel >= len(p_ships): return
            ship = p_ships[sel]

            print("\nSelect Path Direction (Numpad controls / Keyboard keys):")
            print("  [W] North | [S] South | [A] West | [D] East")
            move = input("Vector Direction: ").strip().lower()

            dx, dy = 0, 0
            if move == 'w': dy = -1
            elif move == 's': dy = 1
            elif move == 'a': dx = -1
            elif move == 'd': dx = 1
            else: return

            # Translate vectors bounds checking
            nx, ny = max(0, min(GALAXY_WIDTH - 1, ship.x + dx)), max(0, min(GALAXY_HEIGHT - 1, ship.y + dy))
            ship.x, ship.y = nx, ny
            ship.has_moved = True

            # Process system discovery or colonizations checks
            for sys_obj in self.systems:
                if sys_obj.x == nx and sys_obj.y == ny:
                    if sys_obj.owner_id is None:
                        sys_obj.owner_id = 0
                        sys_obj.population = 1
                        self.combat_logs.append(f"Established new outpost colonies on Planet {sys_obj.name} ({sys_obj.planet_type})!")
                    elif sys_obj.owner_id != 0:
                        self.combat_logs.append(f"Fleet encountered sovereign lines of Faction {self.factions[sys_obj.owner_id].name} at {sys_obj.name}.")

            self.resolve_space_battles()

        except ValueError:
            pass

    def player_build_menu(self):
        p_faction = self.factions[0]
        owned_systems = [s for s in self.systems if s.owner_id == 0]
        
        if not owned_systems:
            print("No shipyard systems operational.")
            time.sleep(1)
            return

        print("\nSelect Production Orbital Station Hub:")
        for idx, sys_obj in enumerate(owned_systems):
            print(f" [{idx}] Colony {sys_obj.name} (Pop: {sys_obj.population}/{sys_obj.max_population})")
        
        try:
            sel = int(input("Select System: "))
            if sel < 0 or sel >= len(owned_systems): return
            target_sys = owned_systems[sel]

            print("\nAvailable Fleet Engineering Blueprints:")
            for s_name, data in SHIP_TYPES.items():
                print(f" - {s_name:<12} Cost: {data['cost']:<5} M-Cr | Atk Power: {data['atk']}")

            build_choice = input("Enter architecture name to lay hull: ").strip().capitalize()
            if build_choice in SHIP_TYPES:
                cost = SHIP_TYPES[build_choice]["cost"]
                if p_faction.credits >= cost:
                    p_faction.credits -= cost
                    p_faction.ships.append(Ship(build_choice, 0, target_sys.x, target_sys.y))
                    self.combat_logs.append(f"Assembled massive {build_choice} hull components over {target_sys.name} dockyards.")
                else:
                    print("Insufficient allocation capital budget units.")
                    time.sleep(1)
        except ValueError:
            pass

    def process_ai_turns(self):
        # AI Faction simple algorithmic behavior layer
        for faction in self.factions:
            if faction.is_player or faction.eliminated: continue

            owned_systems = [s for s in self.systems if s.owner_id == faction.faction_id]
            
            # 1. Macro Economic Check: Build ships if funds exist
            if faction.credits >= 300 and owned_systems:
                spawn_sys = random.choice(owned_systems)
                s_type = random.choice(["Scout", "Corvette", "Cruiser"])
                faction.credits -= SHIP_TYPES[s_type]["cost"]
                faction.ships.append(Ship(s_type, faction.faction_id, spawn_sys.x, spawn_sys.y))

            # 2. Strategic Micro movements logic
            for ship in faction.ships:
                # Seek nearest unclaimed star systems or hunt enemy player hulls
                target_x, target_y = GALAXY_WIDTH // 2, GALAXY_HEIGHT // 2
                closest_dist = 9999
                
                for s in self.systems:
                    if s.owner_id != faction.faction_id:
                        dist = math.sqrt((s.x - ship.x)**2 + (s.y - ship.y)**2)
                        if dist < closest_dist:
                            closest_dist = dist
                            target_x, target_y = s.x, s.y

                # Calculate offset step metrics towards destination vectors
                dx = 1 if target_x > ship.x else (-1 if target_x < ship.x else 0)
                dy = 1 if target_y > ship.y else (-1 if target_y < ship.y else 0)
                
                ship.x = max(0, min(GALAXY_WIDTH - 1, ship.x + dx))
                ship.y = max(0, min(GALAXY_HEIGHT - 1, ship.y + dy))

                # Capture checks
                for sys_obj in self.systems:
                    if sys_obj.x == ship.x and sys_obj.y == ship.y and sys_obj.owner_id != faction.faction_id:
                        if sys_obj.owner_id == 0:
                            self.combat_logs.append(f"⚠️ Warning: Rival AI units have invaded colony assets at outposts {sys_obj.name}!")
                        sys_obj.owner_id = faction.faction_id
                        sys_obj.population = 1

        self.resolve_space_battles()

    def resolve_space_battles(self):
        # Group coordinate mappings
        coord_map = {}
        for faction in self.factions:
            if faction.eliminated: continue
            for ship in faction.ships:
                pos = (ship.x, ship.y)
                if pos not in coord_map:
                    coord_map[pos] = []
                coord_map[pos].append(ship)

        # Evaluate localized battle rounds
        for pos, ships in coord_map.items():
            factions_present = set(s.faction_id for s in ships)
            if len(factions_present) > 1:
                # Execute instant automated attrition loop until 1 side holds matrix grid
                self.combat_logs.append(f"💥 Dynamic Fleet Engagement localized inside Vector coordinates {pos}!")
                
                while len(set(s.faction_id for s in ships if s.hp > 0)) > 1:
                    for ship in ships:
                        if ship.hp <= 0: continue
                        # Find hostile targets in local pile
                        targets = [t for t in ships if t.faction_id != ship.faction_id and t.hp > 0]
                        if targets:
                            target = random.choice(targets)
                            destroyed = target.take_damage(ship.atk)
                            if destroyed:
                                self.combat_logs.append(f" -> A {target.name} hull belonging to Faction [{target.faction_id}] exploded.")

                # Remove dead debris hulls
                for faction in self.factions:
                    faction.ships = [s for s in faction.ships if s.hp > 0]

    def process_economy_phase(self):
        for faction in self.factions:
            if faction.eliminated: continue
            
            # Gather taxes from output pipelines
            income = 25 # Core base passive stipend
            for sys_obj in self.systems:
                if sys_obj.owner_id == faction.faction_id:
                    income += sys_obj.process_production()
                    sys_obj.grow_population()
            
            faction.credits += income
            
            # Reset ship shields and step logs counters
            for ship in faction.ships:
                ship.recharge()
                ship.has_moved = False

    def check_victory_conditions(self):
        # Scan if AI entities have expired or player holds 0 ships and bases
        for faction in self.factions:
            if not faction.eliminated:
                sys_cnt, ship_cnt = faction.get_total_assets(self.systems)
                if sys_cnt == 0 and ship_cnt == 0:
                    faction.eliminated = True
                    self.combat_logs.append(f"❌ Faction [{faction.name}] has been wiped from local logs history matrices!")

        p_faction = self.factions[0]
        if p_faction.eliminated:
            self.render_map()
            print("\n💀 DEFEAT! Your empire fell into celestial space debris... Game Over. 💀")
            self.running = False
            return

        active_rivals = [f for f in self.factions if not f.eliminated and not f.is_player]
        if not active_rivals:
            self.render_map()
            print("\n👑 VICTORY! You purged the dark sectors and established ultimate galactic hegemony! 👑")
            self.running = False

# --- ENTRY SYSTEM DIRECT LINK ---

if __name__ == "__main__":
    game = MicroImperiumEngine()
    game.run_loop()
