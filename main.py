import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 750
screen_height = 750

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#define game variables
tile_size = 50
game_over = 0


#load images
bg_img = pygame.image.load('images/pink1.webp')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))


class Player():
	def __init__(self, x, y):
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

	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False:
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
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


			#handle animation
			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0


			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1

			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy


		elif game_over == -1:
			self.image = self.dead_image
			

		#draw player onto screen
		screen.blit(self.image, self.rect)

		return game_over



class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load('images/block.png')
		grass_img = pygame.image.load('images/block.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
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
				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])

class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('images/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size//2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
class Spike(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('images/spike.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size//2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y




world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1], 
[1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 1, 1, 1, 0, 3, 0, 1, 3, 1, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1], 
[1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1], 
[1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1], 
[1, 0, 0, 1, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 1], 
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
]



player = Player(100, screen_height - 130)
lava_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
world = World(world_data)

run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))
	

	world.draw()
	lava_group.draw(screen)
	game_over = player.update(game_over)


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()