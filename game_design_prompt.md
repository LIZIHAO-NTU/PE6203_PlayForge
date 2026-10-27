# Star Collector

Create a 2D single-player game that runs offline in a desktop browser.
Use vanilla HTML, CSS and JavaScript without third-party libraries, external images, network requests or build tools.

## Rules

- Use a 640 × 420 canvas. The player is a blue square, initially at the middle of the left side.
- Move with arrow keys. Movement must be continuous and smooth, and the player cannot leave the canvas.
- Touching a yellow star adds 10 points and moves the star to another reachable position.
- Place the first star at the middle of the right side so the player can find and collect it.
- Collecting 3 stars, or 30 points, wins; stop normal movement and show a victory message.
- Press P to pause and P again to resume. Player and game state must not advance while paused.
- Provide a “Restart” button that resets score, player position, win/loss and pause state.
- Show the score and controls, with clearly readable buttons and text.

No sound effects, networking, login or level editor are needed. Draw graphics programmatically.
