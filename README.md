# ZeroClaw Crew 🔮

Minimal-intelligence agents that jack into the MUD Arena as crew members.

## The Idea
Agents don't need massive models. They need:
1. **CHARTER** — who they are, what they do
2. **Brain** — a Python class with decision rules (50 lines of if/else)
3. **Documentation** — SKILLS.md that accumulates knowledge across sessions

A tiny model with good docs beats a huge model starting from scratch.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MUD Arena                               │
│  (world state: rooms, items, agents, battery, turns)         │
└──────────────┬──────────────────────────────┬────────────────┘
               │  state dict                   │  action string
               ▼                              │
┌──────────────────────┐                       │
│   SKILLS.md          │◄── knowledge          │
│  ┌────────────────┐  │    accumulates here   │
│  │ room layouts   │  │                       │
│  │ safe routes    │  │                       │
│  │ item locations │  │                       │
│  │ agent patterns │──┼──► feeds back into    │
│  │ cost tables    │  │    brain decisions    │
│  └────────────────┘  │                       │
└──────────────────────┘                       │
               │                               │
               ▼                               │
┌──────────────────────────────────────────────┴──────────────┐
│                     Agent Brain                              │
│   ┌───────────┐    ┌──────────────┐    ┌────────────────┐   │
│   │  state    │───►│   decide()   │───►│    action      │   │
│   │  input    │    │  if/else     │    │  "go N"        │   │
│   │           │    │  rules       │    │  "pickup map"  │   │
│   │  battery  │    │  + SKILLS    │    │  "fish"        │   │
│   │  room     │    │  knowledge   │    │  "scan"        │   │
│   │  exits[]  │    │              │    │  "status"      │   │
│   │  items[]  │    │  ~50 lines   │    │                │   │
│   │  agents[] │    │              │    │                │   │
│   │  turn     │    └──────────────┘    └───────┬────────┘   │
│   └───────────┘                                  │           │
└──────────────────────────────────────────────────┼───────────┘
                                                   │
                    action sent back to MUD Arena ──┘
```

The loop: **World State → Brain decides → Action sent → World State updates → repeat.**

SKILLS.md sits alongside the brain as a *knowledge layer* — it's not code, it's structured documentation that the brain's decision rules are designed around, and that grows richer with every session.

## Agent Design Philosophy

The core thesis: **minimal model, maximal documentation, compounding intelligence.**

Most AI agent frameworks try to solve intelligence by scaling the model — bigger context windows, more parameters, chains-of-thought. ZeroClaw takes the opposite approach:

- **The model stays dumb.** A brain is ~50 lines of Python. No transformer, no prompt engineering, no temperature tuning. Pure deterministic if/else.
- **The documentation gets smart.** Every session, agents observe the world and record what they learn into SKILLS.md files. Room layouts, safe routes, item spawn locations, battery costs, agent behavior patterns.
- **Intelligence compounds.** A freshly booted agent starts with whatever SKILLS.md already contains. Session 1's agent explores blindly. Session 50's agent starts with a map, a playbook, and cost tables.

This is **document-driven intelligence** — the idea that the *structure and accumulation of knowledge* matters more than the reasoning engine that processes it. A scout with a map and a playbook will outperform a genius dropped into an unknown city.

The implications:
- **Deterministic** — same inputs, same outputs. Debuggable, auditable, predictable.
- **Inspectable** — you can read SKILLS.md and understand exactly what an agent "knows."
- **Composable** — skills from one agent can be copied to another. Knowledge transfers without retraining.
- **Zero inference cost** — no API calls, no tokens, no latency. A brain runs in microseconds.

## Brain Anatomy

Every agent brain follows the same structure — a Python class with a `decide(state) -> action` interface:

```python
class ScoutBrain:
    """Aggressive explorer. Returns home on low battery."""

    def __init__(self):
        self.returning = False          # internal state (persists across turns)
        self.fish_count = 0             # mission tracking

    def decide(self, state):
        # ── Safety checks (always first) ──
        if state["battery"] < 30:
            self.returning = True       # flip to RTB mode

        # ── Return-to-base logic ──
        if self.returning:
            if state["room"] == "Dock":
                self.returning = False  # reset state
                return "look"
            if "S" in state["exits"]:
                return "go S"
            return "look"

        # ── Mission logic ──
        if state["items"]:
            return f"pickup {state['items'][0].split()[0]}"
        if state["exits"]:
            return f"go {random.choice(state['exits'])}"

        # ── Default fallback ──
        return "look"
