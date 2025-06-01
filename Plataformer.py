import pgzrun
from pygame import Rect
import json
import time

# --- Configurações ---
WIDTH = 540
HEIGHT = 360
TITLE = "Alien Platformer"

TILE_SIZE = 18  # Conforme o mapa
MAP_WIDTH = 30
MAP_HEIGHT = 20

# --- Variáveis de controle ---
game_state = 'menu'
sound_on = True
moedas_coletadas = 0
vitoria = False
vitoria_timer = 0

# --- Estrutura do mapa: lista de tuplas (Rect, tile_id) ---
tiles_plataforma = []
tiles_obstaculos = []
tiles_moedas = []
tiles_bg = []
tiles_vitoria = []

# --- Mapeamento de tile_id para imagem ---
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
    152:'tile_0151.png',
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

hero = Actor('hero', (100, 300))  # coloque hero_idle.png na pasta images
hero_speed = 3
hero_vy = 0  # velocidade vertical
gravity = 0.5
on_ground = False

# --- Inimigo ---
enemy = Actor('enemy', (300, 325))  # coloque 'enemy_idle.png' na pasta images
enemy_speed = 2
enemy_direction = 1  # 1 = direita, -1 = esquerda
enemy_range = (220, 400)  # limites de movimento (x mínimo, x máximo)


# --- Carregar mapa JSON ---
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

# --- Função de desenho ---
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
    screen.fill((0, 0, 0))  # fundo preto
    
    # Desenhar background
    for rect, tile_id in tiles_bg:
        image = tile_images_bg.get(tile_id)
        if image:
            screen.blit(image, (rect.x, rect.y))
        else:
            screen.draw.filled_rect(rect, (100, 200, 255))  # fallback amarelo
    
    # Desenhar plataformas
    for rect, tile_id in tiles_plataforma:
        image = tile_images_plataforma.get(tile_id)
        if image:
            screen.blit(image, (rect.x, rect.y))
        else:
            screen.draw.filled_rect(rect, (100, 200, 255))  # fallback azul

    # Desenhar obstáculos
    for rect, tile_id in tiles_obstaculos:
        image = tile_images_obstaculos.get(tile_id)
        if image:
            screen.blit(image, (rect.x, rect.y))
        else:
            screen.draw.filled_rect(rect, (255, 0, 0))  # fallback vermelho

    # Desenhar moedas
    for rect, tile_id in tiles_moedas:
        image = tile_images_moedas.get(tile_id)
        if image:
            screen.blit(image, (rect.x, rect.y))
        else:
            screen.draw.filled_rect(rect, (255, 255, 0))  # fallback amarelo

    # Desenhar moedas
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

        screen.draw.filled_rect(caixa, (0, 128, 0))  # verde escuro
        screen.draw.text("VOCÊ VENCEU!", center=caixa.center, fontsize=40, color="white")


    screen.draw.text(f"Moedas: {moedas_coletadas}", topleft=(10, 10), fontsize=30, color="white")
    hero.draw()
    enemy.draw()

# --- Atualização do jogo ---
def update():
    if game_state == 'playing'and not vitoria:
        update_hero()
        update_enemy()
        check_hero_enemy_collision()
        check_hero_collect_moedas()
        check_hero_vitoria()
    elif vitoria:
        check_vitoria_timer()

def update_hero():
    global hero_vy, on_ground

    # Movimento lateral
    if keyboard.left:
        hero.x -= hero_speed
    if keyboard.right:
        hero.x += hero_speed

    # Gravidade
    hero_vy += gravity
    hero.y += hero_vy

    # Colisão com plataformas
    on_ground = False
    hero_rect = Rect(hero.x - hero.width // 2, hero.y - hero.height // 2, hero.width, hero.height)
    for plat_rect, _ in tiles_plataforma:
        if hero_rect.colliderect(plat_rect) and hero_vy >= 0:
            hero.y = plat_rect.y - hero.height // 2
            hero_vy = 0
            on_ground = True
            break

    # Pulo
    if keyboard.up and on_ground:
        hero_vy = -8  # força do pulo

def update_enemy():
    global enemy_direction
    enemy.x += enemy_speed * enemy_direction

    # Inverter direção nos limites
    if enemy.x < enemy_range[0] or enemy.x > enemy_range[1]:
        enemy_direction *= -1

def check_hero_enemy_collision():
    hero_rect = Rect(hero.x - hero.width // 2, hero.y - hero.height // 2, hero.width, hero.height)
    enemy_rect = Rect(enemy.x - enemy.width // 2, enemy.y - enemy.height // 2, enemy.width, enemy.height)
    
    if hero_rect.colliderect(enemy_rect):
        hero.x = 100  # volta para o início
        hero.y = 250
        sounds.damage.play()


def check_hero_collect_moedas():
    global moedas_coletadas
    hero_rect = Rect(hero.x - hero.width // 2, hero.y - hero.height // 2, hero.width, hero.height)
    
    for tile in tiles_moedas[:]:  # cópia para remover sem erro
        rect, tile_id = tile
        if hero_rect.colliderect(rect):
            tiles_moedas.remove(tile)
            moedas_coletadas += 1
            sounds.coin.play()


def check_hero_vitoria():
    global vitoria, vitoria_timer
    hero_rect = Rect(hero.x - hero.width // 2, hero.y - hero.height // 2, hero.width, hero.height)
    
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
    import time
    if time.time() - vitoria_timer >= 3:  # ✅ espera 3 segundos
        vitoria = False
        reset_game()
        game_state = 'menu'

def reset_game():
    global hero, moedas_coletadas, tiles_moedas
    hero.x = 100
    hero.y = 300
    moedas_coletadas = 0

# --- Controle de teclas ---
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
                music.play('menu.wav')  # Reinicia a música
            else:
                music.stop()  # Para completamente
        elif key == keys.K_3:
            quit()

pgzrun.go()