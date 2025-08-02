# 🚀 Zukii Analysis Service

Micro-service d'analyse IA pour fichiers CSV avec intégration OpenAI GPT, visualisations Plotly et protection RGPD.

## 📋 Fonctionnalités

### 🧠 Analyse IA
- **Intégration OpenAI GPT** : Analyse intelligente de données CSV
- **Types d'analyse** : Général, tendances, corrélations, prédictions, statistiques
- **Insights automatiques** : Détection de patterns et anomalies
- **Recommandations** : Suggestions d'actions basées sur les données

### 📊 Visualisations
- **Graphiques Plotly** : Génération automatique de visualisations interactives
- **Types supportés** : Ligne, barres, dispersion, heatmap, histogramme, boîte, circulaire
- **Responsive** : Graphiques adaptatifs pour tous les écrans
- **Export JSON** : Données Plotly pour intégration frontend

### 🔒 Protection RGPD
- **Anonymisation automatique** : Détection et protection des données sensibles
- **Patterns de détection** : Emails, téléphones, SSN, cartes bancaires, etc.
- **Méthodes d'anonymisation** : Masking, hashing, mapping d'IDs
- **Rapport de conformité** : Documentation complète des traitements

### ⚡ Performance
- **Monitoring détaillé** : Métriques de performance et temps de réponse
- **Logging structuré** : Traçabilité complète des analyses
- **Gestion d'erreurs** : Récupération gracieuse et messages informatifs
- **Validation robuste** : Vérification des fichiers et données

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
Analyse un fichier CSV avec IA

**Paramètres :**
- `file` : Fichier CSV (max 50MB)
- `question` : Question d'analyse (10-1000 caractères)
- `analysis_type` : Type d'analyse (general, trends, correlations, predictions, statistical)
- `include_charts` : Inclure des graphiques (bool)
- `anonymize_data` : Anonymiser les données (bool)

**Exemple :**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@data.csv" \
  -F "question=Quelles sont les tendances dans ces données de ventes ?" \
  -F "analysis_type=trends" \
  -F "include_charts=true" \
  -F "anonymize_data=true"
```

#### `POST /api/v1/analyze/batch`
Analyse plusieurs fichiers CSV

**Paramètres :**
- `files` : Liste de fichiers CSV
- `question` : Question d'analyse
- `analysis_type` : Type d'analyse
- `include_charts` : Inclure des graphiques
- `anonymize_data` : Anonymiser les données

#### `GET /api/v1/health`
Vérification de santé du service

#### `GET /api/v1/capabilities`
Capacités et limitations du service

#### `POST /api/v1/validate`
Validation d'un fichier sans analyse

### Réponse d'analyse

```json
{
  "analysis_id": "uuid",
  "summary": "Résumé exécutif",
  "key_insights": [
    {
      "title": "Titre de l'insight",
      "description": "Description détaillée",
      "confidence": 0.85,
      "category": "trend",
      "supporting_data": {}
    }
  ],
  "anomalies": [
    {
      "type": "outlier",
      "description": "Description de l'anomalie",
      "severity": "medium",
      "affected_columns": ["col1"],
      "suggested_action": "Action recommandée"
    }
  ],
  "recommendations": [
    {
      "title": "Titre de la recommandation",
      "description": "Description détaillée",
      "priority": "high",
      "impact": "Impact attendu",
      "effort": "medium",
      "category": "data_quality"
    }
  ],
  "charts": [
    {
      "type": "line",
      "title": "Titre du graphique",
      "description": "Description du graphique",
      "data": {}, // Données Plotly JSON
      "config": {},
      "width": 600,
      "height": 400
    }
  ],
  "confidence_score": 0.85,
  "performance_metrics": {
    "processing_time": 2.5,
    "openai_tokens_used": 1500,
    "openai_response_time": 1.8,
    "chart_generation_time": 0.7
  },
  "privacy_report": {
    "anonymization_applied": true,
    "sensitive_columns_detected": ["email", "phone"],
    "data_retention_days": 30,
    "compliance_status": "compliant"
  },
  "data_summary": {
    "shape": {"rows": 1000, "columns": 5},
    "global_stats": {},
    "anomalies": {}
  }
}
```

## 🧪 Tests

### Lancer les tests
```bash
# Tests unitaires
pytest tests/

