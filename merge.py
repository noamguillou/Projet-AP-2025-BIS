import arcade
import math
import random
import matplotlib.pyplot as plt

BACKGROUND = arcade.color.ALMOND
PROBA_MALADIE = 0.1
PROBA_CONTAMINATION = 0.1
TEMPS_GUÉRISON = 500

COULEUR_VACCINATION_VISUEL = arcade.color.LIME_GREEN
COULEUR_guerison_VISUEL = arcade.color.BLUE 

# probabilité de guérison en fonction du temps d'attente
def proba_gérison(temps_malade):
    return 1 - math.exp(-0.0001 * temps_malade) 

# test de guérison aléatoire en fonction du temps d'attente
def test_guérison(temps_attente):
    p = random.random() 
    if p < proba_gérison(temps_attente):
        return True
    else:
        return False
    
#  fonction de distance entre deux boids
def distance(p1,p2) : 
    return math.sqrt( (p1.center_x - p2.center_x)**2 + (p1.center_y - p2.center_y)**2 )

# fonction de contamination entre deux boids
def contamination(personne_en_contacte, p_contamination) : 
    (p1,p2)= personne_en_contacte 
    if p1.etat == True and p2.etat == False and p2.vaccine == False: 
        if random.random() < p_contamination : 
            p2.etat = True
    elif p2.etat == True and p1.etat == False and p1.vaccine == False: 
        if random.random() < p_contamination : 
            p1.etat = True

# classe Boid qui représente une personne dans la simulation
class Boid(arcade.SpriteCircle):
    def __init__(self, position_x: float, position_y: float, angle: float, liste_boids, etat: bool = False, speed: float = 1.0, temps_malade: int = 0, temps_attente: int = 0, vaccine: bool = False):
        super().__init__(5, arcade.color.BLUE, False)
        self.center_x = position_x
        self.center_y = position_y
        self.angle = angle
        self.speed = speed
        self.etat = etat
        self.voisins = liste_boids
        self.temps_malade = temps_malade
        self.vaccine = vaccine 
        self.temps_attente = temps_attente  
        self.en_soin = False

    # fonction pour convertir l'angle en radians
    def angle_radian(self):
        return self.angle / 180 * math.pi

    # fonction de déplacement sans murs
    def deplacement_intelligent(self):
        if self.en_soin:
            return

        dx = math.cos(self.angle_radian()) * self.speed
        dy = math.sin(self.angle_radian()) * self.speed

        self.center_x += dx
        self.center_y += dy
        self.angle %= 360
    
    # fonction de contact avec les bords de la fenêtre
    def contact_bord(self):
        if self.center_x >= 795  or self.center_x <= 5 : 
            self.angle = 180 - self.angle
        if self.center_y >= 795 or self.center_y <= 5 :
            self.angle = -self.angle

    # fonction de contact avec les autres boids
    def contact_boid(self):
        if self.en_soin:
            return

        rayon_personne = 5
        for autre in self.voisins:
            if autre is not self:  
                if distance(self, autre) < 2 * rayon_personne:
                    self.angle = -self.angle + 180
                    # On ajoute un petit "push" pour éviter qu'ils collent entre eux aussi
                    self.center_x += math.cos(self.angle_radian()) * self.speed
                    self.center_y += math.sin(self.angle_radian()) * self.speed
                    break

    # fonction pour gérer l'état de maladie d'un boid
    def je_suis_malade(self):
        if self.etat == True :
            self.color = arcade.color.RED
            self.temps_malade += 1
        
        if self.vaccine:
            self.color = arcade.color.GREEN

    # fonction pour gérer la guérison d'un boid   
    def je_suis_guéri(self):
        if self.temps_malade >= TEMPS_GUÉRISON :
            self.etat = False
        if self.etat == False :
            self.color = arcade.color.BLUE
            self.temps_malade = 0
        if self.vaccine:
            self.color = arcade.color.GREEN
        
    # fonction de contact avec les boids malades pour gérer la contamination
    def contact_malade(self):
        rayon_personne = 5
        for autre in self.voisins:
            if autre is not self:  
                if self.en_soin or autre.en_soin:
                    continue  
                elif self.vaccine or autre.vaccine:
                    continue  
                elif distance(self, autre) < 2 * rayon_personne:
                    contamination((self,autre), PROBA_CONTAMINATION)
                    break

    # fonction de contact avec les zones de guérison
    def contact_guerison(self, liste_zones_guerison):
        en_zone = len(arcade.check_for_collision_with_list(self, liste_zones_guerison)) > 0
        
        if en_zone and self.etat == True:
            self.en_soin = True
            self.temps_attente += 1 
            
            if test_guérison(self.temps_attente):
                self.etat = False              
                self.color = arcade.color.BLUE  
                self.temps_malade = 0   
                self.temps_attente = 0
                self.en_soin = False           
                
        if not en_zone:
            self.en_soin = False
            self.temps_attente = 0

    # Vaccination des individus
    def contact_vaccination(self, liste_zones_vaccination): 
        if len(arcade.check_for_collision_with_list(self, liste_zones_vaccination)) > 0:
            self.vaccine = True      
            self.etat= False 
            self.temps_malade = 0   
            self.color = arcade.color.GREEN 
    
    # Fonction pour gérer les collisions avec les murs de confinement
    def contact_confinement(self):
        # Mur vertical
        if 390 <= self.center_x <= 410 and 425 <= self.center_y <= 775:
            self.angle = 180 - self.angle
            self.center_x += math.cos(self.angle_radian()) * self.speed
            self.center_y += math.sin(self.angle_radian()) * self.speed
        # Mur horizontal
        if 25 <= self.center_x <= 375 and 390 <= self.center_y <= 410:
            self.angle = -self.angle
            self.center_x += math.cos(self.angle_radian()) * self.speed
            self.center_y += math.sin(self.angle_radian()) * self.speed

