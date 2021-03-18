# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 20
# Player and Mob Health
# https://www.youtube.com/watch?v=xIcDqw35rz8&t=16s
import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *

# HUD functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)



class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        map_folder = path.join(game_folder, 'maps')
        music_folder = path.join(game_folder, 'music')
        snd_folder = path.join(game_folder, 'snd')
        self.title_font = path.join(img_folder, 'ZOMBIE.TTF') # this loads the font into images folder
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha() # this crates a screen size surface
        self.dim_screen.fill((0, 0, 0, 180)) # this fills the surface will black but translucent
        #self.map = Map(path.join(game_folder, 'map3.txt'))
        self.map = TiledMap(path.join(map_folder, 'tiled1.tmx')) # calls the tiled class and passes map in
        self.map_img = self.map.make_map() # makes a img of the map
        self.map_rect = self.map_img.get_rect() # makes a rect for drawing
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha() # loads zombie blood splatter
        self.splat = pg.transform.scale(self.splat, (64, 64)) # this changes scale of image that just loaded
        self.gun_flashes = [] # create list to hold images
        for img in MUZZLE_FLASHES: # loops through all the imgs in muzzle list
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
            # this adds each img to the list and joins a path
        self.item_images = {} # create dic to hold images
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
            # this adds all item name and image as dic to item_images

        #Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC)) # this loads the bg_music from settings
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS: # this loops through the sound effects dict in settings
            self.effects_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
            # this adds the sounds as a dict for calling specific ones
        self.weapon_sounds = {}
        self.weapon_sounds['gun'] = []
        for snd in WEAPON_SOUNDS_GUN:
            self.weapon_sounds['gun'].append(pg.mixer.Sound(path.join(snd_folder, snd))) #this loops thro dict and adds to weapons sounds
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd)) # this loads the sound as a var
            s.set_volume(0.2) # this sets volume for sound before adding it to list (0 - 1)
            self.zombie_moan_sounds.append(s) # this adds adjusted sound to list
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates() # this allows for layers to be set on all sprites
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.room_shadow = pg.sprite.Group()
        self.kills = 0
        # This is old method of drawing txt maps
        #for row, tiles in enumerate(self.map.data):
         #   for col, tile in enumerate(tiles):
          #      if tile == '1':
           #         Wall(self, col, row)
            #    if tile == 'M':
             #       Mob(self, col, row)
              #  if tile == 'P':
               #     self.player = Player(self, col, row)

        for tile_object in self.map.tmxdata.objects: # loops through each object in the object layers of tiled
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2) # this sets spawn center point
            if tile_object.name == 'player': #  checks if the tile objects name is player
                self.player = Player(self, obj_center.x, obj_center.y) # draws player to the tile object x y
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height) # spawns wall obstacle where tile x y d
            if tile_object.name == "mob":
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name in ['health']:
                Item(self, obj_center, tile_object.name)
            if tile_object.name in ['room']:
                room_width, room_height = int(tile_object.width), int(tile_object.height)
                Room_Shadow(self, obj_center, tile_object.name, room_width, room_height)
            if tile_object.name in ['roof']:#testing roof feature
                roof_width, roof_height = int(tile_object.width), int(tile_object.height)
                Roof(self, obj_center, tile_object.name, roof_width, roof_height)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.effects_sounds['level_start'].play() # this starts music from effects sounds dict

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1) # this plays music at start of game on loop
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0  # fix for Python 2.x
            self.events() # this checks for events
            if not self.paused: # only if not paused will the game update
                self.update() # this updates everything keeps it moving
            self.draw() # this draws the images to screen

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        # player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False) # creates list of hits for collisions with player and items
        for hit in hits: # checks list
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH: # if player hits item and health isn't full
                hit.kill() # item gets removed
                self.effects_sounds['health_up'].play() # this plays music from effects dictd
                self.player.add_health(HEALTH_PACK_AMOUNT) # triggers func in player class to add more health

        # player enters house takes off roof then shows dark rooms
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'roof':
                hit.image.set_alpha(0)

        hits = pg.sprite.spritecollide(self.player, self.room_shadow, False)
        for hit in hits:
            if hit.type == 'room':
                hit.image.set_alpha(0)


        # mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play() # this gives strong chance for rand hit sound to play when zombie its player
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.health -= BULLET_DAMAGE
            hit.vel = vec(0, 0)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect)) # draws the map img to the screen and uses camera location
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, RED, self.camera.apply_rect(sprite.hit_rect), 1) # this will draw a rect on hitbox for sprites
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, RED, self.camera.apply_rect(wall.rect), 1)  # this will draw a rect on hitbox for sprites

        # pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0)) # draws the dim screen on the screen surface
            self.draw_text('Paused', self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align='center')
            self.draw_text(str(self.kills) + " Kills", self.title_font, 60, RED, WIDTH / 2, HEIGHT * 0.75, align='center')
            # this draws paused text to the screen when paused
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_TAB:
                    self.draw_debug = not self.draw_debug # this will allow you to toggle every time you hit key
                if event.key == pg.K_p:
                    self.paused = not self.paused # this inverts the paused bool
                    # this used in run method


    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()