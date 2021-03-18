import pygame as pg
from settings import *
import pytmx

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

class TiledMap: # use this for loading tiled application maps
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelaplha=True) # this will load the file in pytmx
        self.width = tm.width * tm.tilewidth # this gets width of map
        self.height = tm.height * tm.tileheight # this gets the height
        self.tmxdata = tm

    def render(self, surface): # this takes a surface and draw tiles on to it
        ti = self.tmxdata.get_tile_image_by_gid # goes through tiled map data by img id
        for layer in self.tmxdata.visible_layers: # goes through each visible layer in map
            if isinstance(layer, pytmx.TiledTileLayer): # checks for tiled tile layer (other layers later)
                for x, y, gid in layer: # for each of these values
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile,(x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight)) # draws tile to surface with correct positioning

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height)) # makes a surface with map w & h
        self.render(temp_surface) # calls the render method
        return temp_surface # returns the surface


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity): # this applies camera to sprite
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect): # this applies camera to rect
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)