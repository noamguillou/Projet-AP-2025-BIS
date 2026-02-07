import arcade
import math
import random
import matplotlib.pyplot as plt

BACKGROUND = arcade.color.ALMOND
PROBA_MALADIE = 0.1
PROBA_CONTAMINATION = 0.1
TEMPS_GUÉRISON = 500
COULEUR_MUR = arcade.color.DARK_GRAY
COULEUR_VACCIN_VISUEL = arcade.color.LIME_GREEN

def distance(p1,p2) : 
    return math.sqrt( (p1.center_x - p2.center_x)**2 + (p1.center_y - p2.center_y)**2 )

def contamination(personne_en_contacte, p_contamination) : 
    (p1,p2)= personne_en_contacte 
    if p1.etat == True and p2.etat == False : 
        if random.random() < p_contamination : 
            p2.etat = True
    elif p2.etat == True and p1.etat == False : 
        if random.random() < p_contamination : 
            p1.etat = True

class Boid(arcade.SpriteCircle):
    def __init__(self, position_x: float, position_y: float, angle: float, liste_boids, liste_murs, etat: bool = False, speed: float = 1.0, temps_malade: int = 0):
        super().__init__(5, arcade.color.BLUE, False)
        self.center_x = position_x
        self.center_y = position_y
        self.angle = angle
        self.speed = speed
        self.etat = etat
        self.voisins = liste_boids
        self.liste_murs = liste_murs 
        self.temps_malade = temps_malade

    def angle_radian(self):
        return self.angle / 180 * math.pi

    # NOUVELLE FONCTION DE DEPLACEMENT ROBUSTE
    def deplacement_intelligent(self):
        # 1. Calcul de la vitesse vectorielle
        dx = math.cos(self.angle_radian()) * self.speed
        dy = math.sin(self.angle_radian()) * self.speed

        # --- AXE X ---
        self.center_x += dx
        if len(arcade.check_for_collision_with_list(self, self.liste_murs)) > 0:
            self.center_x -= dx # Retour arrière
            self.angle = 180 - self.angle # Rebond X
            # Mise à jour des vitesses pour la suite du mouvement
            dx = math.cos(self.angle_radian()) * self.speed
            dy = math.sin(self.angle_radian()) * self.speed

        # --- AXE Y ---
        self.center_y += dy
        if len(arcade.check_for_collision_with_list(self, self.liste_murs)) > 0:
            self.center_y -= dy # Retour arrière
            self.angle = -self.angle # Rebond Y

        self.angle %= 360

    def contact_bord(self):
        if self.center_x >= 795  or self.center_x <= 5 : 
            self.angle = 180 - self.angle
        if self.center_y >= 795 or self.center_y <= 5 :
            self.angle = -self.angle

    def contact_boid(self):
        rayon_personne = 5
        for autre in self.voisins:
            if autre is not self:  
                if distance(self, autre) < 2 * rayon_personne:
                    self.angle = -self.angle + 180
                    # On ajoute un petit "push" pour éviter qu'ils collent entre eux aussi
                    self.center_x += math.cos(self.angle_radian()) * self.speed
                    self.center_y += math.sin(self.angle_radian()) * self.speed
                    break

    def je_suis_malade(self):
        if self.etat == True :
            self.color = arcade.color.RED
            self.temps_malade += 1
    
    def je_suis_guéri(self):
        if self.temps_malade >= TEMPS_GUÉRISON :
            self.etat = False
        if self.etat == False :
            self.color = arcade.color.BLUE
            self.temps_malade = 0

    def contact_malade(self):
        rayon_personne = 5
        for autre in self.voisins:
            if autre is not self:  
                if distance(self, autre) < 2 * rayon_personne:
                    contamination((self,autre), PROBA_CONTAMINATION)
                    break

    def contact_vaccin(self, liste_zones_vaccin):
        # On regarde si on touche une zone de la liste
        if len(arcade.check_for_collision_with_list(self, liste_zones_vaccin)) > 0:
            self.etat = False       # On n'est plus malade
            self.temps_malade = 0   # On remet le compteur à 0
            self.color = arcade.color.BLUE # On reprend sa couleur normale
            # Optionnel : Tu pourrais ajouter self.immunise = True ici si tu veux qu'il ne retombe jamais malade

