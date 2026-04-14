#!/usr/bin/env python3
"""ZeroClaw MUD Client — agents jack into the MUD and act via scripted brains.

Usage:
    python3 mud_client.py --agent scout
    python3 mud_client.py --agent fisher --model deepseek-chat --key YOUR_KEY --base https://api.deepseek.com
"""
import json, sys, random, argparse, urllib.request, ssl

class ScoutBrain:
    """Aggressive explorer. Returns home on low battery."""
    def __init__(self): self.returning = False
    def decide(self, state):
        if state["battery"] < 30: self.returning = True
        if self.returning:
            if state["room"] == "Dock": self.returning = False; return "look"
            if "S" in state["exits"]: return "go S"
            if "W" in state["exits"]: return "go W"
            return "look"
        if state["items"]: return f"pickup {state['items'][0].split()[0]}"
        if state["exits"]: return f"go {random.choice(state['exits'])}"
        return "look"

class GuardBrain:
    """Patrols ship, scans for threats."""
    def decide(self, state):
        if state["battery"] < 40:
            if "S" in state["exits"]: return "go S"
            return "look"
        if state["turn"] % 3 == 0: return "scan"
        if state["agents"]:
            return f"talk {state['agents'][0].split()[0]}"
        if "N" in state["exits"]: return "go N"
        if "S" in state["exits"]: return "go S"
        return "scan"

class FisherBrain:
    """Heads to river, fishes, returns with catch."""
    def __init__(self): self.fish_count = 0
    def decide(self, state):
        if self.fish_count >= 5:
            if state["room"] == "Dock": return "status"
            if "W" in state["exits"]: return "go W"
            if "S" in state["exits"]: return "go S"
            return "look"
        if state["room"] and "river" in state["room"].lower():
            self.fish_count += 1
            return "fish"
        if "E" in state["exits"]: return "go E"
        if "S" in state["exits"]: return "go S"
        return "look"

class TraderBrain:
    """Collects items, trades at dock."""
    def __init__(self): self.inventory = 0
    def decide(self, state):
        if self.inventory >= 6:
            if state["room"] == "Dock": self.inventory = 0; return "status"
            if "S" in state["exits"]: return "go S"
            if "W" in state["exits"]: return "go W"
            return "look"
        if state["items"]:
            self.inventory += 1
            return f"pickup {state['items'][0].split()[0]}"
        if state["exits"]: return f"go {random.choice(state['exits'])}"
        return "look"

BRAINS = {"scout": ScoutBrain, "guard": GuardBrain, "fisher": FisherBrain, "trader": TraderBrain}

def simulate(agent_name):
    """Run agent through simulated MUD rooms."""
    brain = BRAINS[agent_name]()
    rooms = [
        {"room": "Dock", "exits": ["N", "E", "S"], "items": ["docking_rope"], "agents": [], "battery": 100, "turn": 0},
        {"room": "Bridge", "exits": ["N", "S", "E"], "items": ["charts"], "agents": ["Pilot"], "battery": 98, "turn": 1},
        {"room": "Base Camp", "exits": ["W", "N", "E", "S"], "items": ["trail_map"], "agents": [], "battery": 96, "turn": 2},
        {"room": "Forest East", "exits": ["W", "E"], "items": ["birch_bark"], "agents": [], "battery": 94, "turn": 3},
        {"room": "River Bank", "exits": ["W"], "items": ["salmon_scale"], "agents": [], "battery": 90, "turn": 5},
        {"room": "Crystal Cavern", "exits": ["W"], "items": ["crystal_shard"], "agents": ["Dr. Thorne"], "battery": 88, "turn": 6},
        {"room": "Cargo Bay", "exits": ["N"], "items": ["battery_pack"], "agents": [], "battery": 25, "turn": 10},
    ]
    print(f"\n{agent_name.upper()} simulation:")
    for state in rooms:
        action = brain.decide(state)
        print(f"  [{state['room']}] bat={state['battery']}% → {action}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", default="scout", choices=list(BRAINS.keys()))
    args = parser.parse_args()
    
    print(f"🔮 ZeroClaw '{args.agent}' booted")
    print(f"   Brain: {BRAINS[args.agent].__name__}")
    simulate(args.agent)
