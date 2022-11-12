# Compilo
Project aiming at building our own mini-c language using Python

UPDATE : Utilisation de notre projet avec le Makefile : il suffit désormais de taper "make run <nom du fichier texte écrit en mini-c> <arguments>" (exemple "make run programme.txt 1 2 3"). Attention : il n'est pas possible dans ce cas d'utiliser des nombres négatifs en argument car nous n'avons pas réussi à dire à l'invité de commande de les lire comme tels. Cependant après avoir exécuté une commande qui fonctionne, cela crée un fichier a.out que vous pourrez ensuite exécuter avec des entiers relatifs (exemple "./a.out -1 -2 -3)

Travail de Simon et Valentin : Tableau - Opération Vectorielles
Introduction:
Notre compilateur permet de manipuler les tableaux et les opérations vectorielles, nous avons fait le choix de traiter à deux ces deux parties l’une après l’autre car il n’était pas possible de traiter les opérations vectorielles sans avoir traité les tableaux.
 
Comment sont structurés les tableaux:
Les composantes de nos tableaux sont forcément des entiers relatifs


Pour créer un tableau on utilise l’expression : int[entier] -> l’entier peut découler d’une expression , par exemple: ix = 3;  ty = int [ix+1]; crée un tableau de taille 4
Ce qui est réalisé: on calcul l’entier qui découle de l’expression entre les crochet , on réserve ensuite grâce à la fonction malloc de la mémoire dans le tas de la taille 8*la longueur du tableau + 8 octets pour stocker la longueur du tableau (8 premier octets).


on peut accéder aux éléments des tableaux de la manière suivante: tx[1], tx[ix+3] ect…
Convention: on suppose que l’utilisateur ne demande pas l’accès à un élément d’indice supérieur à la longueur -1
L’indexage se fait de 0 à longueur du tableau - 1


On peut accéder à la longueur du tableau grâce à l’ expression : len( expression correspondant à un tableau), exemple : len(tx) , len(tx concat ty)

Noms des variables:  une variable correspondant à un entier relatif doit commencer par le caractère “i” afin de pouvoir les distinguer des variables correspondant aux tableaux qui commence par un “t”  (il est tout à fait possible d’avoir deux variables ix et tx  qui n’ont rien à voir)

Opérations binaires: Nous disposions déjà de l’addition et la soustraction de deux entiers par exemple (ix + iy, ix - iy)  comme expressions dans notre langage.
Pour fonctionner ces opérations nécessitent que l’utilisateur respecte nos conventions 
Nous avons rajouté les opérations suivantes:

Multiplication d’entier:  ix * iy 

Multiplication des composantes d’un tableau par un entier:    ix mult ty 
(convention adoptée: le premier élément doit être un entier et le deuxième un tableau, l’ordre inverse ne fonctionnera pas)

Addition d’un entier à chacune des composante d’un vecteur: ix add ty
(convention adoptée: le premier élément doit être un entier et le deuxième un tableau, l’ordre inverse ne fonctionnera pas)

Soustraction d’un entier à chacune des composante d’un vecteur: ix sub ty
(convention adoptée: le premier élément doit être un entier et le deuxième un tableau, l’ordre inverse ne fonctionnera pas)

Multiplication terme à terme de deux vecteurs: tx times ty
(convention adoptée: les deux vecteurs doivent avoir la même longueur, sinon l’utilisateur peut multiplier un tableau tx plus petit que le tableau ty et cela donnera un nouveau tableau de la taille de tx)

Addition terme à terme de deux vecteurs:   tx sum ty
(convention adoptée: les deux vecteurs doivent avoir la même longueur, sinon idem que pour times)

Soustraction terme à terme de deux vecteurs: tx minus ty
Attention: le résultat est un vecteur dont la composante i est ty[i] -tx[i]
(convention adoptée: les deux vecteurs doivent avoir la même longueur + l'ordre indiqué ci dessus, sinon idem que times)

Concaténation de deux vecteurs:   tx concat ty

Nous nous sommes également lancé le défi de réaliser une opération vectorielle plus ambitieuse : un algorithme de tri 

Nous avons donc créé une commande qui effectue l’algorithme de tri sélection :  sort(tx)
Attention pas de ‘;’ à la fin.
Cette commande trie un tableau dans l'ordre croissant.
Pour écrire cet algorithme en assembleur, on a utilisé ce qui avait déjà été fait sur les boucles while et if. Nous sommes très fiers d’avoir réussi ce défi qui nous paraissait ambitieux au début du projet.

Affichage d’une variable : print
Cette commande avait déjà été réalisée en cours, mais elle n’était pas suffisante pour notre projet car elle ne permettait pas d’afficher un tableau et cette tâche pouvait vite devenir pénible à écrire dans notre langage, alors nous avons implémenté la commande tabletprint, qui affiche un à un chaque élément d’un tableau. Cela rend bien plus lisible un tableau et nous a permis un debugging bien plus efficace par moments


Enfin, nous avons donné la possibilité à l’utilisateur d’écrire son code en mini-c dans un fichier texte  plutôt que de l'écrire dans le fichier python.
Nous laissons à disposition dans le dépôt Git  des fichier texte exemples pour montrer le fonctionnement de notre compilo.
