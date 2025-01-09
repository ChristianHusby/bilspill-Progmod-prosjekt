import pygame
import math
import csv
import os
from kart2 import *
from spritesheett import Spritesheet
import sys

width, height = 1000,600
pygame.init()
overflate = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Bilspill !!!")
font = pygame.font.Font(None, 46)
text_color = (255, 0, 0)
advarsel = font.render("KOM DEG TILBAKE PÅ VEIEN!", True, text_color)
global målstrek_aktivert
målstrek_aktivert = False
målstrek = pygame.Rect(200, 512, 10, 64)
global tid_best
tid_best = 5000
global tid_best_overflate
tid_best_overflate = 0
bakgrunn = pygame.image.load("bakgrunn.png")


checkpoints = [
    pygame.Rect(0, 400, 64, 50),
    pygame.Rect(330, 128, 50, 64),
    pygame.Rect(576, 300, 64, 50),
    pygame.Rect(385, 385, 64, 64)
]

spritesheet = Spritesheet('roads2W.png')
map = TileMap('road_map2.csv', spritesheet) # her lages og initieres banen min. Dette gjør den gjennom de andre python kodene mine. Den henter informasjon om posisjon og hva slags veiblokk fra denne csv filen som da kommer fra programmet Tiled, som jeg har brukt til å lage banen min. 

