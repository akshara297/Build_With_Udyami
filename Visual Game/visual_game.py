import pygame
import sys
import time

pygame.init()

# 1. Screen Setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Temple Time Loop - Final Edition")

# 2. Colors
BLACK = (20, 20, 20)
PLAYER_COLOR = (255, 100, 50)       # Orange-Red
GOLD_DOOR_COLOR = (255, 215, 0)     # Gold
SUN_DOOR_COLOR = (255, 255, 150)    # Soft Yellow
SHADOW_DOOR_COLOR = (70, 70, 90)    # Dark Grey/Blue
CHEST_COLOR = (139, 69, 19)         # Brown
CLUE_COLOR = (0, 255, 255)          # Neon Cyan
TEXT_COLOR = (255, 255, 255)
RED = (255, 0, 0)

# 3. Game State & Across-Loop Variables
loop_count = 1
has_key = False
discovered_code = False

# Inner-loop variables (reset every life)
current_room = "MAIN_HALL"
player_x = 400
player_y = 450
player_speed = 5
player_size = 30
energy = 1000  # Decreases as you move

# Layout Map Rectangles
gold_door = pygame.Rect(350, 50, 100, 40)
sun_door = pygame.Rect(50, 250, 40, 100)
shadow_door = pygame.Rect(710, 250, 40, 100)
chest_rect = pygame.Rect(200, 300, 50, 50)       # In Sun Room
clue_rect = pygame.Rect(400, 300, 40, 40)         # In Shadow Room

font = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()

# --- MAIN LOOP ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Movement Check
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_LEFT]:  
        player_x -= player_speed
        moved = True
    if keys[pygame.K_RIGHT]: 
        player_x += player_speed
        moved = True
    if keys[pygame.K_UP]:    
        player_y -= player_speed
        moved = True
    if keys[pygame.K_DOWN]:  
        player_y += player_speed
        moved = True

    # Lose energy if moving
    if moved:
        energy -= 2

    # Screen Boundaries
    if player_x < 0: player_x = 0
    if player_x > SCREEN_WIDTH - player_size: player_x = SCREEN_WIDTH - player_size
    if player_y < 0: player_y = 0
    if player_y > SCREEN_HEIGHT - player_size: player_y = SCREEN_HEIGHT - player_size

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    # --- TIME LOOP DEATH MECHANIC ---
    if energy <= 0:
        # Flash Screen Red on Collapse
        screen.fill(RED)
        pygame.display.flip()
        time.sleep(1.0)
        
        # Reset current life state
        loop_count += 1
        energy = 1000
        current_room = "MAIN_HALL"
        player_x = 400
        player_y = 450
        continue

    # --- ROOM LOGIC & COLLISIONS ---
    if current_room == "MAIN_HALL":
        if player_rect.colliderect(gold_door):
            if has_key:
                # WIN CONDITION
                screen.fill(GOLD_DOOR_COLOR)
                img_win = font.render("YOU ESCAPED THE LOOP! YOU WIN!", True, BLACK)
                screen.blit(img_win, (250, 280))
                pygame.display.flip()
                time.sleep(3.0)
                pygame.quit()
                sys.exit()
            else:
                player_y = 120 # Bounce back

        elif player_rect.colliderect(sun_door):
            current_room = "SUN_ROOM"
            player_x = 650
        elif player_rect.colliderect(shadow_door):
            current_room = "SHADOW_ROOM"
            player_x = 100

    elif current_room == "SUN_ROOM":
        if player_x > 750:
            current_room = "MAIN_HALL"
            player_x = 110
        
        # Touch Chest to enter password
        if not has_key and player_rect.colliderect(chest_rect):
            print("\n--- THE IRON CHEST DEMANDS A CODE ---")
            guess = input("Look at your VS Code terminal and enter the 1-digit code: ")
            if guess == "7":
                print("SUCCESS! You grabbed the Sun Key!")
                has_key = True
            else:
                print("WRONG CODE! You got knocked back.")
                player_x = 400 # Bounce player away

    elif current_room == "SHADOW_ROOM":
        if player_x < 20:
            current_room = "MAIN_HALL"
            player_x = 670
            
        # Touch Glowing Object for Clue
        if player_rect.colliderect(clue_rect) and not discovered_code:
            discovered_code = True
            print("\n[CLUE DISCOVERED] You inspect the glowing stone. A number '7' is carved here!")

    # --- DRAW SCREEN ---
    screen.fill(BLACK)

    # Display HUD (Heads-up display) visible in all rooms
    img_energy = font.render(f"Temple Stability Energy: {energy}", True, RED if energy < 300 else TEXT_COLOR)
    screen.blit(img_energy, (20, 20))
    img_loop = font.render(f"Loop: #{loop_count}", True, TEXT_COLOR)
    screen.blit(img_loop, (680, 20))
    if has_key:
        img_key = font.render("[KEY ACQUIRED]", True, GOLD_DOOR_COLOR)
        screen.blit(img_key, (330, 20))

    # Room-specific visual drawing
    if current_room == "MAIN_HALL":
        pygame.draw.rect(screen, GOLD_DOOR_COLOR, gold_door)
        pygame.draw.rect(screen, SUN_DOOR_COLOR, sun_door)
        pygame.draw.rect(screen, SHADOW_DOOR_COLOR, shadow_door)
        screen.blit(font.render("MAIN HALL", True, TEXT_COLOR), (350, 100))
        if not has_key:
            screen.blit(font.render("The Gold Exit is locked tight.", True, TEXT_COLOR), (270, 520))

    elif current_room == "SUN_ROOM":
        screen.blit(font.render("SUN ROOM", True, SUN_DOOR_COLOR), (350, 100))
        if not has_key:
            pygame.draw.rect(screen, CHEST_COLOR, chest_rect)
            screen.blit(font.render("Touch the brown chest to attempt unlock", True, TEXT_COLOR), (150, 250))
        else:
            screen.blit(font.render("The chest lies open and broken.", True, TEXT_COLOR), (250, 300))

    elif current_room == "SHADOW_ROOM":
        screen.blit(font.render("SHADOW ROOM", True, SHADOW_DOOR_COLOR), (350, 100))
        if not discovered_code:
            pygame.draw.rect(screen, CLUE_COLOR, clue_rect)
            screen.blit(font.render("Touch the cyan anomaly to gather memories", True, TEXT_COLOR), (150, 250))
        else:
            screen.blit(font.render("The wall reads: THE ANSWER IS 7", True, CLUE_COLOR), (250, 300))

    # Draw Player
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

    pygame.display.flip()
    clock.tick(60)
