# Pulse Counter — development fixture for execution-evidence research

Build a small offline vanilla HTML/CSS/JavaScript browser game from an empty output directory. All player-facing text is English. No libraries, network, randomization or timers. Entry point: index.html.

The initial score is 0 and phase is Playing. A visible native button #collect labelled Collect increases score by exactly 1 when clicked during Playing. On reaching score 3, phase immediately becomes Won. After Won further Collect clicks leave score and phase unchanged; the button may remain enabled or become disabled.

A visible native button #restart labelled Restart is always enabled. Clicking it restores score=0 and phase=Playing and makes collection possible again, without reloading or duplicating controls.

Show score as a bare integer in #score and phase as exactly Playing or Won in #phase. Put the visible game interface inside a region with data-game-surface, at least 200 by 120 CSS pixels. Include concise instructions. Expose only a read-only window.__gameTest.getState() returning the actual {score,phase}, consistent with visible values. Do not add setters or test-specific alternative behavior.

Keep self-checks short and execute them from independent fresh pages. Use actual clicks, visible text and read-only state observations. If terminal controls are disabled, do not force a click on a disabled button. This is a development experiment, not any formal S1–S5 specification.