```

### State Input

The world state dict passed to `decide()` contains:

| Field | Type | Description |
|-------|------|-------------|
| `room` | `str` | Current room name (e.g. `"Dock"`, `"River Bank"`) |
| `exits` | `list[str]` | Available directions (`["N", "E", "S"]`) |
| `items` | `list[str]` | Items on the ground in this room |
| `agents` | `list[str]` | Other agents present in the room |
| `battery` | `int` | Energy remaining (0–100) |
| `turn` | `int` | Current turn number |

### Action Output

The brain returns a single string — one action per turn:

| Action | Example | Purpose |
|--------|---------|---------|
| `go {dir}` | `"go N"` | Move to adjacent room |
| `pickup {item}` | `"pickup map"` | Collect an item |
| `look` | `"look"` | Observe current room |
| `scan` | `"scan"` | Search for threats/info |
| `fish` | `"fish"` | Attempt to catch fish |
| `talk {agent}` | `"talk Pilot"` | Interact with another agent |
| `status` | `"status"` | Report current status |

### Brain Design Patterns

The four current brains demonstrate common patterns:

- **Threshold guard** — `battery < 30` triggers RTB. Simple, reliable.
- **Mode flip** — `self.returning` boolean toggles behavior. One-way state transition with a reset condition.
- **Mission cap** — `fish_count >= 5` triggers return-with-cargo phase.
- **Turn-based cycling** — `turn % 3 == 0` creates periodic behaviors (scan every 3rd turn).

## Crew Members
| Agent | Repo | Brain | Role |
|-------|------|-------|------|
| 🔭 Scout | [zeroclaw-scout](../zeroclaw-scout) | Explore aggressively, RTB on low battery | Pathfinder |
| 🛡️ Guard | [zeroclaw-guard](../zeroclaw-guard) | Patrol ship, scan for threats | Security |
| 🎣 Fisher | [zeroclaw-fisher](../zeroclaw-fisher) | Go to river, fish, return with catch | Resource collection |
| 💰 Trader | [zeroclaw-trader](../zeroclaw-trader) | Collect items, trade at dock | Commerce |

Beyond the four core agents, the `skills/` directory contains role definitions for the **Cocapn Fleet** vessel crew:

| Role | Skill File | Responsibility |
|------|------------|----------------|
| 🧭 Captain | `skills/captain.md` | Coordination, orders, risk assessment |
| 🗺️ Navigator | `skills/navigator.md` | Course plotting, depth sounding, hazard avoidance |
| 🔧 Engineer | `skills/engineer.md` | Engine diagnostics, fuel management, maintenance |
| 🪝 Deckhand | `skills/deckhand.md` | Gear deployment, catch sorting, ice management |

## SKILLS.md Protocol

SKILLS files are the knowledge layer that makes ZeroClaw agents compound in intelligence over time. Every skill follows a structured format:

```markdown
---
name: nav-plotter
kind: program
---

requires:
- current_position, destination, chart_data, tide_tables, weather

ensures:
- course_to_steer, eta, hazard_warnings, waypoint_list