class Window(arcade.Window):

    def __init__(self):
        super().__init__(800, 800, "Simulation Épidémie avec Murs")
        arcade.set_background_color(BACKGROUND)
        self.set_location(800, 100)
        self.historique_sains = []
        self.historique_malades = []
        self.temps = 0

        # Murs
        self.liste_murs = arcade.SpriteList()
        for _ in range(10):
            w = random.randint(50, 200)
            h = random.randint(50, 200)
            x = random.randint(w//2 + 10, 800-w//2 - 10)
            y = random.randint(h// 2 + 10, 800-h//2 - 10)
            mur = arcade.SpriteSolidColor(w, h, COULEUR_MUR)
            mur.center_x = x
            mur.center_y = y
            self.liste_murs.append(mur)

# Zones de vaccination
        self.liste_vaccins = arcade.SpriteList()
        nb_zones_placees = 0
        
        # On boucle TANT QU'ON n'a pas placé 3 zones
        while nb_zones_placees < 3:
            w = 50
            h = 60
            x = random.randint(w, 800 - w)
            y = random.randint(h, 800 - h)
            
            zone = arcade.SpriteSolidColor(w, h, arcade.color.TRANSPARENT_BLACK)            
            zone.center_x = x
            zone.center_y = y
            
            # Si ça ne touche pas un mur, on l'ajoute
            if len(arcade.check_for_collision_with_list(zone, self.liste_murs)) == 0:
                self.liste_vaccins.append(zone)
                nb_zones_placees += 1 # On compte +1 seulement si c'est réussi

        # Boids
        N = 150 
        self.boids =[]
        for k in range(N):
            placed = False
            while not placed:
                x_pos, y_pos = random.randint(5, 795), random.randint(5, 795)
                ang = random.randint(0, 360)
                nouveau_boid = Boid(x_pos, y_pos, ang, self.boids, self.liste_murs, False, temps_malade=0)
                if len(arcade.check_for_collision_with_list(nouveau_boid, self.liste_murs)) == 0:
                    self.boids.append(nouveau_boid)
                    placed = True
                
        # Patients zéros
        for i in range(int(PROBA_MALADIE*len(self.boids))) :
            k = random.randint(0, len(self.boids)-1)
            self.boids[k].etat = True

        self.sprites = arcade.SpriteList()
        for boid in self.boids:
            self.sprites.append(boid)

    

    def on_update(self, delta_time):
        nb_sains = 0
        nb_malades = 0

        for boid in self.boids:
            # MODIFICATION ICI : On utilise la nouvelle fonction 
            boid.deplacement_intelligent()
            
            boid.contact_bord()
            boid.contact_boid()
            boid.je_suis_malade()
            boid.contact_malade()
            boid.je_suis_guéri()
            boid.contact_vaccin(self.liste_vaccins)
            
            if boid.etat == True:
                nb_malades += 1
            else:
                nb_sains += 1
        
        self.historique_sains.append(nb_sains)
        self.historique_malades.append(nb_malades)
        
        self.sprites.update()

    def on_draw(self):
            self.clear()
            self.liste_murs.draw()

            nb_sains = self.historique_sains[-1]
            nb_malades = self.historique_malades[-1]


            ratio = nb_malades/(nb_sains + nb_malades)

            # DESSIN MANUEL DES 4 LIGNES POUR CHAQUE ZONE
            for zone in self.liste_vaccins:
                # 1. On calcule les coins
                gauche = zone.center_x - (zone.width / 2)
                droite = zone.center_x + (zone.width / 2)
                haut   = zone.center_y + (zone.height / 2)
                bas    = zone.center_y - (zone.height / 2)
                
                # 2. On dessine les 4 traits (Haut, Bas, Gauche, Droite)
                # draw_line(x_début, y_début, x_fin, y_fin, couleur, épaisseur)
                
                # Trait du haut
                arcade.draw_line(gauche, haut, droite, haut, COULEUR_VACCIN_VISUEL, 2)
                # Trait du bas
                arcade.draw_line(gauche, bas, droite, bas, COULEUR_VACCIN_VISUEL, 2)
                # Trait de gauche
                arcade.draw_line(gauche, bas, gauche, haut, COULEUR_VACCIN_VISUEL, 2)
                # Trait de droite
                arcade.draw_line(droite, bas, droite, haut, COULEUR_VACCIN_VISUEL, 2)

            #Ajout d'une barre en temps réel
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
plt.title("Évolution de l'épidémie au sein de la population")
plt.xlabel("Temps")
plt.ylabel("Nombre d'individus")
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.show()

#"rg"rg