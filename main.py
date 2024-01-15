import pygame
from pygame.locals import *
from pygame import mixer
from level_data import level1_data, level2_data, level3_data, level4_data 

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# Initialize clock and frames per second
clock = pygame.time.Clock()
fps = 60

# Set up screen dimensions
screen_width = 750
screen_height = 750

# Create the game screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Candy Girl')

#define game variables
tile_size = 50
game_over = 0
main_menu = True
max_levels = 4
current_level = 1
score = 0
lives = 3
game_over_played = False

# Set up font and color
font = pygame.font.SysFont('Roboto', 30)
white = (255,255,255)

#load images
bg_img = pygame.image.load('images/pink1.webp')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))
reset_img = pygame.image.load('images/reset.png')
reset_img = pygame.transform.scale(reset_img, (screen_width//5, screen_height//14))
start_img = pygame.image.load('images/start.png')
start_img = pygame.transform.scale(start_img, (screen_width//5, screen_height//14))
menu_img = pygame.image.load('images/menu.png')
menu_img = pygame.transform.scale(menu_img, (screen_width//5, screen_height//14))
exit_img = pygame.image.load('images/exit.png')
exit_img = pygame.transform.scale(exit_img, (screen_width//5, screen_height//14))

game_over_img = pygame.image.load('images/game_over.png')  
game_over_img = pygame.transform.scale(game_over_img, (screen_width//3 , screen_height//3))
game_over_rect = game_over_img.get_rect(center=(screen_width // 2, screen_height // 2))

died_img = pygame.image.load('images/died.png')  
died_img = pygame.transform.scale(died_img, (screen_width//3 , screen_height//3))
died_rect = died_img.get_rect(center=(screen_width // 2, screen_height // 2))

win_img = pygame.image.load('images/win.png')  
win_img = pygame.transform.scale(win_img, (screen_width//3 , screen_height//3))
win_rect = win_img.get_rect(center=(screen_width // 2, screen_height // 2))

#sounds
pygame.mixer.music.load('images/bg_sound.wav')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
die_sound = pygame.mixer.Sound('images/died_sound.wav')
gover_sound = pygame.mixer.Sound('images/game_over_sound.wav')
gover_sound.set_volume(0.8)
jump = pygame.mixer.Sound('images/jump.wav')
jump.set_volume(0.8)

# Function to draw text on the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

"""
    Class representing the player  in the game.

    Attributes:
    - x, y: Current position of the player.
    - images_right, images_left: Lists of images for player animation.
    - index, counter: Variables for animation control.
    - image: Current image of the player.
    - rect: Rectangular area occupied by the player.
    - width, height: Dimensions of the player's image.
    - vel_y: Vertical velocity of the player.
    - jumped: Flag indicating if the player has jumped.
    - direction: Direction the player is facing (1 for right, -1 for left).
    - high: Flag indicating if the player is in the air.

"""
class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over, lives):
        """
        Update the player's position, animation, and check for collisions.

        Parameters:
        - game_over: Game over state (0 for playing, -1 for loss, 1 for win).
        - lives: Number of lives remaining.

        Returns:
        - game_over: Updated game over state.
        - lives: Updated number of lives.
        """
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            # Get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jumped == False and self.high == False:
                self.vel_y = -15
                self.jumped = True
                jump.play()
            if key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Handle animation
            if self.counter > walk_cooldown:
                self.counter = 0    
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Check for collision
            self.high = True
            for tile in world.tile_list:
                # Check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # Check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # Check if below the ground 
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Check if above the ground 
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.high = False

            # Check for collision with lava and spikes
            if pygame.sprite.spritecollide(self, lava_group, False) or pygame.sprite.spritecollide(self, spike_group, False):
                game_over = -1
                lives -= 1
                die_sound.play()
                
            # Check for collision with portal
            if pygame.sprite.spritecollide(self, portal_group, False):
                game_over = 1

            # Update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
             self.image = self.dead_image

        # Draw player onto screen
        screen.blit(self.image, self.rect)
        return game_over, lives
    
    def reset(self, x, y):
        """
        Reset the player to the initial state.

        Parameters:
        - x, y: Initial position of the player.
        """
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'images/girl{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 50))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('images/dead.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.high = True

	
class Button():
	"""
    Class representing a clickable button in the game.

    Attributes:
    - x, y: Position of the button.
    - image: Image of the button.
    - rect: Rectangular area occupied by the button.
    - clicked: Flag indicating if the button has been clicked.
    """
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False
	def draw(self):
		"""
        Draw the button on the screen and check for mouse interaction.

        Returns:
        - action: True if the button is clicked, False otherwise.
        """
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, self.rect)

		return action

class World():
	"""
    Class representing the game world with tiles and game elements.

    Attributes:
    - tile_list: List of tiles in the world.
    """
	def __init__(self, data):
		"""
        Initialize the world based on the provided level data.

        Parameters:
        - data: 2D list representing the layout of tiles in the level.
        """
		self.tile_list = []

		#load images
		block_img = pygame.image.load('images/block.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(block_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					lava = Lava(col_count*tile_size, row_count*tile_size+(tile_size//2))
					lava_group.add(lava)
				if tile == 3:
					spike = Spike(col_count*tile_size, row_count*tile_size+(tile_size//2))
					spike_group.add(spike)
				if tile == 4:
					portal = Portal(col_count*tile_size, row_count*tile_size-(tile_size//2))
					portal_group.add(portal)
				if tile == 5:
					candy = Candy(col_count*tile_size + (tile_size//2), row_count*tile_size+(tile_size//2))
					candy_group.add(candy)
				col_count += 1
			row_count += 1

	def draw(self):
		"""Draw the tiles in the world on the screen."""
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])

class Lava(pygame.sprite.Sprite):
    """
    Represents a lava sprite in the game.

    Attributes:
    - x, y: Initial position of the lava sprite.
    - image: Surface representing the lava sprite's image.
    - rect: Rectangular area occupied by the lava sprite.
    """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('images/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Spike(pygame.sprite.Sprite):
    """
    Represents a spike sprite in the game.

    Attributes:
    - x, y: Initial position of the spike sprite.
    - image: Surface representing the spike sprite's image.
    - rect: Rectangular area occupied by the spike sprite.
    """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('images/spike.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Portal(pygame.sprite.Sprite):
    """
    Represents a portal sprite in the game.

    Attributes:
    - x, y: Initial position of the portal sprite.
    - image: Surface representing the portal sprite's image.
    - rect: Rectangular area occupied by the portal sprite.
    """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('images/portal.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Candy(pygame.sprite.Sprite):
	"""
    Represents a candy sprite in the game.

    Attributes:
    - x, y: Initial position of the candy sprite.
    - image: Surface representing the candy sprite's image.
    - rect: Rectangular area occupied by the candy sprite.
    """
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('images/candy.png')
		self.image = pygame.transform.scale(img, (tile_size//2, tile_size//2))
		self.rect = self.image.get_rect()
		self.rect.center = (x,y)

player = Player(100, screen_height - 130)
lava_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
candy_group = pygame.sprite.Group()

score_candy = Candy(tile_size // 2, tile_size // 2)
candy_group.add(score_candy)

world = world_data = globals()[f'level{current_level}_data']
world = World(world_data)

# buttons
reset_btn = Button(screen_width//5+150, screen_height//5+400, reset_img)
start_btn = Button(screen_width // 5+150, screen_height //5 +200, start_img)
exit_button = Button(screen_width // 5 + 150, screen_height // 5 +300, exit_img)
menu_btn = Button(screen_width//5+150, screen_height//5+400, menu_img)

# Main game loop
run = True
while run:
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    
    # Main menu handling
    if main_menu:
        if exit_button.draw():
            run = False
        if start_btn.draw():
            main_menu = False
    else:
        world.draw()
        if lives > 0:
            if game_over == 0:
                if pygame.sprite.spritecollide(player, candy_group, True):
                    score += 1
                draw_text('X ' + str(score), font, white, tile_size - 10, 10)
            lava_group.draw(screen)
            spike_group.draw(screen)
            portal_group.draw(screen)
            candy_group.draw(screen)
            game_over, lives = player.update(game_over, lives)

            if game_over == -1:
                died_rect.center = (screen_width // 2, screen_height // 2)
                screen.blit(died_img, died_rect)
                draw_text('Lives left: ' + str(lives), font, white, tile_size + 270, 520)

                if reset_btn.draw():
                    player.reset(100, screen_height - 130)
                    game_over = 0
                    score_candy = Candy(tile_size // 2, tile_size // 2)
                    candy_group.add(score_candy)


            if game_over == 1:
                current_level += 1
                if current_level <= max_levels:
                    lava_group.empty()
                    spike_group.empty()
                    portal_group.empty()
                    candy_group.empty()

                    world_data = globals()[f'level{current_level}_data']
                    world = World(world_data)
                    player.reset(100, screen_height - 130)
                    game_over = 0
                    score_candy = Candy(tile_size // 2, tile_size // 2)
                    candy_group.add(score_candy)
                else:
                    win_rect.center = (screen_width // 2, screen_height // 2)
                    screen.blit(win_img, win_rect)
                    draw_text('Your score: ' + str(score), font, white, tile_size + 270, 520)
                    if menu_btn.draw():
                        current_level = 1
                        lava_group.empty()
                        spike_group.empty()
                        portal_group.empty()
                        candy_group.empty()
                        world_data = globals()[f'level{current_level}_data']
                        world = World(world_data)
                        player.reset(100, screen_height - 130)
                        game_over = 0
                        score = 0
                        lives = 3
                        main_menu = True

        if lives <= 0:
            game_over_rect.center = (screen_width // 2, screen_height // 2)
            screen.blit(game_over_img, game_over_rect)

            if not game_over_played:
                    gover_sound.play()
                    game_over_played = True
            if menu_btn.draw():
                current_level = 1
                lava_group.empty()
                spike_group.empty()
                portal_group.empty()
                candy_group.empty()
                world_data = globals()[f'level{current_level}_data']
                world = World(world_data)
                player.reset(100, screen_height - 130)
                game_over = 0
                score = 0
                lives = 3
                main_menu = True
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()



