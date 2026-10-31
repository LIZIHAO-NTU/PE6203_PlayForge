# Knockdown

A small 3D physics game: throw a ball at a stack of blocks on a table and knock them off.

## Launch

From the repository root:

    bash knockdown/run.sh

Set `PLAYFORGE_PYTHON` to choose the interpreter; otherwise `python3` is used. Requires `pygame`.

## Controls

- Left / Right arrows — orbit camera around the scene
- Up / Down arrows — raise or lower the camera / aim
- Space — hold to charge (about 1 second to full), release to throw
- R — reset blocks, ball, and camera
- Q or Escape — quit

## Notes

- Fixed 1/120 simulation step, 60 FPS rendering.
- The 3D projection, lighting, depth sorting, collision detection and response are implemented directly in `main.py`; only pygame is used for window/input.
- A message on screen announces when the table is clear.
