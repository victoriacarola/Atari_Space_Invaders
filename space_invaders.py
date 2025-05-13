import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen settings (scaled to mimic 224x256 arcade resolution)
SCALE = 3
SCREEN_WIDTH = 224 * SCALE
SCREEN_HEIGHT = 256 * SCALE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# Colors (mimicking original Space Invaders palette)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Original player sprite (11x8 pixels scaled)
        self.image = pygame.Surface((11 * SCALE, 8 * SCALE), pygame.SRCALPHA)
        pixel_data = [
            "0010000",
            "0111000",
            "1111100",
            "1111100",
            "1111100",
            "0111000",
            "0010000",
            "0010000"
        ]
        for y, row in enumerate(pixel_data):
            for x, pixel in enumerate(row):
                if pixel == "1":
                    pygame.draw.rect(self.image, WHITE, (x * SCALE, y * SCALE, SCALE, SCALE))
        self.rect = self.image.get_rect()
        self.rect.bottom = SCREEN_HEIGHT - 30 * SCALE
        self.rect.centerx = SCREEN_WIDTH // 2
        self.speed = 2 * SCALE
        self.lives = 3
        self.score = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

# Pixel data for alien sprites
LARGE_ALIEN_FRAMES = [
    # Frame 1
    [
        "0010101000101010",
        "0101010101010101",
        "1011111111111101",
        "1111111111111111",
        "1111111111111111",
        "0011111111111000",
        "0011100001111000",
        "0011100001111000",
    ],
    # Frame 2
    [
        "0010101000101010",
        "0101010101010101",
        "1011111111111101",
        "1111111111111111",
        "1111111111111111",
        "0011111111111000",
        "0000011111100000",
        "0000011111100000",
    ],
]

MEDIUM_ALIEN_FRAMES = [
    # Frame 1
    [
        "0000111111110000",
        "0111111111111100",
        "1111111111111110",
        "1111111111111110",
        "0000001111000000",
        "0000111111110000",
        "0011111111111100",
        "0011100000111000",
    ],
    # Frame 2
    [
        "0000111111110000",
        "0111111111111100",
        "1111111111111110",
        "1111111111111110",
        "0000001111000000",
        "0000111111110000",
        "0011111111111100",
        "0000011111100000",
    ],
]

SMALL_ALIEN_FRAMES = [
    # Frame 1
    [
        "0000001111000000",
        "0000111111110000",
        "0011111111111100",
        "0111111111111110",
        "1111100000111111",
        "1111100000111111",
        "0111111111111110",
        "0000111111110000",
    ],
    # Frame 2
    [
        "0000001111000000",
        "0000111111110000",
        "0011111111111100",
        "0111111111111110",
        "1111100000111111",
        "1111100000111111",
        "0111111111111110",
        "0000011111100000",
    ],
]

def create_alien_sprite(pixel_data, scale, color):
    """Create a Pygame surface from pixel data."""
    height = len(pixel_data)
    width = len(pixel_data[0])
    surface = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
    for y, row in enumerate(pixel_data):
        for x, pixel in enumerate(row):
            if pixel == "1":
                pygame.draw.rect(surface, color, (x * scale, y * scale, scale, scale))
    return surface

