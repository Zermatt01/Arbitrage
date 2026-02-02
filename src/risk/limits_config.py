"""
Limits Configuration - Configuration des Limites de Trading
============================================================

Définit et gère toutes les limites de trading.

Usage:
    from src.risk.limits_config import LimitsConfig
    
    limits = LimitsConfig()
    print(f"Max par trade: ${limits.max_trade_amount}")
"""

from typing import Dict, Any
import json
import os
from src.utils.logger import get_logger


class LimitsConfig:
    """
    Gère la configuration des limites de trading
    
    Limites configurables :
    - Montants par trade (min/max)
    - Nombre de trades quotidiens
    - Pertes quotidiennes maximum
    - Taille de position maximum
    - Profit minimum requis
    """
    
    # Configuration par défaut (CONSERVATRICE)
    DEFAULT_LIMITS = {
        # Montants
        'max_trade_amount': 100.0,          # $100 max par trade
        'min_trade_amount': 10.0,           # $10 min par trade
        
        # Nombre de trades
        'max_daily_trades': 50,             # 50 trades max par jour
        'max_consecutive_losses': 5,        # 5 pertes consécutives max
        
        # Pertes
        'max_daily_loss': 500.0,            # $500 perte max par jour
        'max_loss_per_trade': 50.0,         # $50 perte max par trade
        
        # Position
        'max_position_size_pct': 10.0,      # 10% du capital max par position
        
        # Profit
        'min_profit_pct': 0.5,              # 0.5% profit min requis
        'min_score': 70.0,                  # Score 70/100 minimum
        
        # Slippage
        'max_slippage_pct': 0.5,            # 0.5% slippage max
        
        # Capital
        'min_balance_usd': 1000.0,          # $1000 balance min pour trader
        'reserve_pct': 10.0,                # 10% en réserve (jamais tradé)
    }
    
    def __init__(self, config_file: str = None):
        """
        Initialise la configuration des limites
        
        Args:
            config_file: Chemin vers fichier JSON de config (optionnel)
        """
        self.logger = get_logger(__name__)
        self.config_file = config_file or 'config/limits.json'
        
        # Charger la config (ou utiliser défauts)
        self.limits = self._load_config()
        
        self.logger.info(
            "Configuration des limites chargée",
            extra={'context': self.limits}
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Charge la configuration depuis un fichier ou utilise les défauts
        
        Returns:
            Dict avec les limites
        """
        # Si fichier existe, charger
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                self.logger.info(f"Configuration chargée depuis {self.config_file}")
                
                # Merger avec défauts (pour nouvelles clés)
                merged = self.DEFAULT_LIMITS.copy()
                merged.update(config)
                
                return merged
                
            except Exception as e:
                self.logger.error(f"Erreur chargement config: {e}, utilisation des défauts")
                return self.DEFAULT_LIMITS.copy()
        
        # Sinon, créer le fichier avec les défauts
        self.logger.info("Création du fichier de configuration par défaut")
        self._save_config(self.DEFAULT_LIMITS)
        return self.DEFAULT_LIMITS.copy()
    
    def _save_config(self, limits: Dict[str, Any]) -> bool:
        """
        Sauvegarde la configuration dans un fichier
        
        Args:
            limits: Configuration à sauvegarder
        
        Returns:
            True si succès
        """
        try:
            # Créer le dossier si besoin
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Sauvegarder
            with open(self.config_file, 'w') as f:
                json.dump(limits, f, indent=4)
            
            self.logger.info(f"Configuration sauvegardée dans {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde config: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Sauvegarde la configuration actuelle dans un fichier
        
        Returns:
            True si succès
        """
        return self._save_config(self.limits)
    
    def update_limit(self, key: str, value: float) -> bool:
        """
        Met à jour une limite spécifique
        
        Args:
            key: Nom de la limite
            value: Nouvelle valeur
        
        Returns:
            True si succès
        """
        if key not in self.DEFAULT_LIMITS:
            self.logger.warning(f"Clé inconnue: {key}")
            return False
        
        old_value = self.limits.get(key)
        self.limits[key] = value
        
        self.logger.info(
            f"Limite mise à jour: {key} = {value} (avant: {old_value})",
            extra={'context': {'key': key, 'old': old_value, 'new': value}}
        )
        
        return True
    
    def validate_limits(self) -> bool:
        """
        Valide que toutes les limites sont cohérentes
        
        Returns:
            True si cohérentes
        """
        errors = []
        
        # Min < Max
        if self.limits['min_trade_amount'] >= self.limits['max_trade_amount']:
            errors.append("min_trade_amount doit être < max_trade_amount")
        
        # Perte par trade < perte quotidienne
        if self.limits['max_loss_per_trade'] >= self.limits['max_daily_loss']:
            errors.append("max_loss_per_trade doit être < max_daily_loss")
        
        # Valeurs positives
        for key, value in self.limits.items():
            if value < 0:
                errors.append(f"{key} ne peut pas être négatif")
        
        # Pourcentages <= 100
        pct_keys = ['max_position_size_pct', 'reserve_pct', 'max_slippage_pct']
        for key in pct_keys:
            if self.limits[key] > 100:
                errors.append(f"{key} ne peut pas être > 100%")
        
        if errors:
            for error in errors:
                self.logger.error(f"Erreur validation: {error}")
            return False
        
        return True
    
    def reset_to_defaults(self):
        """Réinitialise aux valeurs par défaut"""
        self.limits = self.DEFAULT_LIMITS.copy()
        self.logger.info("Configuration réinitialisée aux valeurs par défaut")
    
    # Properties pour accès facile
    @property
    def max_trade_amount(self) -> float:
        """Montant maximum par trade"""
        return self.limits['max_trade_amount']
    
    @property
    def min_trade_amount(self) -> float:
        """Montant minimum par trade"""
        return self.limits['min_trade_amount']
    
    @property
    def max_daily_trades(self) -> int:
        """Nombre maximum de trades par jour"""
        return int(self.limits['max_daily_trades'])
    
    @property
    def max_daily_loss(self) -> float:
        """Perte maximum par jour"""
        return self.limits['max_daily_loss']
    
    @property
    def min_profit_pct(self) -> float:
        """Profit minimum requis en %"""
        return self.limits['min_profit_pct']
    
    @property
    def min_score(self) -> float:
        """Score minimum requis"""
        return self.limits['min_score']
    
    @property
    def max_slippage_pct(self) -> float:
        """Slippage maximum accepté en %"""
        return self.limits['max_slippage_pct']
    
    @property
    def max_consecutive_losses(self) -> int:
        """Nombre maximum de pertes consécutives"""
        return int(self.limits['max_consecutive_losses'])
    
    @property
    def max_loss_per_trade(self) -> float:
        """Perte maximum par trade"""
        return self.limits['max_loss_per_trade']
    
    @property
    def max_position_size_pct(self) -> float:
        """Taille de position maximum en %"""
        return self.limits['max_position_size_pct']
    
    @property
    def min_balance_usd(self) -> float:
        """Balance minimum pour trader"""
        return self.limits['min_balance_usd']
    
    @property
    def reserve_pct(self) -> float:
        """Pourcentage de réserve"""
        return self.limits['reserve_pct']
    
    def get_all_limits(self) -> Dict[str, Any]:
        """
        Retourne toutes les limites
        
        Returns:
            Dict avec toutes les limites
        """
        return self.limits.copy()
    
    def display_limits(self):
        """Affiche toutes les limites de façon lisible"""
        print("\n" + "=" * 60)
        print("  CONFIGURATION DES LIMITES")
        print("=" * 60)
        
        print("\n💰 MONTANTS:")
        print(f"  Max par trade:        ${self.limits['max_trade_amount']:,.2f}")
        print(f"  Min par trade:        ${self.limits['min_trade_amount']:,.2f}")
        
        print("\n📊 TRADES:")
        print(f"  Max par jour:         {self.limits['max_daily_trades']}")
        print(f"  Max pertes consécutives: {self.limits['max_consecutive_losses']}")
        
        print("\n🛡️ PERTES:")
        print(f"  Max par jour:         ${self.limits['max_daily_loss']:,.2f}")
        print(f"  Max par trade:        ${self.limits['max_loss_per_trade']:,.2f}")
        
        print("\n🎯 POSITION:")
        print(f"  Max position:         {self.limits['max_position_size_pct']}% du capital")
        
        print("\n💹 PROFIT:")
        print(f"  Min profit requis:    {self.limits['min_profit_pct']}%")
        print(f"  Score minimum:        {self.limits['min_score']}/100")
        
        print("\n⚡ SLIPPAGE:")
        print(f"  Max slippage:         {self.limits['max_slippage_pct']}%")
        
        print("\n💵 CAPITAL:")
        print(f"  Balance minimum:      ${self.limits['min_balance_usd']:,.2f}")
        print(f"  Réserve:              {self.limits['reserve_pct']}%")
        
        print("\n" + "=" * 60)
    
    def __repr__(self):
        """Représentation textuelle"""
        return f"<LimitsConfig(max_trade=${self.max_trade_amount}, max_daily={self.max_daily_trades})>"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST LIMITS CONFIG")
    print("=" * 60)
    
    # Créer la config
    limits = LimitsConfig()
    
    # Afficher
    limits.display_limits()
    
    # Modifier une limite
    print("\n📝 Modification: max_trade_amount = $500")
    limits.update_limit('max_trade_amount', 500.0)
    
    # Valider
    print("\n✅ Validation...")
    if limits.validate_limits():
        print("✅ Configuration valide")
    else:
        print("❌ Configuration invalide")
    
    # Sauvegarder
    print("\n💾 Sauvegarde...")
    if limits.save_config():
        print(f"✅ Sauvegardé dans {limits.config_file}")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
