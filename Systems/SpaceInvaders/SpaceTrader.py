import random
import os
import sys
import math

# --- CONFIGURATION & ECONOMY CONSTANTS ---
GALAXY_SIZE = 8
MARKET_GOODS = {
    "Water":     {"base_price": 10,   "variance": 3,   "illegal": False},
    "Food":      {"base_price": 30,   "variance": 7,   "illegal": False},
    "Fuel":      {"base_price": 50,   "variance": 10,  "illegal": False},
    "Medicines": {"base_price": 150,  "variance": 35,  "illegal": False},
    "Firearms":  {"base_price": 400,  "variance": 90,  "illegal": True},
    "Narcotics": {"base_price": 800,  "variance": 250, "illegal": True},
}

SYSTEM_TYPES = ["Agricultural", "Industrial", "Technological", "Anarchic", "Barren"]

# --- CORE DATA CLASSES ---

class StarSystem:
    def __init__(self, name, economy_type, x, y):
        self.name = name
        self.economy_type = economy_type
        self.x = x
        self.y = y
        self.market = {}
        self.generate_market()

    def generate_market(self):
        for good, stats in MARKET_GOODS.items():
            price = stats["base_price"] + random.randint(-stats["variance"], stats["variance"])
            
            # Apply economy multipliers
            if self.economy_type == "Agricultural":
                if good == "Food" or good == "Water": price = int(price * 0.6)
                if good == "Medicines": price = int(price * 1.3)
            elif self.economy_type == "Industrial":
                if good == "Fuel": price = int(price * 0.7)
                if good == "Food": price = int(price * 1.2)
            elif self.economy_type == "Technological":
                if good == "Medicines": price = int(price * 0.5)
                if good in ["Firearms", "Narcotics"]: price = int(price * 1.4)
            elif self.economy_type == "Anarchic":
                if good in ["Firearms", "Narcotics"]: price = int(price * 0.5)
                if good in ["Food", "Medicines"]: price = int(price * 1.5)
            
            # Ensure price never drops to zero or negative
            self.market[good] = max(2, price)


class Spaceship:
    def __init__(self):
        self.name = "The Starbounder"
        self.hull = 100
        self.max_hull = 100
        self.shields = 50
        self.max_shields = 50
        self.fuel = 40
        self.max_fuel = 40
        self.cargo_capacity = 15
        self.cargo = {good: 0 for good in MARKET_GOODS}
        self.weapon_power = 12
        self.shield_recharge = 5

    def cargo_used(self):
        return sum(self.cargo.values())

    def free_cargo(self):
        return self.cargo_capacity - self.cargo_used()


class Player:
    def __init__(self):
        self.credits = 1000
        self.bounty = 0
        self.days_passed = 0
        self.ship = Spaceship()

# --- SIMULATION ENGINE ---

