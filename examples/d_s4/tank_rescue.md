# Tank Rescue

Build a small English offline browser game using local vanilla HTML/CSS/JavaScript.
The player pumps water and delivers supplies before running out of moves.

## Rules

R1. Initially water=2, moves=4, delivered=0 and phase=Playing. Water capacity is 5; the goal is 2 deliveries.

R2. While Playing, Pump adds 3 water capped at 5 and consumes exactly 1 move, even when the tank was already full.

R3. While Playing with water below 4, Deliver is a complete no-op: water, moves, delivered and phase all remain unchanged.

R4. While Playing with water at least 4, Deliver consumes exactly 4 water and 1 move and adds exactly 1 delivery.

R5. After each move-consuming action, check the delivery goal first: delivered=2 means Won; otherwise moves=0 means Lost; otherwise stay Playing. Winning on the final move is Won, not Lost.

R6. In Won or Lost, Pump and Deliver must not change any value. They may remain enabled and ignore activation, or be disabled.

R7. Restart is always enabled and immediately restores all four initial values in every phase, including after an invalid action.

R8. Show short English instructions explaining the initial resources, water capacity, Pump cost at the cap, Deliver cost, insufficient-water no-op, delivery goal, move exhaustion, win-before-loss priority, terminal lock and Restart. Give each button an understandable accessible name.

R9. Use native buttons #pump, #deliver and #restart. The visible #water, #moves and #delivered contain bare integers, and #phase contains exactly Playing, Won or Lost. Mark a visible game area with data-game-surface. Expose window.__gameTest.getState() as a fresh read-only snapshot of actual water, moves, delivered and phase; provide no state setters.

## Interaction and technical boundaries

While Playing, both Pump and Deliver must remain enabled, including at capacity or with insufficient water. A normal button activation applies its rule exactly once and updates the visible fields and read-only snapshot together before the next player action. Restart works by normal button activation. Only these three buttons change game state.

There are no timers, passive changes, randomness, enemies, movement, extra resources, levels, keyboard shortcuts, network requests, remote assets or external packages. Use a simple readable DOM interface; no animation or sound is required. The game must work locally offline. Do not add a solver, automatic play or extra rules.
