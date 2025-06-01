import pgzrun
from pygame import Rect
import json
import time

#  Configurações 
WIDTH = 540
HEIGHT = 360
TITLE = "Alien Platformer"

TILE_SIZE = 18  
MAP_WIDTH = 30
MAP_HEIGHT = 20

# Variáveis de controle
game_state = 'menu'
sound_on = True
moedas_coletadas = 0
vitoria = False
vitoria_timer = 0

# Estrutura do mapa
tiles_plataforma = []
tiles_obstaculos = []
tiles_moedas = []
tiles_bg = []
tiles_vitoria = []

# Mapeamento de tile_id para imagem 
tile_images_plataforma = {
    2: 'tile_0001.png',
    3: 'tile_0002.png',
    4: 'tile_0003.png',
    48: 'tile_0047.png',
    49: 'tile_0048.png',
    50: 'tile_0049.png',
    51: 'tile_0050.png',
    102: 'tile_0101.png',
    103: 'tile_0102.png',
    104: 'tile_0103.png',
    122: 'tile_0121.png',
    123: 'tile_0122.png',
    124: 'tile_0123.png',
    142: 'tile_0141.png',
    143: 'tile_0142.png',
    144: 'tile_0143.png',
}

tile_images_obstaculos = {
    34: 'tile_0033.png',
}

tile_images_moedas = {
    152: 'tile_0151.png',
}

tile_images_bg = {
    189: 'backgrounds/tile_0006.png',
    199: 'backgrounds/tile_0007.png',
    219: 'backgrounds/tile_0022.png',
}

tile_images_vitoria = {
    112: 'tile_0111.png',
    132: 'tile_0131.png',
}

class Hero:
    def __init__(self, x, y, speed=3, gravity=0.5):
        self.actor = Actor('hero', (x, y))
        self.speed = speed
        self.vy = 0
        self.gravity = gravity
        self.on_ground = False

    def update(self, tiles_plataforma):
        if keyboard.left:
            self.actor.x -= self.speed
        if keyboard.right:
            self.actor.x += self.speed

        self.vy += self.gravity
        self.actor.y += self.vy

        self.on_ground = False
        hero_rect = self.get_rect()
        for plat_rect, _ in tiles_plataforma:
            if hero_rect.colliderect(plat_rect) and self.vy >= 0:
                self.actor.y = plat_rect.y - self.actor.height // 2
                self.vy = 0
                self.on_ground = True
                break

        if keyboard.up and self.on_ground:
            self.vy = -8

    def get_rect(self):
        return Rect(
            self.actor.x - self.actor.width // 2,
            self.actor.y - self.actor.height // 2,
            self.actor.width,
            self.actor.height
        )

    def draw(self):
        self.actor.draw()

class Enemy:
    def __init__(self, x, y, speed=2, direction=1, move_range=(220, 400)):
        self.actor = Actor('enemy', (x, y))
        self.speed = speed
        self.direction = direction
        self.range = move_range

    def update(self):
        self.actor.x += self.speed * self.direction
        if self.actor.x < self.range[0] or self.actor.x > self.range[1]:
            self.direction *= -1

    def get_rect(self):
        return Rect(
            self.actor.x - self.actor.width // 2,
            self.actor.y - self.actor.height // 2,
            self.actor.width,
            self.actor.height
        )

    def draw(self):
        self.actor.draw()

# Instanciando personagens
hero = Hero(100, 300)
enemy = Enemy(300, 325)

# Carregar mapa JSON 
def load_layer(map_data, layer_name, tiles_list):
    layers = map_data['layers']
    for layer in layers:
        if layer['name'] == layer_name:
            data = layer['data']
            for index, tile_id in enumerate(data):
                if tile_id != 0:
                    col = index % MAP_WIDTH
                    row = index // MAP_WIDTH
                    x = col * TILE_SIZE
                    y = row * TILE_SIZE
                    rect = Rect((x, y, TILE_SIZE, TILE_SIZE))
                    tiles_list.append((rect, tile_id))

def load_map_json(filename):
    with open(filename) as f:
        map_data = json.load(f)
    load_layer(map_data, 'Plataforma', tiles_plataforma)
    load_layer(map_data, 'Obstaculos', tiles_obstaculos)
    load_layer(map_data, 'Moedas', tiles_moedas)
    load_layer(map_data, 'bg', tiles_bg)
    load_layer(map_data, 'Vitoria', tiles_vitoria)

load_map_json('map.json')

# Função de desenho
def draw():
    screen.clear()
    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        draw_game()

