# Zukii Analyse Service

Microservice Python pour l'analyse automatisée de fichiers CSV dans le cadre du projet Zukii.

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://github.com/Wishk6/zukii-python/actions/workflows/ci.yml/badge.svg)](https://github.com/Wishk6/zukii-python/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
git clone https://github.com/Wishk6/zukii-python.git
cd zukii-analyse-service

text

2. Créer un environnement virtuel :
python -m venv venv
source venv/bin/activate # Linux/Mac

ou .\venv\Scripts\activate # Windows
text

3. Installer les dépendances :
pip install -r requirements.txt

text

### Configuration

Créer un fichier `.env` à la racine :
OPENAI_API_KEY=ta-clé-api
JWT_SECRET_KEY=secret-key-1234

text

## Utilisation

### Lancer le service localement
python app/main.py

text

### Endpoints API

**Analyse basique**
curl -X POST -F "file=@/chemin/vers/fichier.csv" http://localhost:5000/analyse

text

**Analyse avec OpenAI**
curl -X POST -F "file=@/chemin/vers/fichier.csv" http://localhost:5000/analyse/advanced

text

### Avec Docker
docker build -t zukii-analyse .
docker run -p 5000:5000 --env-file .env zukii-analyse

text

## Structure du projet
zukii-analyse-service/
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

text

## Développement

### Exécuter les tests
pytest tests/ -v

text

### Formatage du code
black .

text

### Vérification linting
flake8 .

text

## Contribution

1. Forker le projet
2. Créer une branche (`git checkout -b feature/ma-fonctionnalité`)
3. Commiter les changements (`git commit -m 'Ajout d'une super fonctionnalité'`)
4. Pusher la branche (`git push origin feature/ma-fonctionnalité`)
5. Ouvrir une Pull Request

## Licence

Distribué sous licence MIT. Voir `LICENSE` pour plus d'informations.

## Auteurs

- [Guillaume Saurin](https://github.com/Wishk6)

---

> **Note** : Ce service fait partie de l'écosystème Zukii. Voir le [dépôt principal](https://github.com/Wishk6/zukii-python) pour l'architecture globale.