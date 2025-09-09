import pygame
import random
import asyncio

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Falling Debris with Power-ups")

# Load and scale images
background = pygame.image.load("./assets/images/background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

debris_img = pygame.image.load("./assets/images/e1.png")
debris_size = 50
debris_img = pygame.transform.scale(debris_img, (debris_size, debris_size))

player_img = pygame.image.load("./assets/images/mario.png")
player_size = 40
player_img = pygame.transform.scale(player_img, (player_size, player_size))

# font_large = pygame.font.SysFont("Arial", 60)
# font_medium = pygame.font.SysFont("Arial", 30)
# font_small = pygame.font.SysFont("Arial", 20)

font_large = pygame.font.Font(None, 60)
font_medium = pygame.font.Font(None, 30)
font_small = pygame.font.Font(None, 20)

clock = pygame.time.Clock()

# Menu screen -> State 1 
# Gameplay -> State 2
# End screen -> State 3
game_state = 1

# Power-up colors & sizes (simple rectangles)
POWERUP_SIZE = 30
POWERUP_TYPES = {
    "shield": (0, 0, 255),      # Blue
    "slow": (0, 255, 0),        # Green
    "double_score": (255, 215, 0),  # Gold/yellow
}

# Game variables
player = pygame.Rect(WIDTH // 2 - player_size // 2, HEIGHT - player_size - 10, player_size, player_size)
player_speed = 3

is_jumping = False
jump_velocity = 0
jump_strength = 15
gravity = 1
ground_y = HEIGHT - player_size - 10

debris_list = []
debris_speed = 5

powerup_list = []

score = 0

spawn_timer = random.randint(30, 60)
powerup_spawn_timer = random.randint(200, 400)

shield_active = False
slow_active = False
double_score_active = False
slow_timer = 0
double_score_timer = 0


def draw_menu():
    screen.blit(background, (0, 0))
    
    def draw_text_with_shadow(text, font, color, x, y):
        shadow_color = (0, 0, 0)
        screen.blit(font.render(text, True, shadow_color), (x+2, y+2))
        screen.blit(font.render(text, True, color), (x, y))
    
    title_text = "Falling Debris"
    instruction_text = "Press ENTER to Start"
    controls_text = "Arrow keys to move, Space to jump"

    title_x = WIDTH // 2 - font_large.size(title_text)[0] // 2
    title_y = HEIGHT // 3

    instr_x = WIDTH // 2 - font_medium.size(instruction_text)[0] // 2
    instr_y = HEIGHT // 2

    controls_x = WIDTH // 2 - font_medium.size(controls_text)[0] // 2
    controls_y = HEIGHT // 2 + 50

    draw_text_with_shadow(title_text, font_large, (255, 255, 255), title_x, title_y)
    draw_text_with_shadow(instruction_text, font_medium, (255, 255, 255), instr_x, instr_y)
    draw_text_with_shadow(controls_text, font_medium, (255, 255, 255), controls_x, controls_y)


def spawn_debris():
    x = random.randint(0, WIDTH - debris_size)
    y = 0
    moves_horizontally = random.choice([True, False])
    horizontal_speed = random.choice([-3, -2, -1, 1, 2, 3]) if moves_horizontally else 0
    debris = {
        "rect": pygame.Rect(x, y, debris_size, debris_size),
        "h_speed": horizontal_speed,
    }
    debris_list.append(debris)


def spawn_powerup():
    x = random.randint(0, WIDTH - POWERUP_SIZE)
    y = 0
    p_type = random.choice(list(POWERUP_TYPES.keys()))
    powerup = {
        "rect": pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE),
        "type": p_type,
        "v_speed": 3,
    }
    powerup_list.append(powerup)


def game_over_screen(final_score):
    def draw_text_with_shadow(text, font, color, x, y):
        shadow_color = (0, 0, 0)
        screen.blit(font.render(text, True, shadow_color), (x+2, y+2))
        screen.blit(font.render(text, True, color), (x, y))

    screen.fill((30, 30, 30))
    title = "GAME OVER"
    score_text = f"Final Score: {final_score}"
    instr = "Press ENTER to Restart or ESC to Quit"

    title_x = WIDTH // 2 - font_large.size(title)[0] // 2
    score_x = WIDTH // 2 - font_medium.size(score_text)[0] // 2
    instr_x = WIDTH // 2 - font_small.size(instr)[0] // 2

    screen.fill((30, 30, 30))
    draw_text_with_shadow(title, font_large, (255, 0, 0), title_x, HEIGHT//3)
    draw_text_with_shadow(score_text, font_medium, (255, 255, 255), score_x, HEIGHT//3 + 80)
    draw_text_with_shadow(instr, font_small, (200, 200, 200), instr_x, HEIGHT//3 + 140)


async def main():
    global game_state, shield_active, score, player_speed, jump_strength, gravity
    global is_jumping, jump_velocity
    global current_debris_speed, debris_speed 
    global spawn_timer, powerup_spawn_timer
    global slow_active, slow_timer
    global double_score_active, double_score_timer

    while True:
        if game_state == 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_state = 2
            draw_menu()

        elif game_state == 2:    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > 0:
                player.x -= player_speed
            if keys[pygame.K_RIGHT] and player.right < WIDTH:
                player.x += player_speed

            if not is_jumping and keys[pygame.K_SPACE]:
                is_jumping = True
                jump_velocity = -jump_strength

            if is_jumping:
                player.y += jump_velocity
                jump_velocity += gravity
                if player.y >= ground_y:
                    player.y = ground_y
                    is_jumping = False

            current_debris_speed = debris_speed * 0.5 if slow_active else debris_speed

            spawn_timer -= 1
            if spawn_timer <= 0:
                for _ in range(random.randint(1, 2)):  # fewer debris per spawn
                    spawn_debris()
                spawn_timer = random.randint(30, 60)  # longer delay between spawns

            powerup_spawn_timer -= 1
            if powerup_spawn_timer <= 0:
                spawn_powerup()
                powerup_spawn_timer = random.randint(200, 400)

            for d in debris_list[:]:
                d["rect"].y += current_debris_speed
                d["rect"].x += d["h_speed"]

                if d["rect"].left <= 0 or d["rect"].right >= WIDTH:
                    d["h_speed"] *= -1

                if d["rect"].top > HEIGHT:
                    debris_list.remove(d)
                    score += 2 if double_score_active else 1

                if d["rect"].colliderect(player):
                    if shield_active:
                        shield_active = False
                        debris_list.remove(d)
                    else:
                        game_state = 3  # Game over

            for p in powerup_list[:]:
                p["rect"].y += p["v_speed"]
                if p["rect"].top > HEIGHT:
                    powerup_list.remove(p)
                elif p["rect"].colliderect(player):
                    p_type = p["type"]
                    if p_type == "shield":
                        shield_active = True
                    elif p_type == "slow":
                        slow_active = True
                        slow_timer = 5 * 60
                    elif p_type == "double_score":
                        double_score_active = True
                        double_score_timer = 10 * 60

                    powerup_list.remove(p)

            if slow_active:
                slow_timer -= 1
                if slow_timer <= 0:
                    slow_active = False

            if double_score_active:
                double_score_timer -= 1
                if double_score_timer <= 0:
                    double_score_active = False

            screen.blit(background, (0, 0))
            screen.blit(player_img, (player.x, player.y))
            for d in debris_list:
                screen.blit(debris_img, (d["rect"].x, d["rect"].y))

            for p in powerup_list:
                color = POWERUP_TYPES[p["type"]]
                pygame.draw.rect(screen, color, p["rect"])

            score_text = font_medium.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            hud_y = 50
            if shield_active:
                shield_text = font_small.render("Shield: ON", True, (0, 0, 255))
                screen.blit(shield_text, (10, hud_y))
                hud_y += 25
            if slow_active:
                slow_text = font_small.render(f"Slow Down: {slow_timer//60 + 1}s", True, (0, 255, 0))
                screen.blit(slow_text, (10, hud_y))
                hud_y += 25
            if double_score_active:
                ds_text = font_small.render(f"Double Score: {double_score_timer//60 + 1}s", True, (255, 215, 0))
                screen.blit(ds_text, (10, hud_y))

        elif game_state == 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:

                        debris_list.clear()
                        powerup_list.clear()
                        score = 0
                        shield_active = False
                        slow_active = False
                        double_score_active = False
                        slow_timer = 0
                        double_score_timer = 0
                        player_speed = 3
                        is_jumping = False
                        jump_velocity = 0
                        jump_strength = 15
                        gravity = 1
                        debris_speed = 5
                        player.x = WIDTH // 2 - player_size // 2
                        player.y = HEIGHT - player_size - 10

                        game_state = 1          # Restart game
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
            game_over_screen(score)


        clock.tick(60)
        pygame.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())