# affichage 
class Window(arcade.Window):

    def __init__(self):
        super().__init__(800, 800, "Simulation Épidémie")
        arcade.set_background_color(BACKGROUND)
        self.set_location(800, 100)
        self.historique_sains = []
        self.historique_malades = []
        self.historique_vaccines = []
        self.temps = 0

        # Zones de guérison 
        self.liste_guerison = arcade.SpriteList()
        nb_zones_placees = 0
        
        while nb_zones_placees < 3:
            w = 50
            h = 60
            x = random.randint(w, 800 - w)
            y = random.randint(h, 800 - h)
            
            zone = arcade.SpriteSolidColor(w, h, arcade.color.TRANSPARENT_BLACK)            
            zone.center_x = x
            zone.center_y = y
            self.liste_guerison.append(zone)
            nb_zones_placees += 1 

        # Mise en place de zone de vaccination 
        self.liste_vaccination = arcade.SpriteList()
        nb_zones_placees_vaccination = 0
        
        while nb_zones_placees_vaccination < 3:
            w = 50
            h = 60
            x = random.randint(w, 800 - w)
            y = random.randint(h, 800 - h)
            
            zone = arcade.SpriteSolidColor(w, h, arcade.color.TRANSPARENT_BLACK)            
            zone.center_x = x
            zone.center_y = y
            self.liste_vaccination.append(zone)
            nb_zones_placees_vaccination += 1 

        # Initialisation de la liste des boids
        N = 150  # Nombre de boids
        self.boids =[]
        possibilites_1 = list(range(5, 390)) + list(range(410, 795))
        possibilites_2 = list(range(5, 25)) + list(range(410, 795))
        for k in range(N-int(PROBA_MALADIE*len(self.boids))):
            ang = random.randint(0, 360)
            x_pos = random.randint(5,795)
            y_pos = random.randint(5,795)
            if 390 <= x_pos <= 410 and 425 <= y_pos <= 775: # Si on tombe dans le mur vertical
                x_pos = random.choice(possibilites_1)
            if 25 <= x_pos <= 375 and 390 <= y_pos <= 410: # Si on tombe dans le mur horizontal
                y_pos = random.choice(possibilites_2)
            self.boids.append(Boid(x_pos, y_pos, ang, self.boids, False, temps_malade=0))

        # Iniatialisation de l'état de maladie de certains boids : "les patients zéros"
        for i in range(int(PROBA_MALADIE*len(self.boids))) :
            ang = random.randint(0, 360)
            x_pos = random.randint(5,390)
            y_pos = random.randint(410,795)
            self.boids.append(Boid(x_pos, y_pos, ang, self.boids, True, temps_malade=0))

        self.sprites = arcade.SpriteList()
        for boid in self.boids:
            self.sprites.append(boid)
    
    def on_update(self, delta_time):
        nb_sains = 0
        nb_malades = 0
        nb_vaccines = 0

        for boid in self.boids:
            boid.deplacement_intelligent()
            boid.contact_bord()
            boid.contact_boid()
            boid.je_suis_malade()
            boid.contact_malade()
            boid.je_suis_guéri()
            boid.contact_guerison(self.liste_guerison)
            boid.contact_vaccination(self.liste_vaccination)
            boid.contact_confinement()

            if boid.etat == True:
                nb_malades += 1
            else:
                nb_sains += 1

            if boid.vaccine == True:
                nb_vaccines += 1
        
        self.historique_sains.append(nb_sains)
        self.historique_malades.append(nb_malades)
        self.historique_vaccines.append(nb_vaccines)
        
        self.sprites.update()

    def on_draw(self):
            self.clear()
            arcade.draw_rect_filled(arcade.Rect(395, 405, 430, 770, 10, 340, 400, 600), arcade.color.GRAY) # Mur vertical
            arcade.draw_rect_filled(arcade.Rect(30, 370, 395, 405, 340, 10, 200, 400), arcade.color.GRAY) # Mur horizontal
            nb_sains = self.historique_sains[-1]
            nb_malades = self.historique_malades[-1]
            nb_vaccines = self.historique_vaccines[-1]

            ratio = nb_malades/(nb_sains + nb_malades)

            for zone in self.liste_guerison:
                gauche = zone.center_x - (zone.width / 2)
                droite = zone.center_x + (zone.width / 2)
                haut   = zone.center_y + (zone.height / 2)
                bas    = zone.center_y - (zone.height / 2)
                
                
                arcade.draw_line(gauche, haut, droite, haut, COULEUR_guerison_VISUEL, 2)
                arcade.draw_line(gauche, bas, droite, bas, COULEUR_guerison_VISUEL, 2)
                arcade.draw_line(gauche, bas, gauche, haut, COULEUR_guerison_VISUEL, 2)
                arcade.draw_line(droite, bas, droite, haut, COULEUR_guerison_VISUEL, 2)

            for zone in self.liste_vaccination:
                gauche = zone.center_x - (zone.width / 2)
                droite = zone.center_x + (zone.width / 2)
                haut   = zone.center_y + (zone.height / 2)
                bas    = zone.center_y - (zone.height / 2)
                
                arcade.draw_line(gauche, haut, droite, haut, COULEUR_VACCINATION_VISUEL, 2)
                arcade.draw_line(gauche, bas, droite, bas, COULEUR_VACCINATION_VISUEL, 2)
                arcade.draw_line(gauche, bas, gauche, haut, COULEUR_VACCINATION_VISUEL, 2)
                arcade.draw_line(droite, bas, droite, haut, COULEUR_VACCINATION_VISUEL, 2)

            self.barre_width = 100
            self.barre_height= 10
            arcade.draw_lbwh_rectangle_filled(0, 5, self.barre_width, self.barre_height, color = (0,255, 0))
            arcade.draw_lbwh_rectangle_filled(0  ,5, self.barre_width * ratio, self.barre_height, color = (255,0,0))

            self.sprites.draw()

window = Window()
arcade.run()

plt.figure(figsize=(10, 6))
plt.plot(window.historique_malades, label="Malades", color='red', linewidth=2)
plt.plot(window.historique_sains, label="Sains", color='blue', linewidth=2)
# J'ai retiré l'accent ici pour que Matplotlib fonctionne correctement !
plt.plot(window.historique_vaccines, label="Vaccinés", color='green', linewidth=2)
plt.title("Évolution de l'épidémie au sein de la population")
plt.xlabel("Temps")
plt.ylabel("Nombre d'individus")
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.show()