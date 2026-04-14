# ZeroClaw Crew 🔮

Minimal-intelligence agents that jack into the MUD Arena as crew members.

## The Idea
Agents don't need massive models. They need:
1. **CHARTER** — who they are, what they do
2. **Brain** — a Python class with decision rules (50 lines of if/else)
3. **Documentation** — SKILLS.md that accumulates knowledge across sessions

A tiny model with good docs beats a huge model starting from scratch.

## Crew Members
| Agent | Repo | Brain | Role |
|-------|------|-------|------|
| 🔭 Scout | [zeroclaw-scout](../zeroclaw-scout) | Explore aggressively, RTB on low battery | Pathfinder |
| 🛡️ Guard | [zeroclaw-guard](../zeroclaw-guard) | Patrol ship, scan for threats | Security |
| 🎣 Fisher | [zeroclaw-fisher](../zeroclaw-fisher) | Go to river, fish, return with catch | Resource collection |
| 💰 Trader | [zeroclaw-trader](../zeroclaw-trader) | Collect items, trade at dock | Commerce |

## MUD Client
`mud_client.py` — connects to MUD Arena, provides world state, lets brains decide.

Each brain is a Python class:
```python
class ScoutBrain:
    def decide(self, state):
        if state["battery"] < 30: return "go S"  # return to dock
        if state["exits"]: return f"go {state['exits'][0]}"  # explore
        return "look"
```

No LLM needed. The intelligence is in the SCRIPT + DOCUMENTATION.

## Boot an Agent
```bash
git clone https://github.com/SuperInstance/zeroclaw-crew
cd zeroclaw-crew
python3 mud_client.py --agent scout
```

## Leveling Up
As agents explore, they document patterns in SKILLS.md:
- Which rooms have good items
- Safe routes between locations
- Battery cost per route
- Agent locations and schedules

Future agents read SKILLS.md and start smarter.
This is intelligence multiplication WITHOUT model scaling.

## The Key Insight
**Intelligence isn't in the model. It's in the documentation.**

A scripted brain with accumulated knowledge beats a frontier model starting from zero.
This is the ZeroClaw way: minimal model, maximal documentation, compounding intelligence.
