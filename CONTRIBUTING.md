# Guide de Contribution

Merci de votre intérêt pour contribuer à ce projet de bot d'arbitrage crypto ! 🎉

Ce document vous guide à travers le processus de contribution.

---

## 📋 Table des Matières

- [Code de Conduite](#code-de-conduite)
- [Comment Contribuer](#comment-contribuer)
- [Structure du Projet](#structure-du-projet)
- [Standards de Code](#standards-de-code)
- [Tests](#tests)
- [Commits](#commits)
- [Pull Requests](#pull-requests)

---

## 🤝 Code de Conduite

En participant à ce projet, vous acceptez de:
- Être respectueux envers les autres contributeurs
- Accepter les critiques constructives
- Se concentrer sur ce qui est meilleur pour le projet

---

## 💡 Comment Contribuer

### Signaler un Bug

1. **Vérifiez** que le bug n'a pas déjà été signalé dans [Issues](https://github.com/Zermatt01/Arbitrage/issues)
2. **Créez une issue** avec:
   - Titre clair et descriptif
   - Description détaillée du problème
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Logs d'erreur (si applicable)
   - Environnement (OS, Python version, etc.)

**Template Bug Report:**
```markdown
**Description**
Description claire du bug

**Pour Reproduire**
1. Aller à '...'
2. Cliquer sur '...'
3. Voir l'erreur

**Comportement Attendu**
Ce qui devrait se passer

**Screenshots**
Si applicable

**Environnement**
- OS: [e.g. Windows 11]
- Python: [e.g. 3.10.5]
- Version du bot: [e.g. 0.5.0]
```

### Proposer une Fonctionnalité

1. **Créez une issue** avec le label `enhancement`
2. **Décrivez:**
   - Le problème que ça résout
   - La solution proposée
   - Les alternatives considérées
   - Impact sur le code existant

### Contribuer du Code

1. **Fork** le projet
2. **Créez une branche** depuis `main`:
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
3. **Committez** vos changements (voir [Standards de Commits](#commits))
4. **Poussez** vers votre fork:
   ```bash
   git push origin feature/ma-fonctionnalite
   ```
5. **Ouvrez une Pull Request**

---

## 🏗️ Structure du Projet

```
projet_arbitrage/
├── src/                    # Code source
│   ├── connectors/        # Connexions exchanges
│   ├── collectors/        # Collecte de données
│   ├── analyzers/         # Analyse opportunités
│   ├── validators/        # Validations
│   ├── risk/              # Gestion des risques
│   ├── execution/         # Exécution trades
│   ├── monitoring/        # Monitoring (à venir)
│   ├── notifications/     # Alertes (à venir)
│   ├── reporting/         # Rapports (à venir)
│   ├── database/          # Base de données
│   ├── models/            # Modèles SQLAlchemy
│   └── utils/             # Utilitaires
├── config/                 # Configuration
├── scripts/                # Scripts utilitaires
├── tests/                  # Tests
├── logs/                   # Logs (pas sur git)
└── data/                   # Données (pas sur git)
```

### Où Ajouter du Code

- **Nouveau connecteur exchange** → `src/connectors/`
- **Nouvelle stratégie d'arbitrage** → `src/analyzers/`
- **Nouveau validateur** → `src/validators/`
- **Utilitaire général** → `src/utils/`
- **Tests** → `tests/` (même structure que src/)

---

## ✨ Standards de Code

### Style Python

Suivre **PEP 8** avec quelques adaptations:

```python
# ✅ Bon
def calculate_profit(buy_price: float, sell_price: float, amount: float) -> float:
    """
    Calcule le profit d'un trade.
    
    Args:
        buy_price: Prix d'achat
        sell_price: Prix de vente
        amount: Montant tradé
    
    Returns:
        Profit en USD
    """
    return (sell_price - buy_price) * amount

# ❌ Mauvais
def calc(b,s,a):
    return (s-b)*a  # Pas de docstring, noms pas clairs
```

### Docstrings

**Obligatoire** pour:
- Classes
- Méthodes publiques
- Fonctions

Format Google Style:
```python
def ma_fonction(param1: str, param2: int) -> bool:
    """
    Description courte.
    
    Description longue si nécessaire avec plus de détails
    sur le fonctionnement.
    
    Args:
        param1: Description du paramètre 1
        param2: Description du paramètre 2
    
    Returns:
        True si succès, False sinon
    
    Raises:
        ValueError: Si param2 est négatif
    
    Example:
        >>> ma_fonction("test", 42)
        True
    """
    pass
```

### Type Hints

**Obligatoire** pour les signatures:
```python
from typing import Dict, List, Optional

def process_prices(
    prices: Dict[str, float],
    exchanges: List[str]
) -> Optional[float]:
    pass
```

### Nommage

- **Classes**: PascalCase (`TradingOrchestrator`)
- **Fonctions/Méthodes**: snake_case (`calculate_profit`)
- **Constantes**: UPPER_SNAKE_CASE (`MAX_TRADE_AMOUNT`)
- **Variables privées**: `_nom` ou `__nom`

### Imports

```python
# Standard library
import os
import sys
from typing import Dict, List

# Third-party
import ccxt
from sqlalchemy import Column

# Local
from src.utils.logger import get_logger
from src.connectors.base_connector import BaseConnector
```

### Logging

Utiliser le logger du projet:
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Avec contexte
logger.info(
    "Trade exécuté avec succès",
    extra={'context': {
        'exchange': 'binance',
        'symbol': 'BTC/USDT',
        'amount': 100.0
    }}
)
```

---

## 🧪 Tests

### Obligatoire

Tout nouveau code **doit** avoir des tests.

### Structure

```
tests/
├── test_connectors/
│   ├── test_base_connector.py
│   └── test_binance_connector.py
├── test_analyzers/
└── ...
```

### Écrire un Test

```python
import pytest
from src.utils.fee_calculator import FeeCalculator

def test_calculate_fee_binance():
    """Test calcul frais Binance"""
    calc = FeeCalculator()
    fee = calc.calculate_fee('binance', 100.0, is_maker=True)
    assert fee == 0.1  # 0.1% maker

def test_calculate_fee_invalid_exchange():
    """Test avec exchange invalide"""
    calc = FeeCalculator()
    with pytest.raises(ValueError):
        calc.calculate_fee('invalid_exchange', 100.0)
```

### Lancer les Tests

```bash
# Tous les tests
pytest

# Un fichier spécifique
pytest tests/test_fee_calculator.py

# Avec couverture
pytest --cov=src tests/

# En verbose
pytest -v
```

### Couverture

- **Minimum**: 70% de couverture
- **Objectif**: 80%+
- **Critique**: Risk management doit être à 90%+

---

## 📝 Commits

### Format

```
<type>(<scope>): <subject>

<body (optionnel)>

<footer (optionnel)>
```

### Types

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation uniquement
- `style`: Formatage, pas de changement de code
- `refactor`: Refactoring sans changement de comportement
- `test`: Ajout/modification de tests
- `chore`: Tâches de maintenance

### Exemples

```bash
# Simple
git commit -m "feat(collectors): Ajouter support pour Coinbase"

# Avec description
git commit -m "fix(risk): Corriger validation montant trade

Le RiskManager ne validait pas correctement les montants
négatifs. Ajout d'une vérification explicite.

Fixes #123"

# Breaking change
git commit -m "feat(connectors): Refactorer BaseConnector

BREAKING CHANGE: La méthode connect() retourne maintenant
un dict au lieu d'un bool."
```

---

## 🔀 Pull Requests

### Avant de Soumettre

✅ **Checklist:**
- [ ] Code respecte les standards
- [ ] Tests ajoutés et passent
- [ ] Documentation mise à jour
- [ ] CHANGELOG.md mis à jour
- [ ] Commits propres et descriptifs
- [ ] Aucun fichier sensible (.env, logs)
- [ ] Branch à jour avec `main`

### Template PR

```markdown
## Description
Décrivez vos changements

## Type de Changement
- [ ] 🐛 Bug fix
- [ ] ✨ Nouvelle fonctionnalité
- [ ] 💥 Breaking change
- [ ] 📝 Documentation

## Tests
- [ ] Tests unitaires ajoutés
- [ ] Tests d'intégration ajoutés
- [ ] Tous les tests passent

## Checklist
- [ ] Code respecte PEP 8
- [ ] Docstrings ajoutées
- [ ] CHANGELOG.md mis à jour
- [ ] Tests passent localement
```

### Processus de Review

1. **Automated checks**: Tests CI/CD doivent passer
2. **Code review**: Au moins 1 approbation
3. **Merge**: Squash and merge préféré

---

## 🔐 Sécurité

### Ne JAMAIS Committer

- ❌ Fichiers `.env`
- ❌ Clés API
- ❌ Mots de passe
- ❌ Tokens
- ❌ Fichiers de logs avec données sensibles

### Signaler une Vulnérabilité

**NE PAS** créer une issue publique.

Envoyez un email à: [votre-email] avec:
- Description de la vulnérabilité
- Étapes pour la reproduire
- Impact potentiel

---

## 📚 Ressources

### Documentation

- [README.md](README.md) - Vue d'ensemble du projet
- [CHANGELOG.md](CHANGELOG.md) - Historique des versions
- [Plan d'Action](Plan_Action_Etapes_Detaillees.md) - Roadmap détaillée

### Outils Utiles

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [CCXT Documentation](https://docs.ccxt.com/)

---

## ❓ Questions

Des questions ? Plusieurs options:

1. **Issues GitHub**: Pour bugs et fonctionnalités
2. **Discussions**: Pour questions générales
3. **Email**: [votre-email] pour questions privées

---

## 🎉 Remerciements

Merci de contribuer au projet ! Chaque contribution, petite ou grande, est appréciée.

---

**Dernière mise à jour:** 2 février 2026
