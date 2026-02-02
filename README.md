# 🤖 Bot d'Arbitrage Crypto - Automatisé

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-en%20développement-yellow.svg)]()

## 📋 Description

Système automatisé d'arbitrage de crypto-monnaies qui détecte et exploite les différences de prix entre différents exchanges en temps réel.

**⚠️ ATTENTION:** Ce projet est en développement. Utilisez uniquement en mode testnet ou avec de très petits montants.

## 🎯 Objectifs

- ✅ Détecter automatiquement les opportunités d'arbitrage
- ✅ Exécuter des trades de manière automatisée et sécurisée
- ✅ Gérer les risques avec des limites strictes
- ✅ Monitoring en temps réel
- ✅ Alertes instantanées

## 🏗️ Architecture

```
projet_arbitrage/
│
├── config/                 # Fichiers de configuration
├── src/                    # Code source principal
│   ├── connectors/        # Connexions aux exchanges
│   ├── collectors/        # Collection de données
│   ├── analyzers/         # Analyse des opportunités
│   ├── validators/        # Validation (liquidité, etc.)
│   ├── risk/              # Gestion des risques
│   ├── execution/         # Exécution des trades
│   ├── monitoring/        # Dashboards et métriques
│   ├── notifications/     # Alertes (Telegram, etc.)
│   ├── reporting/         # Génération de rapports
│   └── utils/             # Utilitaires
├── logs/                   # Fichiers de logs
├── tests/                  # Tests unitaires et d'intégration
├── data/                   # Données (historique, cache)
├── requirements.txt        # Dépendances Python
├── .env.template          # Template des variables d'environnement
└── README.md              # Ce fichier

```

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- PostgreSQL 14+
- Redis (optionnel, mais recommandé)
- Git

### Étape 1: Cloner le projet

```bash
git clone https://github.com/votre-username/projet-arbitrage.git
cd projet-arbitrage
```

### Étape 2: Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Étape 3: Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 4: Configuration

1. Copier le template de configuration:
```bash
cp .env.template .env
```

2. Éditer `.env` avec vos paramètres:
```bash
nano .env  # ou votre éditeur préféré
```

3. **IMPORTANT:** Configurer d'abord en mode testnet!

### Étape 5: Initialiser la base de données

```bash
# Créer la base de données PostgreSQL
createdb arbitrage_db

# Les tables seront créées automatiquement au premier lancement
```

## ⚙️ Configuration

### Variables d'environnement essentielles

Éditer le fichier `.env`:

```bash
# Mode de fonctionnement
ENVIRONMENT=development
DRY_RUN_MODE=true  # IMPORTANT: Toujours true pour commencer

# Clés API (utiliser TESTNET d'abord!)
BINANCE_API_KEY=votre_clé_testnet
BINANCE_API_SECRET=votre_secret_testnet
BINANCE_TESTNET=true

# Base de données
DATABASE_URL=postgresql://arbitrage_user:password@localhost:5432/arbitrage_db

# Paramètres de trading
MIN_TRADE_AMOUNT=10
MAX_TRADE_AMOUNT=100
MIN_PROFIT_THRESHOLD=0.5
```

### Obtenir des clés API Testnet

**Binance Testnet:**
1. Aller sur https://testnet.binance.vision/
2. Créer un compte
3. Générer des clés API
4. Obtenir des fonds de test gratuits

**Kraken:**
1. Créer un compte sur Kraken
2. Activer l'API (sans permissions de retrait)
3. Générer les clés

## 🎮 Utilisation

### Lancement en mode Dry-Run (Simulation)

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Lancer le bot en simulation
python main.py --dry-run
```

### Lancement en mode Production

**⚠️ NE PAS utiliser avant d'avoir testé en dry-run pendant au moins 7 jours!**

```bash
# Modifier .env: DRY_RUN_MODE=false
python main.py
```

### Commandes utiles

```bash
# Vérifier la configuration
python main.py --check-config

# Tester les connexions aux exchanges
python main.py --test-connections

# Afficher le dashboard
python main.py --dashboard

