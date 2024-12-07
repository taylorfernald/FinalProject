import pygame as pg

class UIElement(pg.sprite.Sprite):
    """For button-like objects"""
    def __init__(self, x, y, w, h, font):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image = pg.Surface((self.w, self.h)) #How big the "image" is
        self.rect = pg.Rect(self.x, self.y, self.w, self.h) #The bounding box within the window
        self.color = (150, 150, 150)
    
    def add_text(self, font, text, color, dx = 0, dy = 0):
        self.image.fill(self.color)
        """Adds a text to the screen"""
        self.text = font.render(text, True, color)
        if dx or dy:
            self.text_rect = (dx, dy, self.rect.width, self.rect.height)
        else:
            self.text_rect = self.text.get_rect(center=(self.image.get_width()/2, self.image.get_height()/2))
        #render the text to the button
        self.image.blit(self.text, self.text_rect)

    def set_color(self, color):
        self.color = color