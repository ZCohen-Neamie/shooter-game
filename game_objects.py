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
    def __init__(self, x, y, size, color=(100, 100, 100), destructible=True):
        super().__init__()

        self.image = pygame.Surface((size, size))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)

        self.destructible = destructible  


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
    def __init__(self, x, y, color, controls, bullet_count=50):
        super().__init__()

        self.width = 10 
        self.height = 10 
        self.color = color 

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # store float positions for smoother physics 
        self.x = float(x)
        self.y = float(y)

        # movement 
        self.x_velocity = 0 
        self.y_velocity = 0 

        # physics 
        self.gravity = 0.5 
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
        self.bullet_color = color 
        self.has_big_bullet = False 

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

    def update(self, keys, terrain):
        self.handle_input(keys)
        self.apply_physics(keys)
        self.move(terrain)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1 

        self.bullets.update() 

    def draw_bullets(self, surface):
        self.bullets.draw(surface) 