class SpaceSimulation:
    def __init__(self):
        self.player = Player()
        self.systems = []
        self.current_system = None
        self.log = ["Welcome to the Deep Space Trading Simulator.", "Earn 20,000 Credits to retire rich."]
        self.running = True
        self.build_galaxy()

    def build_galaxy(self):
        names = ["Alpha Centauri", "Sol Primary", "Vega Prime", "Arcturus-9", "Sirius Outpost", "Kepler-186", "Glise Sector", "Tatoo Prime"]
        coords = [(0,0), (3,4), (-2,5), (6,-1), (-5,-4), (1,-6), (-7,2), (4,7)]
        
        for i in range(min(len(names), GALAXY_SIZE)):
            econ = random.choice(SYSTEM_TYPES)
            sys_obj = StarSystem(names[i], econ, coords[i][0], coords[i][1])
            self.systems.append(sys_obj)
        
        self.current_system = self.systems[0]

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_hud(self):
        self.clear()
        print("=" * 60)
        print(f" LOCATION: {self.current_system.name} ({self.current_system.economy_type} System)")
        print(f" TIME: Day {self.player.days_passed} | CREDITS: {self.player.credits} cr | BOUNTY: {self.player.bounty}")
        print("-" * 60)
        s = self.player.ship
        print(f" HULL: {s.hull}/{s.max_hull} | SHIELDS: {s.shields}/{s.max_shields} | FUEL: {s.fuel}/{s.max_fuel} ly")
        print(f" CARGO BAY: {s.cargo_used()}/{s.cargo_capacity} units used")
        for k, v in s.cargo.items():
            if v > 0:
                print(f"  > {k}: {v} units")
        print("=" * 60)
        for msg in self.log[-3:]:
            print(f" * {msg}")
        print("=" * 60)

    def run(self):
        while self.running:
            if self.player.credits >= 20000:
                self.render_hud()
                print("\n🎉 CELEBRATION! You accumulated 20,000 credits and safely retired to a luxury resort planet! You Win! 🎉")
                break
            if self.player.ship.hull <= 0:
                self.render_hud()
                print("\n💀 GAME OVER! Your ship was blown to space debris... 💀")
                break

            self.render_hud()
            print("Command Actions:")
            print(" [M] Open Local Market")
            print(" [N] Navigate to Next Star System")
            print(" [R] Dock at Maintenance Station (Repair / Refuel)")
            print(" [Q] Abandon Game")
            
            choice = input("\nEnter Command: ").strip().lower()
            if choice == 'm':
                self.run_market()
            elif choice == 'n':
                self.run_navigation()
            elif choice == 'r':
                self.run_maintenance()
            elif choice == 'q':
                self.running = False

    def run_market(self):
        market_loop = True
        while market_loop:
            self.render_hud()
            print(f"--- LOCAL COMMERCE: {self.current_system.name} ---")
            print(f"{'Commodity':<15}{'Local Price':<15}{'Status':<15}")
            for good, price in self.current_system.market.items():
                illegal_str = "[ILLEGAL]" if MARKET_GOODS[good]["illegal"] else ""
                print(f" [{good[0]}] {good:<11} {price:<15} {illegal_str}")
            print("------------------------------------------------------------")
            print(" Actions: [B] Buy Item | [S] Sell Item | [E] Exit Market")
            
            action = input("Select Action: ").strip().lower()
            if action == 'e':
                market_loop = False
            elif action in ['b', 's']:
                item_init = input("Type the full name of commodity: ").strip().capitalize()
                if item_init not in MARKET_GOODS:
                    self.log.append("Unknown commodity type.")
                    continue
                
                price = self.current_system.market[item_init]
                if action == 'b':
                    if self.player.ship.free_cargo() <= 0:
                        self.log.append("No free space in cargo holds!")
                        continue
                    if self.player.credits < price:
                        self.log.append("Insufficient credits available.")
                        continue
                    
                    self.player.credits -= price
                    self.player.ship.cargo[item_init] += 1
                    self.log.append(f"Purchased 1 unit of {item_init}.")
                else:
                    if self.player.ship.cargo[item_init] <= 0:
                        self.log.append(f"You don't own any {item_init} to sell.")
                        continue
                    
                    self.player.credits += price
                    self.player.ship.cargo[item_init] -= 1
                    if MARKET_GOODS[item_init]["illegal"] and self.current_system.economy_type != "Anarchic":
                        self.player.bounty += 150
                        self.log.append(f"Sold illicit {item_init}! Local security flagged your hull.")
                    else:
                        self.log.append(f"Sold 1 unit of {item_init}.")

    def run_maintenance(self):
        self.render_hud()
        print("--- SPACEPORT MAINTENANCE BAY ---")
        print(" [F] Refuel Tank (10 credits per Light Year)")
        print(" [H] Patch Hull Plates (15 credits per HP)")
        print(" [E] Undock")
        
        choice = input("\nSelect service: ").strip().lower()
        ship = self.player.ship
        if choice == 'f':
            needed = ship.max_fuel - ship.fuel
            cost = needed * 10
            if cost == 0:
                self.log.append("Fuel cells already full.")
            elif self.player.credits >= cost:
                self.player.credits -= cost
                ship.fuel = ship.max_fuel
                self.log.append("Tank completely refueled.")
            else:
                self.log.append("Not enough funds for full refuel.")
        elif choice == 'h':
            needed = ship.max_hull - ship.hull
            cost = needed * 15
            if cost == 0:
                self.log.append("Hull plates pristine.")
            elif self.player.credits >= cost:
                self.player.credits -= cost
                ship.hull = ship.max_hull
                self.log.append("Hull integrity completely restored.")
            else:
                self.log.append("Not enough funds for complete hull repair.")

    def run_navigation(self):
        self.render_hud()
        print("--- GALAXY NAVIGATION INDEX ---")
        valid_destinations = []
        idx = 1
        
        for sys_obj in self.systems:
            if sys_obj == self.current_system:
                continue
            
            # Distance computation via Pythagorean theorem
            dist = math.ceil(math.sqrt((sys_obj.x - self.current_system.x)**2 + (sys_obj.y - self.current_system.y)**2))
            print(f" [{idx}] {sys_obj.name:<18} (Dist: {dist} ly) | Type: {sys_obj.economy_type}")
            valid_destinations.append((sys_obj, dist))
            idx += 1
            
        print(" [0] Cancel Warp")
        
        try:
            sel = int(input("\nInput hyperspace vector index: "))
            if sel == 0: return
            if 1 <= sel <= len(valid_destinations):
                target, distance = valid_destinations[sel - 1]
                if self.player.ship.fuel < distance:
                    self.log.append("Hyperspace execution aborted: Insufficient fuel!")
                    return
                
                # Deduct fuel and execute hyperjump
                self.player.ship.fuel -= distance
                self.player.days_passed += max(1, distance // 2)
                self.current_system = target
                self.log.append(f"Warp Drive Complete. Welcome to {target.name}.")
                
                # Check for space encounter mid-warp
                self.trigger_random_encounter()
        except ValueError:
            self.log.append("Navigation calculations corrupted.")

    def trigger_random_encounter(self):
        roll = random.random()
        # 35% chance of an encounter happening during the warp jump
        if roll < 0.15:
            self.encounter_pirate()
        elif roll < 0.25:
            self.encounter_asteroid()
        elif roll < 0.35:
            self.encounter_trader()

    def encounter_pirate(self):
        p_hp = random.randint(30, 60)
        p_atk = random.randint(6, 12)
        self.log.append("⚠️ EMERGENCY! An outlaw raider has dropped you out of warp speed!")
        
        while p_hp > 0 and self.player.ship.hull > 0:
            self.render_hud()
            print(f"⚔️ PIRATE INTERDICTION ⚔️")
            print(f" Raider Hull Strength: {p_hp} HP | Raider Targeting Systems: Active")
            print("-" * 60)
            print(" Tactics: [A] Cycle Weapon Batteries | [F] Push Full Power to Engines")
            
            act = input("Input strategy: ").strip().lower()
            if act == 'a':
                # Player fires weapon batteries
                dmg_to_pirate = random.randint(5, self.player.ship.weapon_power)
                p_hp -= dmg_to_pirate
                self.log.append(f"Laser batteries hit pirate for {dmg_to_pirate} damage.")
                
                if p_hp <= 0:
                    reward = random.randint(200, 600)
                    self.player.credits += reward
                    self.log.append(f"💥 Exploded pirate vessel! Salvaged {reward} credits from wreckage.")
                    break
            elif act == 'f':
                # Escape attempt
                if random.random() > 0.4:
                    self.log.append("Engines flared hot! You broke interdiction and escaped.")
                    break
                else:
                    self.log.append("Escape failed! Pirate tracking systems locked your vectors.")

            # Pirate turn to retaliate
            pirate_dmg = max(0, random.randint(3, p_atk))
            if self.player.ship.shields > 0:
                self.player.ship.shields -= pirate_dmg
                if self.player.ship.shields < 0:
                    self.player.ship.hull += self.player.ship.shields
                    self.player.ship.shields = 0
                self.log.append(f"Shields absorbed pirate blast. (Lost {pirate_dmg} capacity)")
            else:
                self.player.ship.hull -= pirate_dmg
                self.log.append(f"🔴 Direct hit! Hull sustained {pirate_dmg} dynamic structural damage!")
                
            # Passive system recharge round
            self.player.ship.shields = min(self.player.ship.max_shields, self.player.ship.shields + self.player.ship.shield_recharge)

    def encounter_asteroid(self):
        self.log.append("☄️ Navigation alert: Passing through a dense rogue asteroid belt.")
        self.render_hud()
        print("An asteroid drifts directly into your flight path!")
        print(" [E] Perform evasive rolls")
        print(" [B] Brace for impact armor deflection")
        
        choice = input("Reaction: ").strip().lower()
        if choice == 'e':
            if random.random() > 0.3:
                self.log.append("Smooth flying. You threaded the needle through the debris.")
            else:
                dmg = random.randint(10, 25)
                self.player.ship.hull -= dmg
                self.log.append(f"Clip shot! Asteroid clipped the side panels doing {dmg} damage.")
        else:
            dmg = random.randint(5, 15)
            self.player.ship.hull -= dmg
            self.log.append(f"Braced collision. Structural integrity down by {dmg} points.")

    def encounter_trader(self):
        self.log.append("📡 Long-range ping: A wandering bulk merchant vessel signals you.")
        self.render_hud()
        print("The wandering trader offers a quick inventory clearance:")
        print(" Buy 1 Fuel canister for a flat rate of 25 credits? [Y/N]")
        
        choice = input("Response: ").strip().lower()
        if choice == 'y':
            if self.player.credits >= 25:
                self.player.credits -= 25
                self.player.ship.fuel = min(self.player.ship.max_fuel, self.player.ship.fuel + 5)
                self.log.append("Topped off fuel system by 5 light years.")
            else:
                self.log.append("Transaction declined: Insufficient capital.")
        else:
            self.log.append("Saluted and moved along your trajectory.")

# --- ENTRY POINT ---

if __name__ == "__main__":
    simulation = SpaceSimulation()
    simulation.run()