global tid_start
tid_start = False
global delta_tid
delta_tid = None
running = True
tittel_text = font.render("Velkommen til mitt bilspill!", True, (255,255,0))
intro_text = font.render("Målet ditt er å kjøre en runde så fort som mulig!", True, (255,255,0))
intro_text2 = font.render("du beveger deg med piltastene, trykk på r for å resette en runde", True, (255,255,0))
start_text = font.render("trykk på space for å starte.", True, (255,255,0))
def intro_skjerm():
    while True:
        overflate.fill((0,0,0))  
        overflate.blit(bakgrunn,(0,0))

        
        overflate.blit(tittel_text, (width // 2 - tittel_text.get_width() // 2, height // 3))
        overflate.blit(intro_text, (width // 2 - intro_text.get_width() // 2, height // 2))
        overflate.blit(intro_text2, (width // 2 - intro_text2.get_width() // 2, height // 1.75))
        overflate.blit(start_text, (width // 2 - start_text.get_width() // 2, height // 1.5))

       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  
                if event.key == pygame.K_SPACE:  
                    return  

        
        pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    global player
    player = Spiller((200, 545, 180))
    global all_sprites
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    global checkpoints_aktivert
    checkpoints_aktivert = checkpoints_system(checkpoints)
    global målstrek_aktivert
    global running
    global tid_start
    global delta_tid
    global tid_best
    global tid_best_overflate
    global variabel
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # åpner for å starte ny runde hvis man vil det
                    reset_game()

        keys = pygame.key.get_pressed()

        # Oppdaterer spiller bevegelsen
        if keys[pygame.K_UP]:  
            player.move_forward(forward=True)
            
            if delta_tid is None: # Initierer tidtakeren når spilleren starter å kjøre bilen
                delta_tid = pygame.time.get_ticks()
        elif keys[pygame.K_DOWN]:  
            player.move_forward(forward=False, reverse=True)
            if delta_tid is None:
                delta_tid = pygame.time.get_ticks()
        else:  # gradvis mister fart hvis ingen input
            player.move_forward(forward=False)

        if keys[pygame.K_LEFT]:  # roterer bilen
            player.rotate(-3)
        if keys[pygame.K_RIGHT]:  
            player.rotate(3)

        all_sprites.update()
        clock.tick(60)
        overflate.fill((0, 0, 0)) # hvert tick blir skjermen nullstilt med fargen svart

        map.draw_map(overflate) # tegner banen
        player.sjekk_underlag(overflate) # initierer en funksjon som sjekker om spiller er på banen. endrer fart etter om spilleren er på vei, gress, eller utenfor banen
        all_sprites.draw(overflate) 
        count_checkpoints = checkpoints_aktivert.update(player.rect)
        pygame.draw.rect(overflate, (255, 255, 0), målstrek) # tegner målstreken

        if tid_best_overflate != 0:
            overflate.blit(tid_best_overflate, (750, 50))
        author_tid = 15
        author_tekst = f"Author time: {author_tid}s"           #viser tid til skaperen(meg) som spilleren kan prøve å slå
        tid_overflate = font.render(author_tekst, True, (255, 255, 0))
        overflate.blit(tid_overflate, (750, 100))
        if delta_tid is not None:
            tid_milli = pygame.time.get_ticks() - delta_tid
            tid = tid_milli / 1000

            tid_tekst = f"Time: {tid}s"
            tid_overflate = font.render(tid_tekst, True, (255, 255, 0))
            overflate.blit(tid_overflate, (0, 50)) #Initierer tidtaking av spillerens runde

        if målstrek_aktivert:
            if player.rect.colliderect(målstrek):
                rundetid = (pygame.time.get_ticks() - delta_tid) / 1000
                
                if rundetid < tid_best: #hele denne if funksjon rekken sjekker om spilleren har gått gjennom alle checkpoints, og dermed også om spilleren har kjørt over målstreken. Når personen kjører over målstreken sjekker den om rundetiden er bedre enn den nåværende beste tiden. Hvis den er det oppdaterer den PB på skjermen.
                    tid_best = rundetid
                    print("dette er rundetiden;", rundetid)

                    tid_best_tekst = f"PB: {tid_best}s"
                    tid_best_overflate = font.render(tid_best_tekst, True, (255, 255, 0))

                målstrek_aktivert = False
                checkpoints_aktivert.reset()
                delta_tid = None
                #resetter en del variabler for å gjøre klar for neste runde.

        pygame.display.flip()


class checkpoints_system: # Lager en klasse for checkpoints sånn at spilleren må gjennom 4 forskjellig checkpoint plasser rundt på banen før den har lov til å gå over målstreken. Dette var viktig for at spilleren ikke finner noe "loopholes" og får en ugyldig tid.
    def __init__(self, checkpoints):
        self.checkpoints = checkpoints
        self.variabel = 0

    def update(self, player_rect):
        if self.variabel < 4:
            if player_rect.colliderect(self.checkpoints[self.variabel]):
                self.variabel += 1
                
                if self.variabel == 4:
                    global målstrek_aktivert
                    målstrek_aktivert = True
                    

    def reset(self): # resetter variablen slik at den også kan brukes til neste runde.
        self.variabel = 0


class Spiller(pygame.sprite.Sprite): # hele klassen som definerer og lager spilleren min. 
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        original_bilde = pygame.image.load("lightningmcqueen.png") # veldig kul bil!
        self.image = pygame.transform.scale(original_bilde, (30, 30))
        self.original_image = self.image # Her initierer vi spilleren definert med bildet vårt
        self.rect = self.image.get_rect() # Lager også en rektangel som alltid oppdateres etter bildet for å få riktig collision detection
        self.rect.center = (500, 300)
        self.x, self.y, self.angle = position
        self.speed = 0 # her definerer vi en del variabler for å styre bilens bevegelse. Blant annet toppfart 2 og hvor raskt bilen akselererer. 
        self.max_speed = 2
        self.acceleration = 0.1
        self.deceleration = 0.1
        self.friction = 0.025
        self.angle = 180
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        

    def update(self):
        self.rect.center = (self.x, self.y)
        self.keep_within_bounds()

    def move_forward(self, forward, reverse=False): # Her bestemmer vi bevegelsen av spilleren. Vi bruker mange forskjellige if statements for å avgjøre hva som skal gjøres med bilen for å holde seg innen sine grenser.
        if forward:
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
        elif reverse:
            self.speed -= self.acceleration
            if self.speed < -self.max_speed / 2: # rygging er treigere
                self.speed = -self.max_speed / 2
        else:
            #dersom ikke spilleren har noe input skal den sjekke nedover her
            if self.speed > 0:
                self.speed -= self.friction
                if self.speed < 0:
                    self.speed = 0
            elif self.speed < 0:
                self.speed += self.friction
                if self.speed > 0:
                    self.speed = 0
        #Vektorregning for å kalkulere bevegelsen til spilleren, forklares nærmere her: https://www.pygame.org/docs/tut/tom_games4.html
        radians = math.radians(self.angle)
        self.x += self.speed * math.cos(radians)
        self.y += self.speed * math.sin(radians)

    def rotate(self, degrees):
        self.angle = (self.angle + degrees) % 360
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def keep_within_bounds(self):
        if self.rect.left < 0:
            self.x = self.rect.width // 2
        if self.rect.right > overflate.get_width():
            self.x = overflate.get_width() - self.rect.width // 2
        if self.rect.top < 0:
            self.y = self.rect.height // 2
        if self.rect.bottom > overflate.get_height():
            self.y = overflate.get_height() - self.rect.height // 2

    def sjekk_underlag(self, map_surface):
        bil_x, bil_y = int(player.rect.centerx), int(player.rect.centery)
        farge = map_surface.get_at((bil_x, bil_y))[:3]

        jord_farge = (160, 192, 112)

        if farge == jord_farge:
            self.speed *= 0.8  #reduserer fart på spiller hvis den kjører på jord
        elif farge == (0, 0, 0):
            self.speed *= 0.6  #reduserer fart utenfor banen
            overflate.blit(advarsel, (500, 500))
        else:
            pass
def reset_game():
    global player, tid_start, delta_tid, tid_best_overflate, målstrek_aktivert, variabel, checkpoints_aktivert
    #resetter alt til start sånn at spilleren kan starte en ny runde
    player = Spiller((200, 545, 180))  # flytter spilleren til start
    all_sprites.empty()  
    all_sprites.add(player)
    tid_start = False
    delta_tid = None
    målstrek_aktivert = False
    variabel = 0
    
    checkpoints_aktivert.reset()
    print("game reset!")
intro_skjerm()
main()