# Générer un rapport
python main.py --report daily
```

## 📊 Monitoring

### Dashboard Console

Le bot affiche en temps réel:
- Statut du système
- Opportunités détectées
- Trades exécutés
- Profit/Perte du jour
- Dernières erreurs

### Interface Web (Optionnel)

```bash
# Activer dans .env: ENABLE_WEB_INTERFACE=true
python main.py --web
```

Accéder via: http://localhost:5000

### Alertes Telegram

Configurer dans `.env`:
```bash
TELEGRAM_BOT_TOKEN=votre_token
TELEGRAM_CHAT_ID=votre_chat_id
```

Vous recevrez des alertes pour:
- Opportunités importantes
- Trades exécutés
- Erreurs critiques
- Rapport quotidien

## 🔒 Sécurité

### Best Practices

1. **Ne JAMAIS commiter le fichier `.env`**
2. **Utiliser des clés API avec permissions minimales:**
   - ✅ Trading/Lecture
   - ❌ Retrait de fonds
3. **Activer l'authentification 2FA** sur tous les exchanges
4. **Utiliser le testnet** pour tous les tests
5. **Commencer avec de très petits montants** (10-20€ max)
6. **Sauvegarder régulièrement** la base de données

### Limites de Risque

Configurées dans `.env`:
- Montant max par trade
- Nombre max de trades quotidiens
- Perte max quotidienne
- Circuit breaker automatique

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
pytest

# Avec coverage
pytest --cov=src

# Tests spécifiques
pytest tests/test_connectors.py
```

### Tests de validation

```bash
# Test de connexion aux exchanges
python tests/test_exchange_connection.py

# Test de détection d'opportunités
python tests/test_opportunity_detection.py

# Test end-to-end
python tests/test_e2e_dry_run.py
```

## 📈 Métriques et Performance

### KPIs suivis

- **ROI (Return on Investment)**
- **Win Rate** - % de trades profitables
- **Profit Factor** - Ratio gains/pertes
- **Latence moyenne** - Temps détection → exécution
- **Uptime** - Disponibilité du système

### Rapports automatiques

- Quotidien (envoyé chaque soir)
- Hebdomadaire (le dimanche)
- Mensuel (1er du mois)

## 🗺️ Roadmap

### Version 1.0 (Actuelle) - MVP
- [x] Configuration de base
- [ ] Connexion à 2 exchanges
- [ ] Détection d'arbitrage simple
- [ ] Mode dry-run
- [ ] Gestion des risques basique
- [ ] Monitoring console

### Version 2.0 - Optimisation
- [ ] Arbitrage triangulaire
- [ ] 5+ exchanges
- [ ] WebSockets temps réel
- [ ] Interface web
- [ ] Machine Learning basique

### Version 3.0 - Avancé
- [ ] Stratégies multiples
- [ ] Backtesting complet
- [ ] Auto-optimisation des paramètres
- [ ] API publique
- [ ] Support multi-devises

## 🤝 Contribution

Ce projet est personnel mais les suggestions sont bienvenues:

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📝 Changelog

### [En cours] - 2026-01-19
- Initialisation du projet
- Configuration de base
- Documentation

## ⚖️ Licence

MIT License - Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## ⚠️ Disclaimer

**Ce projet est fourni "tel quel", à des fins éducatives uniquement.**

- Le trading de crypto-monnaies comporte des risques importants
- Vous pouvez perdre tout votre capital
- Testez TOUJOURS en mode testnet d'abord
- L'auteur n'est pas responsable des pertes financières
- Utilisez à vos propres risques

## 📞 Support

- **Issues:** https://github.com/votre-username/projet-arbitrage/issues
- **Discussions:** https://github.com/votre-username/projet-arbitrage/discussions

## 🙏 Remerciements

- [CCXT](https://github.com/ccxt/ccxt) - Pour l'excellente bibliothèque d'API unifiée
- La communauté crypto pour le partage de connaissances
- Tous les contributeurs

---

**Fait avec ❤️ pour l'apprentissage du trading algorithmique**

*Dernière mise à jour: 19 janvier 2026*
