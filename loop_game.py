import time
import sys

def typewriter(text):
    """Makes the text scroll naturally instead of just printing instantly."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.03)
    print()

def start_game():
    # These variables track our progress across the loops
    loop_count = 1
    has_key = False
    
    while True:
        typewriter(f"\n--- LOOP NUMBER {loop_count} ---")
        typewriter("You wake up on a cold stone floor. The ceiling is cracking overhead!")
        typewriter("You have exactly 5 moves before the temple collapses.")
        
        moves_left = 5
        current_room = "Main Hall"
        
        # This is the inner loop for the current life
        while moves_left > 0:
            print(f"\n[Moves left: {moves_left}]")
            
            if current_room == "Main Hall":
                typewriter("You are in the Main Hall. Massive pillars are shaking.")
                typewriter("Options: 1. Examine the Gold Door | 2. Go to the Sun Room")
                choice = input("> ")
                
                if choice == "1":
                    if has_key:
                        typewriter("You insert the Sun Key into the Gold Door... IT OPENS! You escape!")
                        typewriter("CONGRATULATIONS! You broke the loop!")
                        return # Exits the entire game
                    else:
                        typewriter("The Gold Door is locked tight. It has a sun-shaped engraving.")
                        moves_left -= 1
                elif choice == "2":
                    current_room = "Sun Room"
                    moves_left -= 1
                else:
                    print("Invalid choice, time is ticking!")
            
            elif current_room == "Sun Room":
                typewriter("You are in the Sun Room. Sunlight beams down on an altar.")
                if not has_key:
                    typewriter("Options: 1. Search the altar | 2. Go back to Main Hall")
                else:
                    typewriter("The altar is empty. Options: 1. Go back to Main Hall")
                
                choice = input("> ")
                
                if choice == "1" and not has_key:
                    typewriter("You found the Sun Key glowing on the altar!")
                    has_key = True
                    moves_left -= 1
                elif choice == "2" or (choice == "1" and has_key):
                    current_room = "Main Hall"
                    moves_left -= 1
                else:
                    print("Invalid choice!")
                    
        # If the inner loop finishes because moves_left reached 0
        typewriter("\nCRASH! The ceiling caves in. Everything goes dark...")
        time.sleep(1.5)
        loop_count += 1
        # The while loop continues, restarting the game but keeping has_key and loop_count!

# Run the game
start_game()