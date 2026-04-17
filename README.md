# ColorStudio - SAE Maintenance Logicielle 2026

Projet de maintenance, modernisation et évolution de l'application ColorStudio dans le cadre de la SAE de BUT3 Informatique (Parcours A).

## Auteurs
* KARAMI Anir
* ARABAH Yanis

## Description du projet
ColorStudio est un outil de compositing basé sur la fusion dynamique des sources lumineuses. L'application permet d'ajuster en temps réel la couleur, l'exposition et la position de lampes le long de trajectoires prédéfinies pour recomposer l'éclairage d'une scène 3D.

Cette version 2026 apporte les modernisations suivantes :
* Migration complète de PyQt5 vers PyQt6.
* Compatibilité avec Python 3.12 et 3.13.
* Utilisation de QOpenGLWidget pour l'affichage du nuage de points 3D.
* Suppression de la bibliothèque obsolète easygui au profit de QFileDialog.
* Pipeline de post-traitement complet : Balance des blancs (AWB), Exposition automatique (AE), Saturation/Vibrance et Correction Gamma.
* Sauvegarde et chargement interactifs de configurations complètes (lampes et post-traitements) via fichiers XML.
* Correction du bug de référence d'attribut (ImagesArray) lors de l'export XML.
* Corrections de bugs de calcul dans les post-traitements (PPClip).

## Installation

### Prérequis
* Python 3.12 ou supérieur.
* Le dossier `images` de rendu (ex: `images/museum2x2`) placé à la racine.

### Configuration
```bash
# Configuration de l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt
```

## Utilisation

Pour lancer l'application :
```bash
python colorStudioApp.py
```
Sélectionnez ensuite un fichier de configuration XML (ex: `xml-2019-6-7-22-47-1.xml`) à l'ouverture.

## Tests
Pour exécuter la suite de tests unitaires :
```bash
python -m unittest test_color_studio.py
```
