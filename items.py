import pygame

class Item(pygame.sprite.Sprite):
  def __init__(self, x, y, item_type, animation_list):
    pygame.sprite.Sprite.__init__(self)
    self.item_type = item_type
    self.animation_list = animation_list
    self.frame_index = 0
    self.update_time = pygame.time.get_ticks()
    self.image = self.animation_list[self.frame_index]
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
  
  def update(self):
    animation_cooldown = 150
    self.image = self.animation_list[self.frame_index]
    
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    if self.frame_index >= len(self.animation_list):
      self.frame_index = 0
