"""
Original Script:
https://www.youtube.com/watch?v=Mp57mHfOXTw
https://github.com/scartwright91/pygame-tutorials/tree/master/cut_scenes

Honorable mention:
    ChatGPT
    Gemini
"""
from settings import *

def draw_text(screen, text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)



class CutSceneOne:
    
    def __init__(self, player):

        # Variables
        self.name = 'test'
        self.step = 0
        self.timer = pygame.time.get_ticks()
        self.cut_scene_running = True

        # If we need to control the player while a cut scene running
        self.player = player

        # Dialogue
        self.text = {
            'one': "Hey get back in the middle!",
            'two': "That's better, now stay there."
        }
        self.text_counter = 0

    def update(self):

        pressed = pygame.key.get_pressed()
        space = pressed[pygame.K_SPACE]
        
        # First cut scene step (dialogue)
        if self.step == 0:
            if int(self.text_counter) < len(self.text['one']):
                self.text_counter += 0.4
            else:
                if space:
                    self.step = 1

        # Second part (player movement)
        if self.step == 1:
            if self.player.rect.centerx < 400:
                self.step = 2
                self.text_counter = 0
            else:
                self.player.rect.x -= 5

        # Third part (dialogue)
        if self.step == 2:
            if int(self.text_counter) < len(self.text['two']):
                self.text_counter += 0.4
            else:
                if space:
                    # Finish the cut scene
                    self.cut_scene_running = False

        return self.cut_scene_running

    def draw(self, screen):
        
        if self.step == 0:
            draw_text(
                screen,
                self.text['one'][0:int(self.text_counter)],
                50,
                (255, 255, 255),
                50,
                50
            )

        if self.step == 2:
            draw_text(
                screen,
                self.text['two'][0:int(self.text_counter)],
                50,
                (255, 255, 255),
                50,
                50
            )



class CutSceneManager:

    def __init__(self, screen):
        self.cut_scenes_complete = []
        self.cut_scene = None
        self.cut_scene_running = False

        # Drawing variables
        self.screen = screen
        self.window_size = 0

    def start_cut_scene(self, cut_scene):
        if cut_scene.name not in self.cut_scenes_complete:
            self.cut_scenes_complete.append(cut_scene.name)
            self.cut_scene = cut_scene
            self.cut_scene_running = True

    def end_cut_scene(self):
        self.cut_scene = None
        self.cut_scene_running = False

    def update(self):

        if self.cut_scene_running:
            if self.window_size < self.screen.get_height()*0.3: self.window_size += 2
            self.cut_scene_running = self.cut_scene.update()
        else:
            self.end_cut_scene()

    def draw(self):
        if self.cut_scene_running:
            # Draw rect generic to all cut scenes
            pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, self.screen.get_width(), self.window_size))
            # Draw specific cut scene details
            self.cut_scene.draw(self.screen)
class DialogueScene:
    
    def __init__(self, name, player, dialogue_data):
        self.name = name 
        # dialogue_data: {1: "Metin 1", 2: "Metin 2", ...} şeklinde diyalog içeriği
        self.dialogue = dialogue_data
        
        # self.player objesine ihtiyacımız kalmasa da, manager'ın yapısını korumak için tutabiliriz.
        self.player = player 
        
        self.current_step = 1 # Diyalog metinlerinin anahtarını tutar (1, 2, 3...)
        self.max_steps = len(dialogue_data)
        self.text_counter = 0  # Yazıların yavaşça belirmesi için
        self.cut_scene_running = True
        self.can_advance = True # Space spam'ini engellemek için cooldown

    def update(self):
        
        pressed = pygame.key.get_pressed()
        space = pressed[pygame.K_SPACE]
        
        # Space tuşuna basılıp basılmadığını kontrol et
        if space and self.can_advance:
            # Önceki metin tamamen yazılmış mı?
            current_text_key = self.current_step
            if int(self.text_counter) >= len(self.dialogue.get(current_text_key, '')):
                
                # Metin tamamen yazıldı, bir sonraki adıma geç
                self.current_step += 1
                self.text_counter = 0 # Yeni metin için sayacı sıfırla
                self.can_advance = False # Cooldown başlat
                pygame.time.set_timer(pygame.USEREVENT + 1, 300, 1) # 300ms sonra tekrar ilerlemeyi sağla

        # İlerleme cooldown'u
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT + 1:
                self.can_advance = True
        
        # Metin yavaş yavaş yazılıyorsa sayacı artır
        if self.current_step <= self.max_steps:
            current_text = self.dialogue[self.current_step]
            if int(self.text_counter) < len(current_text):
                self.text_counter += 0.4 
                self.can_advance = False # Yazı bitene kadar atlamayı engelle
            else:
                self.can_advance = True # Yazı bitti, artık space ile atlayabilir
        else:
            # Tüm adımlar bitti
            self.cut_scene_running = False

        return self.cut_scene_running

    def draw(self, screen):
        # Sadece mevcut adımı çiz
        if self.current_step <= self.max_steps:
            current_text = self.dialogue[self.current_step]
            
            draw_text(
                screen,
                current_text[0:int(self.text_counter)], # Yavaşça beliren metin
                50,
                (255, 255, 255),
                50,
                50
            )

# NOT: 'CutSceneManager' sınıfında bir değişiklik yapmaya gerek yok, çünkü
# 'update' ve 'draw' metotlarını kullanmaya devam edecek.