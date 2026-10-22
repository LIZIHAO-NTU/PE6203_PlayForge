# Reservoir Relay

Build a small offline resource game from an empty output directory. Use only
vanilla local HTML, CSS and JavaScript. Do not use networking, external assets,
libraries, randomness, timers, movement, levels or extra upgrades.

The game starts with 6 water, 0 filled tanks and phase Playing. The Pump action
adds exactly 3 water, capped at 10. The Fill action costs exactly 4 water and
adds exactly one filled tank. Fill has no effect when water is below 4.

Reaching 2 filled tanks immediately changes the phase to Won. After Won, Pump
and Fill have no effect. Restart always restores exactly 6 water, 0 filled
tanks and phase Playing.

Show concise English rules and the current counters. Use visible native buttons
`#pump`, `#fill` and `#restart`. Show water and filled tanks as bare integers in
`#water` and `#tanks`, and show the exact text Playing or Won in `#phase`. Put
the visible interface inside a region marked `data-game-surface`.

Expose a read-only `window.__gameTest.getState()` that returns the actual
`{water, tanks, phase}` and stays consistent with the visible counters. Do not
add setters, test-only shortcuts or alternative behavior for verification.
