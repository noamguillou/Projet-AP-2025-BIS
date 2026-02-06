import arcade
import math
import random
import matplotlib.pyplot as plt

BACKGROUND = arcade.color.ALMOND
PROBA_MALADIE = 0.1
PROBA_CONTAMINATION = 0.1
TEMPS_GUÉRISON = 500

# Fonction pour calculer la distance entre deux boids
def distance(p1,p2) : 
    return math.sqrt( (p1.center_x - p2.center_x)**2 + (p1.center_y - p2.center_y)**2 )

# Fonction pour gérer la contamination entre les boids en contact
def contamination(personne_en_contacte, p_contamination) : 
    (p1,p2)= personne_en_contacte 
    if p1.etat == True and p2.etat == False : 
        if random.random() < p_contamination : 
            p2.etat = True
    elif p2.etat == True and p1.etat == False : 
        if random.random() < p_contamination : 
            p1.etat = True

#def test_contacte(liste_personnes, rayon_personne) : 
#    personnes_en_contacte = []
#    for i in range (len (liste_personnes)) : 
#       for j in range (i+1, len (liste_personnes)) : 
#           if distance (liste_personnes[i], liste_personnes[j]) < 2*rayon_personne : 
#                personnes_en_contacte.append ( (liste_personnes[i], liste_personnes[j]) )
#    return personnes_en_contacte 



class Boid(arcade.SpriteCircle):
    def __init__(self, position_x: float, position_y: float, angle: float, liste_boids, etat: bool = False, speed: float = 1.0, temps_malade: int = 0):
        super().__init__(5, arcade.color.BLUE, False)
        self.center_x = position_x
        self.center_y = position_y
        self.angle = angle
        self.speed = speed
        self.etat = etat
        self.voisins = liste_boids
        self.temps_malade = temps_malade

    # Fonction qui assure un déplacement rectiligne des boids
    def move(self):
       self.center_x += math.cos(self.angle_radian()) * self.speed
       self.center_y += math.sin(self.angle_radian()) * self.speed

    # Conversion de l'angle du boid en radians pour les fonctions trigonométriques
    def angle_radian(self):
        return self.angle / 180 * math.pi
    
    # Fonction pour maintenir les boids à l'intérieur de la fenêtre
    def contact_bord(self):
        if self.center_x >= 795  or self.center_x <= 5 : 
            self.angle = 180 - self.angle
        if self.center_y >= 795 or self.center_y <= 5 :
            self.angle = -self.angle

    # Fonction pour gérer les collisions entre les boids
    def contact_boid(self):
        rayon_personne = 5
        for autre in self.voisins:
            if autre is not self:  
                if distance(self, autre) < 2 * rayon_personne:
                    self.angle = -self.angle + 180
                    self.center_x += math.cos(self.angle_radian()) * self.speed
                    self.center_y += math.sin(self.angle_radian()) * self.speed
                    break

    #test pour vérifier si les personnes sont suffisamment proche pour se contaminer
    def test_proximité(self,p2):
        return distance(self,p2)<10
    
    # Fonction pour déterminer l'état de santé du patient
    def je_suis_malade(self):
        if self.etat == True :
            self.color = arcade.color.RED
            self.temps_malade += 1
    
    # Fonction pour déterminer si le patient est guéri après un certain temps
    def je_suis_guéri(self):
        if self.temps_malade >= TEMPS_GUÉRISON :
            self.etat = False
        if self.etat == False :
            self.color = arcade.color.BLUE
            self.temps_malade = 0

    def contact(self, x, y):
        return math.isclose(self.center_x,x) and math.isclose(self.center_y,y)
    
    def proj(self, x,y) :# inspiré de l'hackaton
        px = min(max(x, self.center_x), self.center_x )
        py = min(max(y, self.center_y), self.center_y )
        return px, py
    
    def contact_malade(self):
        rayon_personne = 5
        for autre in self.voisins:
            if autre is not self:  
                if distance(self, autre) < 2 * rayon_personne:
                    contamination((self,autre), PROBA_CONTAMINATION)
                    break
    
class Window(arcade.Window):

    def __init__(self):
        super().__init__(800, 800, "My first boid")
        arcade.set_background_color(BACKGROUND)
        self.set_location(800, 100)
        self.historique_sains = []
        self.historique_malades = []
        self.temps = 0

        # Initialisation de la liste des boids
        N = 150  # Nombre de boids
        self.boids =[]
        for k in range(N):
            x_pos, y_pos, ang = random.randint(5, 795),random.randint(5, 795),random.randint(0, 360)
            self.boids.append(Boid(x_pos, y_pos, ang, self.boids, False, temps_malade=0))
        # Iniatialisation de l'état de maladie de certains boids : "les patients zéros"
        for i in range(int(PROBA_MALADIE*len(self.boids))) :
            k = random.randint(0, len(self.boids)-1)
            self.boids[k].etat = True

        self.sprites = arcade.SpriteList()
        for boid in self.boids:
            self.sprites.append(boid)

    def on_draw(self):
        self.clear()
        self.sprites.draw()

    def on_update(self, delta_time):
        nb_sains = 0
        nb_malades = 0
# dfvd
        for boid in self.boids:
            boid.move()
            boid.contact_bord()
            boid.contact_boid()
            boid.je_suis_malade()
            boid.contact_malade()
            boid.je_suis_guéri()
            
            # on compte pour le graphique à la fin
            if boid.etat == True:
                nb_malades += 1
            else:
                nb_sains += 1
        # listes qui serviront à tracer le graphique de l'évolution de l'épidémie
        self.historique_sains.append(nb_sains)
        self.historique_malades.append(nb_malades)
        
        self.sprites.update()

window = Window()
arcade.run()

# Tracé du graphique de l'évolution de l'épidémie
plt.figure(figsize=(10, 6))
plt.plot(window.historique_malades, label="Malades", color='red', linewidth=2)
plt.plot(window.historique_sains, label="Sains", color='blue', linewidth=2)
plt.title("Évolution de l'épidémie au sein de la population")
plt.xlabel("Temps")
plt.ylabel("Nombre d'individus")
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.show()

