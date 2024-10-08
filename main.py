import pygame
import csv
import constants
from character import Character
from weapon import Weapon
from items import Item
from world import World

pygame.init()
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption('The Labyrinth')
clock = pygame.time.Clock()
level = 1
screen_scroll = [0, 0]

moving_left = False
moving_right = False
moving_up = False
moving_down = False

font = pygame.font.Font('assets/fonts/AtariClassic.ttf', 20)

def scale_img(image, scale):
  w = image.get_width()
  h = image.get_height()
  return pygame.transform.scale(image, (w * scale, h * scale))

heart_empty = scale_img(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
heart_half = scale_img(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
heart_full = scale_img(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)

coin_images = []
for x in range(4):
  img = scale_img(pygame.image.load(f"assets/images/items/coin_f{x}.png").convert_alpha(), constants.ITEM_SCALE)
  coin_images.append(img)

red_potion = scale_img(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)

bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)

tile_list = []
for x in range(constants.TILE_TYPES):
  tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
  tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
  tile_list.append(tile_image)

mob_animations = []
mob_types = ['elf', 'imp', 'skeleton', 'goblin', 'muddy', 'tiny_zombie', 'big_demon']

animation_types = ["idle", "run"]

for mob in mob_types:
  animation_list = []
  for animation in animation_types:
    temp_list = []
    for i in range(4):
      img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
      img = scale_img(img, constants.SCALE)
      temp_list.append(img)
    animation_list.append(temp_list)
  mob_animations.append(animation_list)

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def draw_info():
  pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
  pygame.draw.line(screen, constants.ORANGE, (0, 50), (constants.SCREEN_WIDTH, 50))
  half_heart_drawn = False
  for i in range(5):
    if player.health >= ((i + 1) * 20):
      screen.blit(heart_full, (10 + i * 50, 0))
    elif (player.health % 20 > 0) and half_heart_drawn == False: 
      screen.blit(heart_half, (10 + i * 50, 0))
      half_heart_drawn = True
    else:
      screen.blit(heart_empty, (10 + i * 50, 0))
  draw_text(f"X{player.score}", font, constants.ORANGE, constants.SCREEN_WIDTH - 100, 15)

world_data = []
for row in range(constants.ROWS):
  r = [-1] * constants.COLS
  world_data.append(r)

with open(f"levels/level{level}_data.csv", newline="") as csvfile:
  reader = csv.reader(csvfile, delimiter = ",")
  for x, row in enumerate(reader):
    for y, tile in enumerate(row):
      world_data[x][y] = int(tile)

world = World()
world.process_data(world_data, tile_list)


class DamageText(pygame.sprite.Sprite):
  def __init__(self, x, y, damage, colour):
    pygame.sprite.Sprite.__init__(self)
    self.image = font.render(damage, True, colour)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.counter = 0

  def update(self):
    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]
    self.rect.y -= 1
    self.counter += 1
    if self.counter > 30:
      self.kill()

player = Character(400, 300, 100, mob_animations, 0)
enemy = Character(300, 300, 100, mob_animations, 1)
bow = Weapon(bow_image, arrow_image)

enemy_list = []
enemy_list.append(enemy)
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
item_group.add(score_coin)
potion = Item(200, 200, 1, [red_potion])
item_group.add(potion)
coin = Item(400, 400, 0, coin_images)
item_group.add(coin)

run = True
while run:
  clock.tick(constants.FPS)
  screen.fill(constants.BG)
  dx = 0
  dy = 0
  
  if moving_right == True:
    dx = constants.SPEED
  if moving_left == True:
    dx = -constants.SPEED
  if moving_up == True:
    dy = -constants.SPEED
  if moving_down == True:
    dy = constants.SPEED
  
  screen_scroll = player.move(dx, dy)  
  world.update(screen_scroll)
  for enemy in enemy_list:
    enemy.ai(screen_scroll)
    enemy.update()
  player.update()
  arrow = bow.update(player)
  if arrow:
    arrow_group.add(arrow)
  for arrow in arrow_group:
    damage, damage_pos = arrow.update(screen_scroll, enemy_list)
    if damage:
      damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
      damage_text_group.add(damage_text)
  damage_text_group.update()
  item_group.update(screen_scroll, player)
  
  world.draw(screen)
  for enemy in enemy_list:
    enemy.draw(screen)
  player.draw(screen)
  bow.draw(screen)
  for arrow in arrow_group:
    arrow.draw(screen)
  damage_text_group.draw(screen)
  item_group.draw(screen)
  draw_info()
  score_coin.draw(screen)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a:
        moving_left = True
      if event.key == pygame.K_d:
        moving_right = True
      if event.key == pygame.K_w:
        moving_up = True
      if event.key == pygame.K_s:
        moving_down = True
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_a:
        moving_left = False
      if event.key == pygame.K_d:
        moving_right = False
      if event.key == pygame.K_w:
        moving_up = False
      if event.key == pygame.K_s:
        moving_down = False
  
  pygame.display.update()

pygame.quit()