# Tests avec couverture
pytest tests/ --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_analysis_service.py -v
```

### Tests d'intégration
```bash
# Test de l'API
curl -X GET "http://localhost:8000/api/v1/health"
curl -X GET "http://localhost:8000/api/v1/capabilities"
```

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Clé API OpenAI | Requis |
| `OPENAI_MODEL` | Modèle GPT à utiliser | `gpt-4` |
| `OPENAI_MAX_TOKENS` | Nombre max de tokens | `2000` |
| `OPENAI_TEMPERATURE` | Température GPT | `0.3` |
| `ANONYMIZATION_ENABLED` | Activer l'anonymisation | `true` |
| `MAX_FILE_SIZE_MB` | Taille max des fichiers | `50` |
| `API_PORT` | Port du service | `8000` |
| `LOG_LEVEL` | Niveau de log | `INFO` |

### Configuration avancée

Le service utilise Pydantic Settings pour la configuration. Toutes les variables d'environnement sont automatiquement chargées depuis le fichier `.env`.

## 📊 Monitoring

### Logs structurés

Le service génère des logs JSON structurés pour faciliter l'analyse :

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "app.services.analysis_service",
  "message": "{\"event\": \"analysis_started\", \"analysis_id\": \"uuid\", \"user_id\": \"user123\", \"file_count\": 1, \"question\": \"Question d'analyse\"}"
}
```

### Métriques de performance

- Temps de traitement total
- Temps de réponse OpenAI
- Temps de génération des graphiques
- Nombre de tokens utilisés
- Utilisation mémoire

## 🔒 Sécurité

### Validation des fichiers
- Vérification du type MIME
- Validation de la taille
- Détection de contenu malveillant
- Nettoyage des noms de fichiers

### Protection des données
- Anonymisation automatique
- Chiffrement des données sensibles
- Rétention limitée
- Conformité RGPD

### API Security
- Validation des entrées
- Rate limiting
- CORS configuré
- Gestion d'erreurs sécurisée

## 🚀 Déploiement

### Docker Compose

```yaml
version: '3.8'
services:
  zukii-analysis:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zukii-analysis
spec:
  replicas: 3
  selector:
    matchLabels:
      app: zukii-analysis
  template:
    metadata:
      labels:
        app: zukii-analysis
    spec:
      containers:
      - name: zukii-analysis
        image: zukii-analysis:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
```

## 🤝 Intégration avec NestJS

### Endpoint NestJS

```typescript
// Dans le service NestJS
async analyzeFile(file: Express.Multer.File, question: string) {
  const formData = new FormData();
  formData.append('file', file.buffer, file.originalname);
  formData.append('question', question);
  formData.append('analysis_type', 'general');
  formData.append('include_charts', 'true');
  formData.append('anonymize_data', 'true');

  const response = await fetch('http://python-service:8000/api/v1/analyze', {
    method: 'POST',
    body: formData
  });

  return response.json();
}
```

## 📈 Roadmap

### Version 1.1
- [ ] Support des formats Excel (.xlsx, .xls)
- [ ] Templates d'analyse prédéfinis
- [ ] Cache Redis pour les analyses
- [ ] Métriques Prometheus

### Version 1.2
- [ ] Support des bases de données (PostgreSQL, MySQL)
- [ ] Analyses en temps réel
- [ ] Notifications webhook
- [ ] Interface d'administration

### Version 1.3
- [ ] Support multi-langues
- [ ] Analyses collaboratives
- [ ] Export PDF des rapports
- [ ] Intégration BI (Power BI, Tableau)

## 🐛 Support

### Problèmes connus
- Limitation OpenAI : 60 requêtes/minute
- Taille max fichier : 50MB
- Encodage : UTF-8 recommandé

### Debugging
```bash
# Mode debug
API_DEBUG=true python -m uvicorn app.main:app --reload

# Logs détaillés
LOG_LEVEL=DEBUG python -m uvicorn app.main:app
```

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📞 Contact

- **Email** : contact@zukii.com
- **Documentation** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Explorer** : [http://localhost:8000/redoc](http://localhost:8000/redoc)