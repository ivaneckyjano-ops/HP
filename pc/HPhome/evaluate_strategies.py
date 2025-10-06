#!/usr/bin/env python3
"""Vyhodnotenie stratégií.

Načítava trades_log.json, open_positions.json a closed_positions.json,
vypočítava P&L vrátane všetkých nákladov, úspešnosť stratégií, atď.

Použitie:
- python evaluate_strategies.py
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

POSITIONS_FILE = "open_positions.json"
CLOSED_FILE = "closed_positions.json"
TRADES_FILE = "trades_log.json"

def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {}

def calculate_strategy_pnl(trades):
    """Vypočíta P&L pre každú stratégiu."""
    strategy_stats = defaultdict(lambda: {
        'total_trades': 0,
        'winning_trades': 0,
        'total_premium': 0,
        'total_commissions': 0,
        'total_roll_costs': 0,
        'total_close_costs': 0,
        'net_pnl': 0,
        'trades': []
    })

    for trade in trades:
        strategy = trade['strategy']
        stats = strategy_stats[strategy]

        if trade['action'] == 'open_summary':
            stats['total_premium'] += trade.get('net_credit', 0)
            stats['total_commissions'] += trade.get('total_commission', 0)
            stats['total_trades'] += 1
            stats['trades'].append(trade)

        elif trade['action'] == 'roll':
            stats['total_roll_costs'] += trade.get('total_cost', 0)
            stats['trades'].append(trade)

        elif trade['action'] == 'close':
            pnl = trade.get('realized_pnl', 0)
            stats['net_pnl'] += pnl
            if pnl > 0:
                stats['winning_trades'] += 1
            stats['total_close_costs'] += trade.get('commission', 0)
            stats['trades'].append(trade)

    # Vypočítaj celkové náklady a úspešnosť
    for strategy, stats in strategy_stats.items():
        total_costs = stats['total_commissions'] + stats['total_roll_costs'] + stats['total_close_costs']
        stats['total_costs'] = total_costs
        stats['net_pnl_after_costs'] = stats['total_premium'] + stats['net_pnl'] - total_costs

        if stats['total_trades'] > 0:
            stats['win_rate'] = stats['winning_trades'] / stats['total_trades'] * 100
            stats['avg_premium_per_trade'] = stats['total_premium'] / stats['total_trades']
            stats['avg_costs_per_trade'] = total_costs / stats['total_trades']
        else:
            stats['win_rate'] = 0
            stats['avg_premium_per_trade'] = 0
            stats['avg_costs_per_trade'] = 0

    return dict(strategy_stats)

def print_strategy_report(strategy_stats):
    """Vytlačí detailný report pre každú stratégiu."""
    print("\n" + "="*80)
    print("VYHODNOTENIE STRATÉGIÍ - DETAILNÝ REPORT")
    print("="*80)

    for strategy, stats in strategy_stats.items():
        print(f"\n🧠 STRATÉGIA: {strategy}")
        print("-" * 50)
        print(f"📊 Celkový počet obchodov: {stats['total_trades']}")
        print(f"✅ Vyhrané obchody: {stats['winning_trades']}")
        print(f"📈 Win Rate: {stats['win_rate']:.1f}%")

        print(f"\n💰 PREMIUM & NÁKLADY:")
        print(f"   • Celkové premium prijaté: ${stats['total_premium']:.2f}")
        print(f"   • Priemerné premium/obchod: ${stats['avg_premium_per_trade']:.2f}")
        print(f"   • Celkové komisie: ${stats['total_commissions']:.2f}")
        print(f"   • Náklady na roll: ${stats['total_roll_costs']:.2f}")
        print(f"   • Náklady na zatvorenie: ${stats['total_close_costs']:.2f}")
        print(f"   • Celkové náklady: ${stats['total_costs']:.2f}")
        print(f"   • Priemerné náklady/obchod: ${stats['avg_costs_per_trade']:.2f}")

        print(f"\n💎 ZISKOVOSŤ:")
        print(f"   • Realizovaný P&L: ${stats['net_pnl']:.2f}")
        print(f"   • Čistý P&L po nákladoch: ${stats['net_pnl_after_costs']:.2f}")

        if stats['total_costs'] > 0:
            cost_ratio = (stats['total_premium'] / stats['total_costs']) * 100
            print(f"   • Pomer premium/náklady: {cost_ratio:.1f}%")

        print(f"\n📋 POSLEDNÝCH 5 OBCHODOV:")
        for trade in stats['trades'][-5:]:
            action = trade.get('action', '')
            timestamp = trade.get('timestamp', '')[:19]
            pnl = trade.get('realized_pnl', 0)
            print(f"   • {timestamp} | {action} | P&L: ${pnl:.2f}")

def print_summary_report(strategy_stats):
    """Vytlačí súhrnný report všetkých stratégií."""
    print("\n" + "="*80)
    print("SÚHRNNÝ REPORT VŠETKÝCH STRATÉGIÍ")
    print("="*80)

    total_trades = sum(s['total_trades'] for s in strategy_stats.values())
    total_wins = sum(s['winning_trades'] for s in strategy_stats.values())
    total_premium = sum(s['total_premium'] for s in strategy_stats.values())
    total_costs = sum(s['total_costs'] for s in strategy_stats.values())
    total_pnl = sum(s['net_pnl_after_costs'] for s in strategy_stats.values())

    print(f"📊 CELKOVÉ ŠTATISTIKY:")
    print(f"   • Celkový počet obchodov: {total_trades}")
    print(f"   • Celkové vyhrané obchody: {total_wins}")
    if total_trades > 0:
        overall_win_rate = total_wins / total_trades * 100
        print(f"   • Celkový Win Rate: {overall_win_rate:.1f}%")

    print(f"\n💰 CELKOVÉ FINANCIE:")
    print(f"   • Celkové premium prijaté: ${total_premium:.2f}")
    print(f"   • Celkové náklady: ${total_costs:.2f}")
    print(f"   • Čistý P&L: ${total_pnl:.2f}")

    if total_costs > 0:
        roi = (total_pnl / total_costs) * 100
        print(f"   • ROI (čistý P&L / náklady): {roi:.1f}%")

    print(f"\n🏆 PORADIE STRATÉGIÍ (podľa čistého P&L):")
    sorted_strategies = sorted(strategy_stats.items(),
                              key=lambda x: x[1]['net_pnl_after_costs'],
                              reverse=True)
    for i, (strategy, stats) in enumerate(sorted_strategies, 1):
        pnl = stats['net_pnl_after_costs']
        trades = stats['total_trades']
        win_rate = stats['win_rate']
        print(f"   {i}. {strategy}: ${pnl:.2f} | {trades} obchodov | {win_rate:.1f}% win rate")

def main():
    trades = load_json(TRADES_FILE)
    open_pos = load_json(POSITIONS_FILE)
    closed_pos = load_json(CLOSED_FILE)

    print(f"Načítané dáta:")
    print(f"- Trades log: {len(trades)} záznamov")
    print(f"- Otvorené pozície: {len(open_pos)}")
    print(f"- Uzavreté pozície: {len(closed_pos)}")

    if not trades:
        print("Žiadne trades na vyhodnotenie.")
        return

    strategy_stats = calculate_strategy_pnl(trades)

    print_strategy_report(strategy_stats)
    print_summary_report(strategy_stats)

    # Export do JSON pre ďalšie analýzy
    with open('strategy_evaluation.json', 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'strategy_stats': strategy_stats,
            'summary': {
                'total_trades': sum(s['total_trades'] for s in strategy_stats.values()),
                'total_wins': sum(s['winning_trades'] for s in strategy_stats.values()),
                'total_premium': sum(s['total_premium'] for s in strategy_stats.values()),
                'total_costs': sum(s['total_costs'] for s in strategy_stats.values()),
                'net_pnl': sum(s['net_pnl_after_costs'] for s in strategy_stats.values())
            }
        }, f, indent=2)

    print(f"\n💾 Výsledky uložené do strategy_evaluation.json")

if __name__ == "__main__":
    main()