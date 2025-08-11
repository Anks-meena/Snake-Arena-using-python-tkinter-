# Snake-Arena-using-python-tkinter-
Guide the snake to eat food, grow longer, and avoid walls or yourself.
Smart AI mode lets the computer play — watch it slither with precision!"

**How To Play:**

**Controls--**
* Move with Arrow keys or w A S D.
* No pause (unless you add one); use the Try Again button after game over.

**Game objects--**
* Player snake (your snake) — green.
* AI snakes — yellow (they move on their own).
* Food — red ovals placed randomly.
* Death food — when a snake dies, its body turns into food you can eat.

**Rules & mechanics--**
* Movement & wrapping: The arena edges are portals — go off one side and appear on the opposite side.
* Eating: Move your head onto a food cell → your snake grows by one segment and your score increases.
* Normal food respawns elsewhere after eaten.
* Food created from dead snake bodies (death food) can also be eaten and removed.
* AI behavior: AI snakes seek food (with basic pathing + randomness). They grow and score like the player.
* Collision rule (head-to-body): If your head hits any part of another snake’s body, your snake dies. The other snake stays alive. (Same for AI: if an AI head hits another body, that AI dies.)
* If you hit your own body, you die.
* Death handling: When a snake dies, its body parts become food (visible and eatable).
* AI that dies will respawn as a fresh AI snake (score resets to 0).
* If the player dies, the game ends and a Try Again button appears.
* Score & best score: Eating increases your score. Best score is saved to best_score.txt and displayed on screen.

**Tips--**
* Eating dead bodies gives quick growth but can also trap you — be cautious.
* Use portal wrapping to escape tight spots or to flank AI.
* Let AI cluster and wait for mistakes; opportunistic play wins.



<img width="1049" height="1149" alt="Screenshot 2025-08-11 112509" src="https://github.com/user-attachments/assets/e598f242-c5d0-4dc2-bffc-cdae996f5a55" />

