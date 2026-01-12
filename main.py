from settings import *
from player import Player
from sprites import *
from random import randint,choice
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from cut_scenes import CutSceneManager, CutSceneOne,DialogueScene


class Game:

    # Structure that contains all level dialogues and their properties
    LEVEL_DIALOGUES = {
        1: {
            'name': 'level_1_intro',
            'dialogue': {
                1: "Silahın var...      [Space]",
                2: "kullan...                         [Space]",
                3: "Yıldızlar güneşe yaklaşmana yardımcı olur                  [Space]",
                4: "Bahadır Erkayalar da yolu kapatır                  [Space]",
                5: "Capiche?              [Space]",
                6: "İzlemediysen git youtubeden intro videosunu izle     [Space]",
                7: "Oyun bitince de git outroyu izle     [Space]",
                # 4: "               [Press_Space]"
            }
        },
        2: {
            #
            'name': 'İLERLE.',
            'dialogue': {
                1: "Görünüşe göre erkayalar yolu kapatmış       [Space]",
                2: "Onları geçmek için 20 düşman öldür       [Space]",
                3: "İLERLE.       [Space]",
            }
        },
        3: {
            #
            'name': 'level_3_intro',
            'dialogue': {
                1: "Level 3'e hoş geldin.",
                2: "Sen çok fenasal bir şeysin",
                
            },
        4: {
            'name': 'level_4_intro',
            'dialogue': {
                1: "Buraya da yazıyım bir şeyler boş kalmasın",
                2: "Seni çok seviyorum lütfen evlen benimle",
            }
        },
        9: {
            #death
            'name': 'death',
            'dialogue': {
                1: "Skill issue???  [(‿ˠ‿)]? ",

            }
        },
        },
        

    }

    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Hell YEAHHHH')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 230

        #enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event,100)
        self.spawn_positions = []

        #audio
        self.shoot_sound = pygame.mixer.Sound(join('audio','shoot.wav'))
        self.shoot_sound.set_volume(0.1)
        self.impact_sound = pygame.mixer.Sound(join('audio','impact.ogg'))
        self.music = pygame.mixer.Sound(join('audio','intro demo.wav'))
        self.music.set_volume(0.4)
        self.music.play(loops = -1)

        # Level Management
        self.current_level = 1
        self.max_levels = 5
        self.level_is_over = False
        self.isDead = False
        self.score = 0

        #videos


        #cut_scene mangement
        self.cutscene_manager = CutSceneManager(self.display_surface)
        self.starting_cutscene = None

        #setup
        self.load_images()
        self.setup()



    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()
        folders = list(walk(join('images','enemies')))[0][1]
        self.enemy_frames = {}

        for folder in folders:

            for folder_path,_,file_names in walk(join('images','enemies',folder)):
                self.enemy_frames[folder] = []

                for file_name in sorted(file_names,key = lambda name : int(name.split('.')[0])): #0.png
                    full_path = join(folder_path,file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True
                self.shoot_time = pygame.time.get_ticks()

    def setup(self):
        #Level map .tmx files
        LEVEL_MAPS = {
        1: 'world.tmx', 
        2: 'world2.tmx', 
        3: 'world3.tmx'  ,
        4: 'world4.tmx' ,
        5: 'world5.tmx'  
    }

        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.spawn_positions.clear()


        map_file = LEVEL_MAPS.get(self.current_level)

        if not map_file:
            # End all levels, end game 
            print("Tüm leveller tamamlandı!")
            self.running = False
            return

        print(f"Level {self.current_level} yükleniyor: {map_file}")
        map_path = join('data', 'maps', map_file)
        map = load_pygame(map_path)
        print(map.get_layer_by_name('Ground'))


        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            sprite = CollisionSprite((obj.x,obj.y),obj.image,(self.all_sprites,self.collision_sprites))
            sprite.is_removable = True

        for obj in map.get_layer_by_name('Stars'):
            sprite1 = CollisionSprite((obj.x,obj.y),obj.image,(self.all_sprites,self.collision_sprites))
            sprite1.is_exit = True # Mark as level escape object

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x,obj.y),pygame.Surface((obj.width,obj.height)),self.collision_sprites)


        for obj in map.get_layer_by_name('Entities'):

            if obj.name =='Player':
                self.player = Player((obj.x,obj.y), self.all_sprites,self.collision_sprites)
                self.gun = Gun(self.player,self.all_sprites)
                self.starting_cutscene = CutSceneOne(self.player)

            else:
                self.spawn_positions.append((obj.x,obj.y))

        pygame.time.set_timer(self.enemy_event, 100)
        self.check_and_start_cutscene(False)
        
        self.level_is_over = False

    def check_star_collision_for_level_end(self):
        collided_stars = pygame.sprite.spritecollide(self.player, self.collision_sprites, False)
        for sprite in collided_stars:

            if hasattr(sprite, 'is_exit') and sprite.is_exit:
                self.level_is_over = True
                self.level_end_time = pygame.time.get_ticks() 
                print("Star objesiyle çarpışma! Level bitişi tetiklendi.")
                sprite.kill()
                break

    def check_and_start_cutscene(self,dead = False):
            if dead == False:
                dialogue_info = self.LEVEL_DIALOGUES.get(self.current_level)

                if dialogue_info:
                    # Create DialogueScene example dinamically
                    new_dialogue_scene = DialogueScene(
                        name = dialogue_info['name'],
                        player = self.player,
                        dialogue_data = dialogue_info['dialogue']
                    )
                    # Start with CutSceneManager
                    self.cutscene_manager.start_cut_scene(new_dialogue_scene)
                    print(f"Level {self.current_level} için diyalog başlatılıyor.")

                else:
                    print(f"Level {self.current_level} için özel diyalog yok.")

            if dead == True:
                dialogue_info = self.LEVEL_DIALOGUES.get(9)#lies,god damn lies (╯’□’)╯︵ ┻━┻

                if dialogue_info:
                    # Create DialogueScene example dinamically 
                    new_dialogue_scene = DialogueScene(
                        name = dialogue_info['name'],
                        player = self.player,
                        dialogue_data = dialogue_info['dialogue']

                    )
                    # CutSceneManager ile başlat
                    self.cutscene_manager.start_cut_scene(new_dialogue_scene)





    def bullet_collision(self):
        if self.bullet_sprites:
            
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet,self.enemy_sprites,False,pygame.sprite.collide_mask)

                if collision_sprites:
                    self.impact_sound.play()

                    for sprite in collision_sprites:
                        sprite.destroy()
                        self.score += 1

                    bullet.kill()





    def player_collision(self):
        if pygame.sprite.spritecollide(self.player,self.enemy_sprites,False,pygame.sprite.collide_mask):
            self.isDead = True
            self.score = 0 

        pass

    def check_level_end(self):
            # Level ending  case
            # self.level_is_over = True
            # print(f"Level {self.current_level} bitti!")
            # self.level_end_time = pygame.time.get_ticks()
            pass

    def draw_text(self,screen, text, size, color, pos):
        """
        Draws text with properties given ( ͡° ͜ʖ ͡° )
        
        :param self: self
        :param screen: Display surface / self.display_surface
        :param text: Text
        :param size: Size of your text
        :param color: RGB color of your text
        :param pos: Position of your text (x,y) starts from top left
        """
        font = pygame.font.SysFont(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(topleft=pos) 
        screen.blit(text_surface, text_rect)

    def check_score_and_remove_objects(self):
        """
        Checks self.score and if self.score is higher than 20, removes objects (erkayalar) tagged as 'is_removable=True' 

        """
        if self.score >= 20 and not self.level_is_over:
            
            removed_count = 0
            
            #loop over copy of self.collision_sprites group
            for sprite in self.collision_sprites.copy():
                
                # Check objects that tagged as removable
                if hasattr(sprite, 'is_removable') and sprite.is_removable:
                    sprite.kill()
                    removed_count += 1
            
            # Print removed object count (for test purposes I believe???)
            if removed_count > 0:
                print(f"SKOR 20'ye ulaştı. Haritadan {removed_count} adet Object kaldırıldı.")
                # self.level_is_over = True

    def transition_level(self):
            """
            Increases self.current level and changes level self.music
            
            :param self: Description
            """
            if self.level_is_over:

                current_time = pygame.time.get_ticks()

                if current_time - self.level_end_time >= 0.000001:
            
                    if self.current_level < self.max_levels:
                        self.score = 0
                        self.music.stop()
                        self.current_level += 1
                        
                        if self.current_level == 2:
                            self.music = pygame.mixer.Sound(join('audio','clubsal bişi.mp3'))
                            self.music.set_volume(0.4)
                            self.music.play(loops = -1)

                        if self.current_level == 3:
                            self.music = pygame.mixer.Sound(join('audio','kozmik sarkı demo.mp3'))
                            self.music.set_volume(0.4)
                            self.music.play(loops = -1)

                        if self.current_level == 4:
                            self.music = pygame.mixer.Sound(join('audio','potential outro.mp3'))
                            self.music.set_volume(0.4)
                            self.music.play(loops = -1)
                            
                        if self.current_level == 5:
                            self.music = pygame.mixer.Sound(join('audio','dark-wet-eerie-japanese-vocals_110bpm_C_major (1).wav'))
                            self.music.set_volume(0.4)
                            self.music.play(loops = -1)

                        self.setup()

                    else:
                        print("TEBRİKLER! OYUN BİTTİ.")
                        self.running = False

            elif self.isDead:
                self.setup()
                self.isDead = False

    def run(self):

        while self.running:

            # set delta time
            dt = self.clock.tick(60) / 1000

            # event loop
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
   
                    self.running = False

            if event.type == self.enemy_event:
                # 1. Continue if there is a spawn location.
                if self.spawn_positions: 
                    # 2. Generate enemy
                    Enemy(
                        choice(self.spawn_positions),
                        choice(list(self.enemy_frames.values())),(self.all_sprites,self.enemy_sprites),self.player,self.collision_sprites 
                    )

            # draw
            self.display_surface.fill('black')
            self.cutscene_manager.update()

            if not self.cutscene_manager.cut_scene_running: # Checking if cutscene is not working

                self.gun_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.player_collision()

                # Level ending control
                self.check_score_and_remove_objects()
                
                # *** New level ending control ***
                self.check_star_collision_for_level_end()
                self.check_level_end()

                self.transition_level()

            self.all_sprites.draw(self.player.rect.center)
            score_text = f"Leş: {self.score}"
            
            text_x = WINDOW_WIDTH - 200 
            text_y = 10                  
            
            self.draw_text(
                        self.display_surface,          
                        score_text,                   
                        40,                             
                        (255, 255, 255),                
                        (text_x, text_y)                
                    )
            self.cutscene_manager.draw()
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()