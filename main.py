import pygame
import random
import sys
import os
import asyncio

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.5
FLAP_STRENGTH = -8
PIPE_SPEED = 3
PIPE_FREQUENCY = 1500  # milliseconds
GAP_HEIGHT = 150
FLOOR_HEIGHT = 100
FLOOR_SPEED = 3

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Load or create assets
def create_bird_surface():
    bird_surface = pygame.Surface((34, 24), pygame.SRCALPHA)
    # Draw a simple bird shape
    pygame.draw.ellipse(bird_surface, YELLOW, (0, 0, 34, 24))
    pygame.draw.ellipse(bird_surface, (255, 165, 0), (25, 8, 10, 8))  # Orange beak
    pygame.draw.circle(bird_surface, (0, 0, 0), (8, 8), 4)  # Eye
    return bird_surface

bird_surface = create_bird_surface()
bird_rect = bird_surface.get_rect(center=(100, HEIGHT // 2))

# Game variables
bird_movement = 0
score = 0
high_score = 0
game_active = False
pipe_list = []
last_pipe = pygame.time.get_ticks()
floor_x_pos = 0

# Font
game_font = pygame.font.SysFont("Arial", 40)

class Pipe:
    def __init__(self, x):
        self.gap_pos = random.randint(200, HEIGHT - GAP_HEIGHT - FLOOR_HEIGHT - 100)
        self.x = x
        self.passed = False
        
        # Create pipe rectangles
        self.top_pipe = pygame.Rect(x, 0, 60, self.gap_pos)
        self.bottom_pipe = pygame.Rect(x, self.gap_pos + GAP_HEIGHT, 60, HEIGHT)
        
    def update(self):
        self.x -= PIPE_SPEED
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x
        
    def draw(self, surface):
        # Top pipe (upside down)
        pygame.draw.rect(surface, GREEN, self.top_pipe)
        # Add pipe cap for top pipe
        pygame.draw.rect(surface, (0, 100, 0), (self.x - 5, self.gap_pos - 20, 70, 20))
        
        # Bottom pipe
        pygame.draw.rect(surface, GREEN, self.bottom_pipe)
        # Add pipe cap for bottom pipe
        pygame.draw.rect(surface, (0, 100, 0), (self.x - 5, self.gap_pos + GAP_HEIGHT, 70, 20))
        
    def check_collision(self, bird_rect):
        return self.top_pipe.colliderect(bird_rect) or self.bottom_pipe.colliderect(bird_rect)

    
floor_surface = pygame.Surface((WIDTH, FLOOR_HEIGHT))
floor_surface.fill((222, 184, 135))
def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, HEIGHT - FLOOR_HEIGHT))
    screen.blit(floor_surface, (floor_x_pos + WIDTH, HEIGHT - FLOOR_HEIGHT))
    
    # Add some details to the floor
    for i in range(0, WIDTH, 30):
        x_pos = (i + floor_x_pos) % (WIDTH * 2) - 30
        if 0 <= x_pos < WIDTH:
            pygame.draw.rect(screen, (200, 164, 115), (x_pos, HEIGHT - FLOOR_HEIGHT + 20, 20, 5))
def display_score(game_state):
    if game_state:
        score_surface = game_font.render(f'Score: {score}', True, WHITE)
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)
    else:
        # Score
        score_surface = game_font.render(f'Score: {score}', True, WHITE)
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)
        
        # High score
        high_score_surface = game_font.render(f'High Score: {high_score}', True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(WIDTH // 2, 100))
        screen.blit(high_score_surface, high_score_rect)
        
        # Game over
        game_over_surface = game_font.render('GAME OVER', True, (255, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=(WIDTH // 2, 150))
        screen.blit(game_over_surface, game_over_rect)
        
        # Restart instruction
        restart_surface = game_font.render('Press SPACE to Restart', True, WHITE)
        restart_rect = restart_surface.get_rect(center=(WIDTH // 2, 200))
        screen.blit(restart_surface, restart_rect)

def check_collision(pipes):
    # Check if bird hits the floor or ceiling
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT - FLOOR_HEIGHT:
        return True
    
    # Check if bird hits any pipes
    for pipe in pipes:
        if pipe.check_collision(bird_rect):
            return True
    
    return False

def rotate_bird(bird):
    # Rotate the bird based on its movement
    rotation = min(max(-90, bird_movement * -3), 30)
    return pygame.transform.rotate(bird, rotation)

def reset_game():
    global bird_rect, bird_movement, pipe_list, score, game_active
    bird_rect.center = (100, HEIGHT // 2)
    bird_movement = 0
    pipe_list = []
    score = 0
    game_active = True

def run_game():
    global bird_rect, bird_movement, pipe_list, score, high_score, game_active, last_pipe, floor_x_pos
    
    # Reset game variables for web
    bird_rect = bird_surface.get_rect(center=(100, HEIGHT // 2))
    bird_movement = 0
    score = 0
    high_score = 0
    game_active = False
    pipe_list = []
    last_pipe = pygame.time.get_ticks()
    floor_x_pos = 0
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        bird_movement = FLAP_STRENGTH
                    else:
                        reset_game()
            
            # Handle touch events for mobile
            if event.type == pygame.FINGERDOWN:
                if game_active:
                    bird_movement = FLAP_STRENGTH
                else:
                    reset_game()
        
        # Draw background
        screen.fill(SKY_BLUE)
        
        # Draw clouds
        for i in range(0, WIDTH * 3, WIDTH):
            offset = (pygame.time.get_ticks() // 50) % (WIDTH * 3)
            x_pos = i - offset
            if -100 <= x_pos <= WIDTH:
                pygame.draw.ellipse(screen, WHITE, (x_pos, 50, 100, 50))
                pygame.draw.ellipse(screen, WHITE, (x_pos - 30, 70, 70, 40))
                pygame.draw.ellipse(screen, WHITE, (x_pos + 30, 70, 70, 40))
        
        if game_active:
            # Bird movement
            bird_movement += GRAVITY
            bird_rect.centery += bird_movement
            rotated_bird = rotate_bird(bird_surface)
            screen.blit(rotated_bird, bird_rect)
            
            # Pipes
            current_time = pygame.time.get_ticks()
            if current_time - last_pipe > PIPE_FREQUENCY:
                pipe_list.append(Pipe(WIDTH + 100))
                last_pipe = current_time
            
            # Update pipes
            pipes_to_remove = []
            for pipe in pipe_list:
                pipe.update()
                pipe.draw(screen)
                
                # Check for points
                if pipe.x + 60 < bird_rect.left and not pipe.passed:
                    score += 1
                    pipe.passed = True
                
                # Remove pipes that are off screen
                if pipe.x < -100:
                    pipes_to_remove.append(pipe)
            
            for pipe in pipes_to_remove:
                pipe_list.remove(pipe)
            
            # Check for collisions
            if check_collision(pipe_list):
                game_active = False
                if score > high_score:
                    high_score = score
        
        # Draw floor
        floor_x_pos -= FLOOR_SPEED
        if floor_x_pos <= -WIDTH:
            floor_x_pos = 0
        draw_floor()
        
        # Display score
        display_score(game_active)
        
        # Update the display
        pygame.display.update()
        clock.tick(FPS)

# This allows the module to be imported for web usage
if __name__ == "__main__":
    run_game()