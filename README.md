## Projet-AP-2025-BIS ##

# Commentaires sur les programmes :

    • Le premier programme à consiédrer est le pogramme de contamination le plus élémentaire, il s'agit du notebook epidemie_simple.py. Des agents se déplacent aléatoirement sur une carte, certains sont sains (bleus) et d'autres sont malades (rouges). Lors d'un contact entre une personne saine et un personne malade, il y a un risque de contamination selon une certaine probabilité PROBA_CONTAMINATION. Un graphique récapitule l'évolution des populations à la fermeture du programme. 

    • confinement.py reprend la base du programme précédent. Mais cette fois deux murs ont été ajoutés pour limiter les déplacements des boids et ainsi simuler un confinement en haut à gauche de l'écran. Une autre différence est que les boids malades à l'instant initial sont tous dans la zone confinée et non plus répartis aléatoirement sur le cadre. On observe alors que la garnde majorité de la population malade reste dans le cadre prévu à cet effet, ce qui limite la propagation de l'épidémie.

    • barre_simulation.py est plus complexe. Nous avons ajouté des obstacles (batiments blancs générés aléatoirement) pour modifier davantage les trajectoires des boids et des carrés verts qui sont des zones de soins. Il y a également un curseur qui permet de suivre la proportion des populations malades et saines en direct.

    • vaccination.py reprend le concept de barre_simulation en l'améliorant. Lorsqu'un boid malade atteint une zone de soin il reste bloqué quelques temps (le temps nécessaire pour se faire soigner), puis il quitte cette zone en étant vacciné donc immunisé contre la maladie. Il est alors de couleur verte. 

    • 





# Commentaires sur l'élaboration du code et l'utilisation de l'IA générative: #

Nous sommes repartis de la base du TP sur le mouvement de foule des Boids, d'où la strucuture avec deux classes (boid et window) et l'utilisation d'arcade pour la vidéo.
Nous avons principalement tout codé à la main et l'IA sert juste à débugger quelques problèmes lorsque que nos fonctions ne marchent pas comme prévues.
Gemini nous a notamment permis d'introduire la liste_boids dans la classe boid pour que chaque personne aie "conscience" de son entourage et qu'on puisse ensuite faire fonctionner la fonction contac_boid que nous avions coder auparavant. Mais cette fonction test_contacte (qui est commentée au début du code) était trop lourde en calcul, Gemini nous a donc lui même suggéré la version qu'on utilise maintenant.

Pour les collisions entre personnes, nous avons d'abord créé une fonction collision dans la class boids pour savoir si deux personnes étaient en contact avec la fonction isclose du module maths comme on l'avait vu en cours. A partir de là, une fonction update_collision a été créée pour mettre à jour la position de toutes les personnes à chaque instant. Pour cela, il a fallu créer une fonction projection pour changer la trajectoire des boids, qui était inspiré d'une fonction que certains d'entre nous avions eu à utiliser lors de l'hackaton. Le seul problème étant que comme les rayons des cercles sont petits, le changement de trajectoire n'est pas toujours flagrant. 

Pour le cas des contaminations, on introduit une probabilité de contamination quand deux personnes rentrent en contact, et que l'un d'eux est malade. Si c'est le cas, on génére un nombre aléatoire pour savoir si la personne est contaminée et dans ce cas, son état devient True pour malade et la couleur de la personne devient rouge. Le problème que l'on a observé est le suivant: nous voulions que la contamination soit possible même sans contact, mais à ce moment-là, la contamination était quasiment automatique même avec une probabilité faible car le test se faisait plusieurs fois (tant que la personne était dans le rayon de contamination). 

Il est impossible d'ajouter un graphique qui trace en temps réel l'évolution des populations car cela fait crasher python, nous nous sommes donc contenter d'un graphique apparaissant à la fin de la simulation. On a néanmoins rajouté une barre suivant la proportion de personnes malades en direct 