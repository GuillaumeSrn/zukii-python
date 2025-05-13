# Zukii Analyse Service

Microservice Python pour l'analyse automatisée de fichiers CSV dans le cadre du projet Zukii.

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://github.com/Wishk6/zukii-python/actions/workflows/ci.yml/badge.svg)](https://github.com/Wishk6/zukii-python/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
## Fonctionnalités

- Analyse statistique de fichiers CSV
- Intégration avec OpenAI pour des insights avancés
- API REST sécurisée (JWT)
- Monitoring avec Prometheus/Grafana
- Hébergement Docker-ready

## Prérequis

- Python 3.10+
- Docker (optionnel)
- OpenAI API Key (optionnel)

## Installation

### Environnement local

1. Cloner le dépôt :
````bash
git clone https://github.com/Wishk6/zukii-python.git
cd zukii-analyse-service</code>
````
2. Créer un environnement virtuel :
````bash
python -m venv venv
source venv/bin/activate # Linux/Mac
````
ou 
````bash
.\venv\Scripts\activate # Windows
````

3. Installer les dépendances :
````bash
pip install -r requirements.txt
````
### Configuration

Créer un fichier `.env` à la racine :
````text
OPENAI_API_KEY=ton-api-key-openai
JWT_SECRET_KEY=secret-key-1234
````

## Utilisation

### Lancer le service localement
````bash
python app/main.py
````
### Endpoints API

**Analyse basique**
```` bash
curl -X POST -F "file=@/chemin/vers/fichier.csv" http://localhost:5000/analyse
````
```` bash
**Analyse avec OpenAI**
curl -X POST -F "file=@/chemin/vers/fichier.csv" http://localhost:5000/analyse/advanced
````
### Avec Docker
```` bash
docker build -t zukii-analyse .
docker run -p 5000:5000 --env-file .env zukii-analyse
````
## Structure du projet
````text
zukii-python-ms/
├── app/
│ ├── init.py
│ ├── main.py # Point d'entrée Flask
│ └── analyse.py # Logique d'analyse
├── tests/
│ └── test_analyse.py # Tests unitaires
├── requirements.txt
├── Dockerfile
└── .github/
└── workflows/
└── ci.yml # Intégration continue
````
## Développement

### Exécuter les tests
```` bash
pytest tests/ -v
````
### Formatage du code
```` bash
black .
````
### Vérification linting
```` bash
flake8 .
````
## Contribution souhaitée

1. Forker le projet
2. Créer une branche (`git checkout -b feature/ma-fonctionnalité`)
3. Commiter les changements (`git commit -m 'Ajout d'une super fonctionnalité'`)
4. Pusher la branche (`git push origin feature/ma-fonctionnalité`)
5. Ouvrir une Pull Request


## Auteurs

- [Guillaume Saurin](https://github.com/Wishk6)

---

> **Note** : Ce service fait partie de l'écosystème Zukii. Voir le [dépôt principal](https://github.com/Wishk6/zukii-python) pour l'architecture globale.