import pygame
from game_objects import Player, TerrainBlock, PowerUp, BigBullet
from map_generator import generate_cave_map, room_center 
import random 
pygame.init() 

# colors 
WHITE = (255, 255, 255)
BLACK = (0,0,0)
RED = (255, 0, 0)

gameDisplay = pygame.display.set_mode( (800,600) )
pygame.display.set_caption("Shooting Game")

# power up group initiation and spawn first power up
def spawn_powerUp(powerUp_group, rooms, block_size):
    room = random.choice(rooms)
    cx, cy = room_center(room)

    powerUp_size = 10 
    x = cx * block_size + (block_size - powerUp_size) // 2 
    y = cy * block_size + (block_size - powerUp_size) // 2 

    power = PowerUp(x, y)
    powerUp_group.add(power)

def main():
    # make map 
    block_size = 20 
    level_map, rooms = generate_cave_map()

    # determine player starting rooms 
    player1_room, player2_room = random.sample(rooms, 2)
    player1_cx, player1_cy = room_center(player1_room)
    player2_cx, player2_cy = room_center(player2_room)
    player1_x = player1_cx * block_size + (block_size - 10) // 2 # convert room_grid position to pixel position
    player1_y = player1_cy * block_size + (block_size - 10) // 2 
    player2_x = player2_cx * block_size + (block_size - 10) // 2 
    player2_y = player2_cy * block_size + (block_size - 10) // 2 

    # player controls 
    player1_controls = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "up": pygame.K_UP,
        "shoot": pygame.K_m
    }
    player2_controls = {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "up": pygame.K_w,
        "shoot": pygame.K_q
    }

    # create players 
    player1 = Player(player1_x, player1_y, BLACK, player1_controls, bullet_count=50)
    player2 = Player(player2_x, player2_y, RED, player2_controls, bullet_count=50)

    # player group 
    players = pygame.sprite.Group()
    players.add(player1, player2) 

    # terrain group, generate terrain blocks 
    terrain = pygame.sprite.Group()
    for row_index, row in enumerate(level_map):
        for col_index, cell in enumerate(row):
            if cell == "1":
                block_x = col_index * block_size 
                block_y = row_index * block_size 

                is_border = (
                    row_index == 0 or
                    row_index == len(level_map) - 1 or 
                    col_index == 0 or 
                    col_index == len(row) - 1 
                )

                if is_border:
                    block = TerrainBlock(block_x, block_y, block_size, color=(100, 100, 100),destructible=False)
                else:
                    block = TerrainBlock(block_x, block_y, block_size)
                
                terrain.add(block)

    # power up handling 
    powerUp = pygame.sprite.Group()
    spawn_powerUp(powerUp, rooms, block_size)

    # Game external handling 
    winner = None 
    game_over = False 
    start_screen = True 
    countdown_active = False 
    countdown_value = 3 
    countdown_start_time = 0 

    running = True 
    clock = pygame.Clock() 

    # font for game end screen 
    font_big = pygame.font.SysFont(None, 80)
    font_medium = pygame.font.SysFont(None, 40)
    font_small = pygame.font.SysFont(None, 28)

    # main game loop  
    while running:
        #FPS
        clock.tick(30)
        
        # add quit feature 
        for event in pygame.event.get(): 
            # 1st event handler (QUIT)
            if event.type == pygame.QUIT:
                running = False 

            if start_screen and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: 
                    start_screen = False 
                    countdown_active = True 
                    countdown_value = 3 
                    countdown_start_time = pygame.time.get_ticks()

        # check keys being held down 
        keys = pygame.key.get_pressed() 

        if countdown_active: 
            elapsed = (pygame.time.get_ticks() - countdown_start_time) // 1000

            if elapsed < 3: 
                countdown_value = 3 - elapsed 
            else:
                countdown_active = False 

        # gameplay updates only after countdown is done 
        if not start_screen and not countdown_active and not game_over:
            # update player sprite 
            player1.update(keys, terrain)
            player2.update(keys, terrain)
            powerUp.update(terrain)
            
            # detect bullet collision with terrain and differentiate between BigBullet and normal bullets
            for bullet in player1.bullets.copy():
                hit_blocks = pygame.sprite.spritecollide(bullet, terrain, False)
                if hit_blocks:
                    hit_indestructible = False 
                    for block in hit_blocks:
                        if block.destructible:
                            block.kill()
                        else:
                            hit_indestructible = True 
                    if isinstance(bullet, BigBullet):
                        if hit_indestructible:
                            bullet.kill() 
                    else:
                        bullet.kill()
                    
            for bullet in player2.bullets.copy():
                hit_blocks = pygame.sprite.spritecollide(bullet,terrain,False)
                if hit_blocks:
                    hit_indestructible = False
                    for block in hit_blocks:
                        if block.destructible:
                            block.kill()
                        else:
                            hit_indestructible = True 
                    if isinstance(bullet, BigBullet):
                        if hit_indestructible:
                            bullet.kill() 
                    else:
                        bullet.kill()
            
            # detect player collision with powerUp
            player1_pickups = pygame.sprite.spritecollide(player1, powerUp, True)
            if player1_pickups:
                player1.has_big_bullet = True 
                # apply effect to player1 and generate new powerUp
                spawn_powerUp(powerUp, rooms, block_size)
            player2_pickups = pygame.sprite.spritecollide(player2, powerUp, True)
            if player2_pickups:
                player2.has_big_bullet = True 
                # apply effects to player2 here 
                spawn_powerUp(powerUp, rooms, block_size)

            # bullet collision detection
            if pygame.sprite.spritecollide(player1, player2.bullets, True):
                winner = "Player 2"
                player1.kill()
                game_over = True 
            if pygame.sprite.spritecollide(player2, player1.bullets, True):
                winner = "Player 1"
                player2.kill()
                game_over = True 

        if start_screen: 
            gameDisplay.fill((255, 0, 0))
            
            title_text = font_big.render("Shooting Game", True, WHITE)
            line1 = font_medium.render("Player 1: Arrow keys to move, M to shoot", True, WHITE)
            line2 = font_medium.render("Player 2: WASD to move, Q to shoot", True, WHITE)
            line3 = font_small.render("Collect the yellow power up to fire a big bullet", True, WHITE)
            line4 = font_small.render("Press any key to start", True, WHITE)

            gameDisplay.blit(title_text, title_text.get_rect(center=(400,150)))
            gameDisplay.blit(line1, line1.get_rect(center=(400,250)))
            gameDisplay.blit(line2, line2.get_rect(center=(400,300)))
            gameDisplay.blit(line3, line3.get_rect(center=(400,360)))
            gameDisplay.blit(line4, line4.get_rect(center=(400,440)))

        elif countdown_active:
            gameDisplay.fill(WHITE)

            terrain.draw(gameDisplay)
            players.draw(gameDisplay)
            powerUp.draw(gameDisplay)

            countdown_text = font_big.render(str(countdown_value), True, BLACK)
            gameDisplay.blit(countdown_text, countdown_text.get_rect(center=(400,300)))
        
        # draw gameplay / game over 
        else:
            # draw everything 
            gameDisplay.fill(WHITE)

            # draw terrain
            terrain.draw(gameDisplay)

            # draw players 
            players.draw(gameDisplay)
            player1.draw_bullets(gameDisplay)
            player2.draw_bullets(gameDisplay)

            # draw powerUp 
            powerUp.draw(gameDisplay)
            
            if game_over and winner: 
                text = font_big.render(f"{winner} Wins!", True, WHITE)
                gameDisplay.blit(text, text.get_rect(center=(400,300)))

        pygame.display.flip()

    pygame.quit()

main()




