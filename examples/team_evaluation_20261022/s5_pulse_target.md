# Pulse Target

Build a small offline real-time target game from an empty output directory.
Use only vanilla local HTML, CSS and JavaScript. Do not use networking,
external assets, libraries, randomness, enemies, timers, levels or extra
targets.

The visible game area is a 360 by 220 canvas. Treat horizontal positions as
canvas coordinates. The player marker starts centered at `playerX=30` and may
move while ArrowLeft or ArrowRight is held. Movement uses the animation loop
at 120 pixels per second and clamps the player's center to the inclusive range
10 through 350. Simultaneous opposite directions produce no movement.

Draw one fixed target zone spanning x=170 through x=190. While phase is
Playing, pressing Space wins only when the player's center is inside that
inclusive target zone. A successful lock sets score to 1 and phase to Won.
Pressing Space outside the zone has no effect. After Won, movement and Space
have no effect and the state remains stable.

A visible native button `#restart` always restores exactly `playerX=30`,
`score=0` and phase Playing without reloading the page. Show concise English
instructions, the score as a bare integer in `#score`, and the exact phase text
Playing or Won in `#phase`. Put the canvas and controls inside a region marked
`data-game-surface`.

Expose a read-only `window.__gameTest.getState()` that returns the actual
`{playerX, score, phase}`. Do not add setters, test-only shortcuts or
alternative behavior for verification.