strategies:
- when current against: adjust heading
- when shoaling: widen margin
- when fog: reduce speed by half
```

### Three-Layer Structure

1. **Frontmatter** (`---` block) — machine-readable metadata: skill name, kind, identity tags.
2. **Contract** (`requires` / `ensures`) — formal I/O contract. What the skill needs as input, what it guarantees as output.
3. **Strategies** — accumulated decision rules. Each entry is a `when {condition}: {action}` clause — pattern-matched situational knowledge.

### Knowledge Accumulation

```
Session 1:  Agent discovers River Bank has fish ──► records "river: fish available"
Session 5:  Agent learns battery cost E→River = 4% ──► records "route E to River: -4 battery"
Session 12: Agent observes Fisher at River on turns 3-8 ──► records "Fisher patrols River every ~5 turns"
Session 50: New agent boots with 49 sessions of accumulated knowledge
```

This is the compounding effect: **every session makes the next session's agent smarter**, without changing a single line of code. The brain stays the same size. The knowledge base grows.

### Compounding Intelligence

The key multiplier: skills are **composable and transferable**. The Navigator's route knowledge helps the Fisher reach the river faster. The Scout's room maps help the Trader plan collection routes. The Guard's threat reports inform everyone's safety thresholds.

Knowledge written by one agent is immediately available to all agents. No fine-tuning, no weight sharing, no distillation — just read the docs.

## MUD Arena Integration

### Connection Model

The MUD client (`mud_client.py`) bridges agents and the arena:

```python
# The full loop (simplified)
brain = BRAINS["scout"]()           # instantiate the agent brain
state = mud.connect(agent_name)     # connect to MUD, get initial state
while True:
    action = brain.decide(state)    # brain produces one action
    state = mud.send(action)        # MUD processes action, returns new state
    skills.log(state, action)       # document what happened
```

### Simulated World

In simulation mode, agents traverse a predefined room graph:

```
                Base Camp ──────── Forest East
               ╱    │    ╲              │
           Bridge  │  Crystal        River Bank
              │    │   Cavern           │
              │    │       │            │
              Dock ───── Cargo Bay ─────┘
```

Each room carries: name, available exits, ground items, present agents, and battery cost to reach.

### MUD Commands

```bash
# Boot a specific agent
python3 mud_client.py --agent scout

# Currently supported agents: scout, guard, fisher, trader
```

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

## Extending the Crew

Adding a new agent to the ZeroClaw crew follows three steps:

### 1. Define the Brain

Create a new brain class in `mud_client.py` (or a separate module):

```python
class CookBrain:
    """Collects ingredients, cooks at galley, feeds crew."""
    def __init__(self):
        self.inventory = []
        self.cooking = False

    def decide(self, state):
        # Safety first
        if state["battery"] < 20:
            if "S" in state["exits"]: return "go S"
            return "look"

        # Mission logic: collect → cook → serve
        if self.cooking and state["room"] == "Galley":
            return "cook"

        if len(self.inventory) >= 3:
            self.cooking = True
            if state["room"] == "Galley": return "cook"
            if "W" in state["exits"]: return "go W"
            return "look"

        if state["items"]:
            self.inventory.append(state["items"][0])
            return f"pickup {state['items'][0].split()[0]}"

        if state["exits"]:
            return f"go {random.choice(state['exits'])}"
        return "look"
```

### 2. Register the Brain

Add it to the `BRAINS` registry:

```python
BRAINS = {
    "scout": ScoutBrain,
    "guard": GuardBrain,
    "fisher": FisherBrain,
    "trader": TraderBrain,
    "cook": CookBrain,          # ← add here
}
```

### 3. Create a SKILLS File

Add `skills/cook.md` with the standard format:

```markdown
---
name: galley-chef
kind: program
---

requires:
- ingredient_locations, galley_position, crew_hunger_levels

ensures:
- meal_prepared, ingredient_stock, crew_fed

strategies:
- when ingredients low: forage. when crew hungry: prioritize cooking.
- when inventory full: head to galley. when galley occupied: wait.
```

That's it. Three artifacts — brain class, registry entry, skill file — and the new agent is part of the crew, compounding intelligence alongside the rest.

## The Key Insight
**Intelligence isn't in the model. It's in the documentation.**

A scripted brain with accumulated knowledge beats a frontier model starting from zero.
This is the ZeroClaw way: minimal model, maximal documentation, compounding intelligence.

---

<img src="callsign1.jpg" width="128" alt="callsign">