def draw_menu():
    screen.draw.text("Platformer Game", center=(WIDTH//2, HEIGHT//4), fontsize=60, color="white")
    screen.draw.text("1. Start Game", center=(WIDTH//2, HEIGHT//2 - 50), fontsize=40, color="yellow")
    screen.draw.text("2. Toggle Sound: {}".format("ON" if sound_on else "OFF"), center=(WIDTH//2, HEIGHT//2), fontsize=40, color="yellow")
    screen.draw.text("3. Quit", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=40, color="yellow")

def draw_game():
    screen.fill((0, 0, 0))

    for rect, tile_id in tiles_bg:
        image = tile_images_bg.get(tile_id)
        if image:
            screen.blit(image, (rect.x, rect.y))
        else:
            screen.draw.filled_rect(rect, (100, 200, 255))

    for rect, tile_id in tiles_plataforma:
        image = tile_images_plataforma.get(tile_id)
        if image:
            screen.blit(image, (rect.x, rect.y))
        else:
            screen.draw.filled_rect(rect, (100, 200, 255))

    for rect, tile_id in tiles_obstaculos:
        image = tile_images_obstaculos.get(tile_id)
        if image:
            screen.blit(image, (rect.x, rect.y))
        else:
            screen.draw.filled_rect(rect, (255, 0, 0))

    for rect, tile_id in tiles_moedas:
        image = tile_images_moedas.get(tile_id)
        if image:
            screen.blit(image, (rect.x, rect.y))
        else:
            screen.draw.filled_rect(rect, (255, 255, 0))

    for rect, tile_id in tiles_vitoria:
        image = tile_images_vitoria.get(tile_id)
        if image:
            screen.blit(image, (rect.x, rect.y))
        else:
            screen.draw.filled_rect(rect, (255, 255, 0))

    if vitoria:
        caixa_largura = 300
        caixa_altura = 100
        caixa_x = (WIDTH - caixa_largura) // 2
        caixa_y = (HEIGHT - caixa_altura) // 2
        caixa = Rect(caixa_x, caixa_y, caixa_largura, caixa_altura)

        screen.draw.filled_rect(caixa, (0, 128, 0))  
        screen.draw.text("VOCÊ VENCEU!", center=caixa.center, fontsize=40, color="white")

    screen.draw.text(f"Moedas: {moedas_coletadas}", topleft=(10, 10), fontsize=30, color="white")
    hero.draw()
    enemy.draw()

# Atualização do jogo
def update():
    if game_state == 'playing' and not vitoria:
        hero.update(tiles_plataforma)
        enemy.update()
        check_hero_enemy_collision()
        check_hero_obstaculo_collision()
        check_hero_collect_moedas()
        check_hero_vitoria()
    elif vitoria:
        check_vitoria_timer()

def check_hero_enemy_collision():
    if hero.get_rect().colliderect(enemy.get_rect()):
        hero.actor.x = 100
        hero.actor.y = 250
        sounds.damage.play()

def check_hero_collect_moedas():
    global moedas_coletadas
    hero_rect = hero.get_rect()
    for tile in tiles_moedas[:]:
        rect, tile_id = tile
        if hero_rect.colliderect(rect):
            tiles_moedas.remove(tile)
            moedas_coletadas += 1
            sounds.coin.play()

def check_hero_obstaculo_collision():
    hero_rect = hero.get_rect()
    for rect, tile_id in tiles_obstaculos:
        if hero_rect.colliderect(rect):
            hero.actor.x = 100
            hero.actor.y = 300
            sounds.damage.play()
            break

def check_hero_vitoria():
    global vitoria, vitoria_timer
    hero_rect = hero.get_rect()
    for tile in tiles_vitoria:
        rect, tile_id = tile
        if hero_rect.colliderect(rect):
            vitoria = True
            vitoria_timer = time.time()
            music.stop()
            sounds.vitoria.play()
            print("Vitória!")
            break

def check_vitoria_timer():
    global game_state, vitoria
    if time.time() - vitoria_timer >= 3:
        vitoria = False
        reset_game()
        game_state = 'menu'

def reset_game():
    global moedas_coletadas
    hero.actor.x = 100
    hero.actor.y = 300
    moedas_coletadas = 0

# Controle de teclas
def on_key_down(key):
    global game_state, sound_on
    if game_state == 'menu':
        if key == keys.K_1:
            game_state = 'playing'
            music.stop()
            music.play('house.wav')
        elif key == keys.K_2:
            sound_on = not sound_on
            if sound_on:
                music.set_volume(0.5)
                music.play('menu.wav')  
            else:
                music.stop()  
        elif key == keys.K_3:
            quit()

pgzrun.go()