# Pre-create sprite surfaces with original colors
ALIEN_SPRITES = {
    0: [create_alien_sprite(frame, SCALE, GREEN) for frame in LARGE_ALIEN_FRAMES],  # Large aliens
    1: [create_alien_sprite(frame, SCALE, CYAN) for frame in MEDIUM_ALIEN_FRAMES],  # Medium aliens
    2: [create_alien_sprite(frame, SCALE, MAGENTA) for frame in SMALL_ALIEN_FRAMES],  # Small aliens
}

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, type_id):
        super().__init__()
        self.type_id = type_id  # 0=large, 1=medium, 2=small
        self.frames = ALIEN_SPRITES[type_id]
        self.frame = 0
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.points = [30, 20, 10][type_id]
        self.moved = False

    def update(self):
        if self.moved:
            self.frame = (self.frame + 1) % 2
            self.image = self.frames[self.frame]
            self.moved = False

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((2 * SCALE, 8 * SCALE))
        self.image.fill(WHITE if direction == -1 else GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 5 * SCALE * direction  # Up (-1) or down (+1)

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Pixel data for bunker sprite (24x18 pixels, based on original Space Invaders)
BUNKER_PIXEL_DATA = [
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111111111111111111111",
    "111111100000000000111111",
    "111111100000000000111111",
    "111111100000000000111111",
    "111111100000000000111111",
    "111111100000000000111111",
    "111111100000000000111111",
]

class Bunker(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create bunker sprite from pixel data
        self.image = pygame.Surface((24 * SCALE, 18 * SCALE), pygame.SRCALPHA)
        for y_idx, row in enumerate(BUNKER_PIXEL_DATA):
            for x_idx, pixel in enumerate(row):
                if pixel == "1":
                    pygame.draw.rect(self.image, GREEN, (x_idx * SCALE, y_idx * SCALE, SCALE, SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def hit(self, bullet_rect):
        # Use PixelArray in a controlled scope
        pixels = pygame.PixelArray(self.image)
        for dy in range(-4, 5):  # Increased range to -4 to 4 for triple damage
            for dx in range(-4, 5):
                px = (bullet_rect.centerx - self.rect.x) // SCALE + dx
                py = (bullet_rect.centery - self.rect.y) // SCALE + dy
                if 0 <= px < 24 and 0 <= py < 18:
                    pixels[px, py] = (0, 0, 0, 0)  # Transparent black
        del pixels  # Unlock the surface

# UFO class
class UFO(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32 * SCALE, 8 * SCALE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.y = 20 * SCALE
        self.rect.x = -self.rect.width if random.choice([True, False]) else SCREEN_WIDTH
        self.speed = 2 * SCALE * (-1 if self.rect.x < 0 else 1)
        self.points = random.choice([50, 100, 150, 300])

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# Game setup
player = Player()
player_group = pygame.sprite.Group(player)
aliens = pygame.sprite.Group()
bullets = pygame.sprite.Group()
bunkers = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()

# Create aliens (5 rows x 11 columns)
for row in range(5):
    for col in range(11):
        type_id = 2 if row < 2 else 1 if row < 4 else 0
        x = (40 + col * 16) * SCALE
        y = (40 + row * 16) * SCALE
        alien = Alien(x, y, type_id)
        aliens.add(alien)

# Create bunkers
for i in range(4):
    x = (30 + i * 50) * SCALE
    y = 180 * SCALE
    bunkers.add(Bunker(x, y))

# Game variables
alien_direction = 1
alien_move_timer = 0
alien_speed = 0.5 * SCALE  # Initial speed
ufo_timer = 0
font_size = 18 * SCALE  # Define a font size based on the scale
font = pygame.font.Font(None, font_size)
running = True
game_over = False

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                if not any(b.speed < 0 for b in bullets):  # One player bullet at a time
                    bullet = Bullet(player.rect.centerx, player.rect.top, -1)
                    bullets.add(bullet)
            if event.key == pygame.K_r and game_over:
                # Reset game (simplified)
                player.lives = 3
                player.score = 0
                aliens.empty()
                bullets.empty()
                ufo_group.empty()
                for row in range(5):
                    for col in range(11):
                        type_id = 2 if row < 2 else 1 if row < 4 else 0
                        x = (40 + col * 16) * SCALE
                        y = (40 + row * 16) * SCALE
                        aliens.add(Alien(x, y, type_id))
                game_over = False

    if not game_over:
        # Update
        player_group.update()
        bullets.update()
        ufo_group.update()

        # Alien movement
        alien_move_timer += 1
        speed_factor = 0.5 + (55 - len(aliens)) / 55 * 2
        if alien_move_timer >= 30 / speed_factor:
            min_x = min(a.rect.x for a in aliens)
            max_x = max(a.rect.right for a in aliens)
            if max_x >= SCREEN_WIDTH - 8 * SCALE and alien_direction == 1:
                alien_direction = -1
                for alien in aliens:
                    alien.rect.y += 8 * SCALE
                    alien.moved = True  # Flag movement
            elif min_x <= 8 * SCALE and alien_direction == -1:
                alien_direction = 1
                for alien in aliens:
                    alien.rect.y += 8 * SCALE
                    alien.moved = True
            else:
                for alien in aliens:
                    alien.rect.x += alien_direction * 8 * SCALE
                    alien.moved = True
            alien_move_timer = 0

        # Update aliens to animate
        aliens.update()

        # Alien shooting
        if random.random() < 0.01 and len(aliens) > 0:
            shooter = random.choice([a for a in aliens])
            bullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, 1)
            bullets.add(bullet)

        # UFO spawning
        ufo_timer += 1
        if ufo_timer > 600 and not ufo_group and random.random() < 0.01:
            ufo_group.add(UFO())
            ufo_timer = 0

        # Collisions
        for bullet in bullets:
            if bullet.speed < 0:  # Player bullet
                hit_aliens = pygame.sprite.spritecollide(bullet, aliens, True)
                if hit_aliens:
                    player.score += hit_aliens[0].points
                    bullet.kill()
                hit_ufo = pygame.sprite.spritecollide(bullet, ufo_group, True)
                if hit_ufo:
                    player.score += hit_ufo[0].points
                    bullet.kill()
                for bunker in pygame.sprite.spritecollide(bullet, bunkers, False):
                    bunker.hit(bullet.rect)
                    bullet.kill()
            else:  # Alien bullet
                if pygame.sprite.spritecollide(bullet, player_group, False):
                    player.lives -= 1
                    bullet.kill()
                    if player.lives <= 0:
                        game_over = True
                for bunker in pygame.sprite.spritecollide(bullet, bunkers, False):
                    bunker.hit(bullet.rect)
                    bullet.kill()

        # Check alien invasion
        if any(a.rect.bottom >= player.rect.top for a in aliens):
            player.lives = 0
            game_over = True

        # Extra life
        if player.score // 1500 > (player.score - 10) // 1500:
            player.lives += 1

    # Draw
    screen.fill(BLACK)
    player_group.draw(screen)
    aliens.draw(screen)
    bullets.draw(screen)
    bunkers.draw(screen)
    ufo_group.draw(screen)

    # HUD
    score_text = font.render(f"Score: {player.score}", True, WHITE)
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    screen.blit(score_text, (10 * SCALE, 10 * SCALE))
    screen.blit(lives_text, (SCREEN_WIDTH - 60 * SCALE, 10 * SCALE))
    if game_over:
        game_over_text = font.render("Game Over - Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100 * SCALE, SCREEN_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()