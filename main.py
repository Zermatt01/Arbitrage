from src.trading_orchestrator import TradingOrchestrator
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--duration', type=int, default=3600)
    args = parser.parse_args()
    
    orchestrator = TradingOrchestrator(
        dry_run=args.dry_run,
        initial_balance=10000.0
    )
    
    orchestrator.run(duration_seconds=args.duration)

if __name__ == "__main__":
    main()