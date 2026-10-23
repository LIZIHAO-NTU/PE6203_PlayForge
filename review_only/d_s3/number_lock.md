S3 - Three-Guess Number Lock (C-owned draft for D review)
Build an offline vanilla HTML/CSS/JS game with English UI, no network, packages, timers or randomization.
The fixed target is 7. The player has at most three valid submissions to guess it.
Initial state: attempts=0, phase=Playing, feedback=Ready, and an empty input.
Use a visible text input #guess, a #submit button, #restart, #attempts (bare integer), #feedback and #phase. The main game region has data-game-surface.
Only clicking Submit submits; typing alone does not change game state. Trim surrounding whitespace; a valid submission is exactly one digit from 1 to 9. Empty input, letters, decimals, multiple digits and out-of-range values are invalid.
During Playing, invalid input sets feedback to Invalid input but leaves attempts and phase unchanged. Each valid submission increments attempts exactly once, including the winning submission.
For a correct guess set phase=Won and feedback=Correct. This takes precedence over exhaustion on the third attempt.
For a wrong guess on attempts 1 or 2, remain Playing and show Too low or Too high. A third wrong guess sets phase=Lost and feedback=No attempts left.
After Won or Lost, Submit is a no-op (may remain enabled); attempts, phase and feedback stay unchanged.
Restart is always available and restores attempts=0, phase=Playing, feedback=Ready and clears #guess, including after an invalid input or terminal state.
Expose read-only window.__gameTest.getState() returning the real {attempts,phase,feedback}. Counters, phase and feedback must match those fields. No setters or tester-specific behavior.
