import pygame 

class BigBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()

        # size + appearance 
        self.image = pygame.Surface( (50, 30) )
        self.image.fill((250,224,51))

        # position
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

        # movement
        self.speed = 10 
        self.direction = direction 
    
    def update(self):
        # move bullet 
        self.rect.x += self.direction * self.speed 
        
        # remove bullet if it goes off screen 
        if (self.rect.right < 0 or self.rect.left > 800):
            self.kill() 



class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, size=10, color=(250,224,51)):
        # basic make it stuff 
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # physics 
        self.y = float(y)
        self.y_velocity = 0 
        self.gravity = 0.5 
        self.max_fall_speed = 10 

    def apply_physics(self):
        self.y_velocity += self.gravity 
        if self.y_velocity > self.max_fall_speed:
            self.y_velocity = self.max_fall_speed 

    def move(self, terrain):
        self.y += self.y_velocity 
        self.rect.y = int(self.y)

        # so powerup doesn't go through the floor 
        collided_blocks = pygame.sprite.spritecollide(self, terrain, False)
        for block in collided_blocks:
            if self.y_velocity > 0:
                self.rect.bottom = block.rect.top
                self.y_velocity = 0 
                self.y = self.rect.y

    def update(self, terrain):
        self.apply_physics()
        self.move(terrain)



class TerrainBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, size, row, col, level_map, color=(70, 120, 168), destructible=True):
        super().__init__()

        self.image = pygame.Surface((size, size))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)

        self.destructible = destructible 
        self.color = color 
        self.row = row 
        self.col = col 
        self.level_map = level_map 
        self.size = size  

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

        WHITE_BORDER = (255, 255, 255)
        RED_BORDER = (255, 60, 60)

        max_rows = len(self.level_map)
        max_cols = len(self.level_map[0])

        r = self.row 
        c = self.col 

        top = self.level_map[r-1][c] if r > 0 else "0"
        bottom = self.level_map[r+1][c] if r < max_rows - 1 else "0"
        left = self.level_map[r][c-1] if c > 0 else "0"
        right = self.level_map[r][c+1] if c < max_cols - 1 else "0"

        x = self.rect.x
        y = self.rect.y
        s = self.size 

        # TOP
        if top == "0":
            pygame.draw.line(
                surface, 
                WHITE_BORDER, 
                (x,y),
                (x+s, y), 
                3
            )
            pygame.draw.line(
                surface,
                RED_BORDER,
                (x,y+1),
                (x+s,y+1),
                1
            )
        if bottom == "0":
            pygame.draw.line(
                surface, 
                WHITE_BORDER, 
                (x, y + s - 1), 
                (x + s, y + s - 1), 
                3
            )
            pygame.draw.line(
                surface,
                RED_BORDER,
                (x, y+s-2),
                (x+s, y+s-2),
                1
            )
        if left == "0":
            pygame.draw.line(
                surface, 
                WHITE_BORDER, 
                (x, y), 
                (x, y + s), 
                3
            )
            pygame.draw.line(
                surface,
                RED_BORDER,
                (x+1, y),
                (x+1, y+s),
                1
            )
        if right == "0":
            pygame.draw.line(
                surface, 
                WHITE_BORDER, 
                (x+s-1, y), 
                (x + s - 1, y + s), 
                3
            )
            pygame.draw.line(
                surface,
                RED_BORDER,
                (x+s-2, y),
                (x+s-2, y+s),
                1
            )


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()

        # size + appearance 
        self.image = pygame.Surface( (8, 4) )
        self.image.fill((255,0,0))

        # position
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

        # movement
        self.speed = 10 
        self.direction = direction 

    def update(self):
        # move bullet 
        self.rect.x += self.direction * self.speed 
        
        # remove bullet if it goes off screen 
        if (self.rect.right < 0 or self.rect.left > 800):
            self.kill() 


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, sprite_sheet_path, bullet_count=50):
        super().__init__()

        self.frame_width = 23
        self.frame_height = 31
        self.scale = 0.8

        self.animations = self.load_sprite_sheet(sprite_sheet_path)
        
        self.idle_frames = self.animations[0][0:4]
        self.run_frames = self.animations[1]
        self.shoot_frames = self.animations[4] 
        
        self.animation_index = 0 
        self.animation_speed = 0.25
        self.facing_direction = 1 
        self.image = self.idle_frames[0]

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        self.width = self.rect.width
        self.height = self.rect.height 

        # store float positions for smoother physics 
        self.x = float(x)
        self.y = float(y)

        # movement 
        self.x_velocity = 0 
        self.y_velocity = 0 

        # physics 
        self.gravity = 0.4 
        self.jetpack_strength = -0.8
        self.max_fall_speed = 10 

        self.run_acceleration= 0.5 
        self.friction = 0.3 
        self.max_run_speed = 6

        # player direction 
        self.facing_direction = 1 

        # ground / bounds 
        self.ground_y = 550 
        self.screen_width = 800 

        # controls 
        self.controls = controls 

        # shooting 
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0 
        self.shoot_delay = 5 
        self.bullet_count = bullet_count 
        self.has_big_bullet = False 

    def load_sprite_sheet(self, sprite_sheet_path):
        sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        
        animations = [] 
        
        spacing_x = 25 #pixels
        spacing_y = 17 #pixels

        rows = sheet.get_height() // (self.frame_height + spacing_y)
        cols = sheet.get_width() // (self.frame_width + spacing_x)

        for row in range(rows):
            animation_row = [] 

            for col in range(cols):
                x = col * (self.frame_width + spacing_x)
                y = row * (self.frame_height + spacing_y)
                
                frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                frame.blit(
                    sheet,
                    (0,0),
                    (x, y, self.frame_width, self.frame_height)
                )

                scaled_frame = pygame.transform.scale(
                    frame,
                    (int(self.frame_width * self.scale), int(self.frame_height * self.scale))
                )

                animation_row.append(scaled_frame)
            
            animations.append(animation_row)
        
        return animations 

    def handle_input(self, keys):
        if keys[self.controls["left"]]:
            self.x_velocity -= self.run_acceleration 
            self.facing_direction = -1 

        if keys[self.controls["right"]]:
            self.x_velocity += self.run_acceleration 
            self.facing_direction = 1 

        if keys[self.controls["up"]]:
            self.y_velocity += self.jetpack_strength 

        if keys[self.controls["shoot"]] and self.shoot_cooldown == 0:
            bullet_y = self.rect.centery # what does this do?

            if self.has_big_bullet:
                if self.facing_direction == 1:
                    bullet_x = self.rect.right + 25 
                else:
                    bullet_x = self.rect.left - 25 

                bullet = BigBullet(bullet_x, bullet_y, self.facing_direction)
                self.bullets.add(bullet)
                self.has_big_bullet = False 
                self.shoot_cooldown = self.shoot_delay 


            elif self.bullet_count > 0:
                if self.facing_direction == 1: 
                    bullet_x = self.rect.right 
                else:
                    bullet_x = self.rect.left 

                bullet = Bullet(bullet_x, bullet_y, self.facing_direction)
                self.bullets.add(bullet)
                self.shoot_cooldown = self.shoot_delay 
                self.bullet_count -= 1 

    def apply_physics(self, keys):
        # friction when no horizontal input 
        if not keys[self.controls["left"]] and not keys[self.controls["right"]]:
            if self.x_velocity > 0:
                self.x_velocity -= self.friction
                if self.x_velocity < 0:
                    self.x_velocity = 0 
            elif self.x_velocity < 0:
                self.x_velocity += self.friction 
                if self.x_velocity > 0:
                    self.x_velocity = 0 

        # cap horizontal speed 
        if self.x_velocity > self.max_run_speed:
            self.x_velocity = self.max_run_speed 
        if self.x_velocity < -self.max_run_speed:
            self.x_velocity = -self.max_run_speed 

        # gravity 
        self.y_velocity += self.gravity 
        if self.y_velocity > self.max_fall_speed:
            self.y_velocity = self.max_fall_speed

    def move(self, terrain):
        # move horizontally and check terrain collision 
        self.x += self.x_velocity 
        self.rect.x = int(self.x)

        collided_blocks = pygame.sprite.spritecollide(self, terrain, False)
        for block in collided_blocks: 
            if self.x_velocity > 0:
                self.rect.right = block.rect.left 
            elif self.x_velocity < 0:
                self.rect.left = block.rect.right 
            self.x = self.rect.x 

        # move vertically and check terrain collision 
        self.y += self.y_velocity 
        self.rect.y = int(self.y) 

        collided_blocks = pygame.sprite.spritecollide(self, terrain, False)
        for block in collided_blocks:
            if self.y_velocity > 0:
                self.rect.bottom = block.rect.top
                self.y_velocity = 0 
            elif self.y_velocity < 0:
                self.rect.top = block.rect.bottom 
                self.y_velocity = 0 
            self.y = self.rect.y 

        # horizontal bounds 
        if self.x < 0: 
            self.x = 0 
            self.x_velocity = 0 
        if self.x > self.screen_width - self.width: 
            self.x = self.screen_width - self.width 
            self.x_velocity = 0

        self.rect.x = int(self.x)
        self.rect.y = int(self.y) 

    def update_animation(self, keys):
        moving = keys[self.controls["left"]] or keys[self.controls["right"]]
        shooting = keys[self.controls["shoot"]]

        if shooting:
            current_animation = self.shoot_frames
        elif moving:
            current_animation = self.run_frames
        else:
            current_animation = self.idle_frames
        
        self.animation_index += self.animation_speed 

        if self.animation_index >= len(current_animation):
            self.animation_index = 0 

        frame = current_animation[int(self.animation_index)]

        if self.facing_direction == -1:
            self.image = pygame.transform.flip(frame, True, False)
        else:
            self.image = frame 

        # if moving:
        #     self.animation_index += self.animation_speed
        #     if self.animation_index >= len(self.animations_right):
        #         self.animation_index = 0 
        # else:
        #     self.animation_index = 0 
        
        # if self.facing_direction == 1:
        #     self.image = self.animations_right[int(self.animation_index)]
        # else:
        #     self.image = self.animations_left[int(self.animation_index)]

    def update(self, keys, terrain):
        self.handle_input(keys)
        self.apply_physics(keys)
        self.move(terrain)
        self.update_animation(keys)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1 

        self.bullets.update() 

    def draw_bullets(self, surface):
        self.bullets.draw(surface) 
