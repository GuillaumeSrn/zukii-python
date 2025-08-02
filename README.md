# 🚀 Zukii Analysis Service - MVP

Micro-service d'analyse IA simplifié pour fichiers CSV avec intégration OpenAI GPT.

## 📋 Fonctionnalités MVP

### 🧠 Analyse IA
- **Intégration OpenAI GPT** : Analyse intelligente de données CSV
- **Analyse simplifiée** : Génération d'insights et recommandations
- **Graphiques JSON** : Données de graphiques pour intégration frontend
- **Anonymisation basique** : Protection des données sensibles

### ⚡ Performance
- **Service simplifié** : Code optimisé pour MVP
- **Gestion d'erreurs** : Récupération gracieuse
- **Validation basique** : Vérification des fichiers CSV

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   NestJS API    │    │  Python Service │
│   Angular       │───▶│   Backend       │───▶│   FastAPI       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   OpenAI GPT    │
                                              │   API           │
                                              └─────────────────┘
```

## 🚀 Installation

### Prérequis
- Python 3.11+
- Docker (optionnel)
- Clé API OpenAI

### Installation locale

1. **Cloner le repository**
```bash
cd zukii-python
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration**
```bash
cp env.example .env
# Éditer .env avec vos paramètres
```

5. **Lancer le service**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Installation Docker

1. **Construire l'image**
```bash
docker build -t zukii-analysis .
```

2. **Lancer le conteneur**
```bash
docker run -p 8000:8000 --env-file .env zukii-analysis
```

## 📚 API Documentation

### Endpoints principaux

#### `POST /api/v1/analyze`
Analyse de fichiers CSV avec question personnalisée.

**Paramètres :**
- `files` : Fichiers CSV (multipart)
- `question` : Question d'analyse
- `analysis_type` : Type d'analyse (défaut: "general")
- `include_charts` : Inclure des graphiques (défaut: true)
- `anonymize_data` : Anonymiser les données (défaut: true)

**Réponse :**
```json
{
  "analysis_id": "uuid",
  "summary": "Résumé de l'analyse",
  "key_insights": [...],
  "charts": [...],
  "processing_time": 1.23
}
```

#### `GET /`
Point d'entrée principal avec informations du service.

#### `GET /api/v1/health`
Vérification de santé du service.

#### `GET /api/v1/capabilities`
Capacités du service.

## 🔧 Configuration

Variables d'environnement dans `.env` :

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.3
```

## 🧪 Tests

```bash
pytest tests/
```

## 📝 Notes MVP

- **Service simplifié** : Code optimisé pour MVP
- **Graphiques JSON** : Données structurées pour frontend
- **Anonymisation basique** : Protection RGPD simplifiée
- **Performance** : Optimisé pour rapidité de développement