from tkinter import *
import random
import os

# Constants
GAME_WIDTH = 700
GAME_HEIGHT = 700
SPACE_SIZE = 25
TICK_MS = 140
INITIAL_LENGTH = 1
NUM_AI = 2

PLAYER_COLOR = "#00CC66"
AI_COLOR = "#FFCC33"
FOOD_COLOR = "#FF3333"
BG_COLOR = "#000000"

BEST_SCORE_FILE = "best_score.txt"

# Load and save best score from file
def load_best_score():
    try:
        if os.path.exists(BEST_SCORE_FILE):
            with open(BEST_SCORE_FILE, "r") as f:
                return int(f.read().strip() or 0)
    except Exception:
        pass
    return 0

def save_best_score(score):
    try:
        with open(BEST_SCORE_FILE, "w") as f:
            f.write(str(int(score)))
    except Exception:
        pass

best_score = load_best_score()

# Helpers
def random_cell():
    max_x = (GAME_WIDTH // SPACE_SIZE) - 1
    max_y = (GAME_HEIGHT // SPACE_SIZE) - 1
    return [random.randint(0, max_x) * SPACE_SIZE, random.randint(0, max_y) * SPACE_SIZE]

def wrap_coord(x, y):
    if x < 0:
        x = GAME_WIDTH - SPACE_SIZE
    elif x >= GAME_WIDTH:
        x = 0
    if y < 0:
        y = GAME_HEIGHT - SPACE_SIZE
    elif y >= GAME_HEIGHT:
        y = 0
    return [x, y]

# Food class managing multiple food items (normal + death food)
class Food:
    def __init__(self, canvas):
        self.canvas = canvas
        self.positions = []
        self.ids = []
        self.spawn_food()  # spawn initial food

    def spawn_food(self):
        pos = self._get_random_free_cell()
        self.positions.append(pos)
        food_id = self.canvas.create_oval(
            pos[0], pos[1], pos[0] + SPACE_SIZE, pos[1] + SPACE_SIZE,
            fill=FOOD_COLOR, tag="food"
        )
        self.ids.append(food_id)

    def _get_random_free_cell(self):
        for _ in range(200):
            pos = random_cell()
            occupied = False
            for s in snakes:
                if pos in s.coordinates:
                    occupied = True
                    break
            if pos in self.positions or pos in death_food_positions:
                occupied = True
            if not occupied:
                return pos
        return random_cell()

    def remove_food_at(self, pos):
        if pos in self.positions:
            idx = self.positions.index(pos)
            self.positions.pop(idx)
            try:
                self.canvas.delete(self.ids[idx])
            except Exception:
                pass
            self.ids.pop(idx)

    def add_death_food(self, pos):
        if pos not in self.positions and pos not in death_food_positions:
            death_food_positions.append(pos)
            food_id = self.canvas.create_oval(
                pos[0], pos[1], pos[0] + SPACE_SIZE, pos[1] + SPACE_SIZE,
                fill=FOOD_COLOR, tag="food"
            )
            self.ids.append(food_id)

# Snake class
class Snake:
    def __init__(self, canvas, color, is_player=False, start_pos=None):
        self.canvas = canvas
        self.color = color
        self.is_player = is_player
        self.direction = random.choice(["up", "down", "left", "right"])
        self.score = 0
        self.alive = True
        self.coordinates = []
        self.squares = []
        if start_pos is None:
            start_pos = random_cell()
        for _ in range(INITIAL_LENGTH):
            self.coordinates.append([start_pos[0], start_pos[1]])
            sq = self.canvas.create_rectangle(
                start_pos[0], start_pos[1], start_pos[0] + SPACE_SIZE, start_pos[1] + SPACE_SIZE,
                fill=self.color, tag="snake"
            )
            self.squares.append(sq)

    def head(self):
        return self.coordinates[0]

    def set_direction(self, new_dir):
        opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
        if opposites.get(new_dir) != self.direction:
            self.direction = new_dir

    def move(self, grow=False):
        hx, hy = self.head()
        if self.direction == "up":
            hy -= SPACE_SIZE
        elif self.direction == "down":
            hy += SPACE_SIZE
        elif self.direction == "left":
            hx -= SPACE_SIZE
        else:
            hx += SPACE_SIZE
        nx, ny = wrap_coord(hx, hy)
        new_head = [nx, ny]
        sq = self.canvas.create_rectangle(
            nx, ny, nx + SPACE_SIZE, ny + SPACE_SIZE, fill=self.color, tag="snake"
        )
        self.coordinates.insert(0, new_head)
        self.squares.insert(0, sq)
        if not grow:
            tail_id = self.squares.pop()
            try:
                self.canvas.delete(tail_id)
            except Exception:
                pass
            self.coordinates.pop()

    def destroy(self):
        for sq in self.squares:
            try:
                self.canvas.delete(sq)
            except Exception:
                pass
        self.squares = []
        self.coordinates = []
        self.alive = False

# Globals
snakes = []
food = None
player = None
running = False
game_after_id = None
death_food_positions = []
try_again_button = None

# Spawn AI snake
def spawn_ai():
    for _ in range(200):
        pos = random_cell()
        if any(pos in s.coordinates for s in snakes):
            continue
        s = Snake(canvas, AI_COLOR, is_player=False, start_pos=pos)
        snakes.append(s)
        return s
    # fallback
    s = Snake(canvas, AI_COLOR, is_player=False)
    snakes.append(s)
    return s

def respawn_ai(dead_snake):
    try:
        dead_snake.destroy()
    except Exception:
        pass
    if dead_snake in snakes:
        snakes.remove(dead_snake)
    new_ai = spawn_ai()
    new_ai.score = 0
    return new_ai

# Collision check (head hits any body except own head)
def check_head_body_collision(s):
    head = s.head()
    # Check self collision with body
    if head in s.coordinates[1:]:
        return True
    # Check collision with other snakes' bodies
    for other in snakes:
        if other is s or not other.alive:
            continue
        if head in other.coordinates:
            return True
    return False

# Simple AI move logic: mostly go toward closest food, some randomness
def ai_decide_direction(s):
    if not food or not food.positions:
        return
    hx, hy = s.head()
    # Get closest food pos (normal + death food)
    all_food = food.positions + death_food_positions
    target = min(all_food, key=lambda f: abs(f[0]-hx)+abs(f[1]-hy))
    dx = target[0] - hx
    dy = target[1] - hy
    if abs(dx) > abs(dy):
        preferred = "right" if dx > 0 else "left"
    else:
        preferred = "down" if dy > 0 else "up"
    if random.random() < 0.25:
        choices = ["up", "down", "left", "right"]
        opp = {"up":"down","down":"up","left":"right","right":"left"}
        if s.direction in choices:
            choices.remove(opp[s.direction])
        s.direction = random.choice(choices)
    else:
        s.set_direction(preferred)

# Main game loop tick
def tick():
    global running, game_after_id, best_score, player, try_again_button

    if not running:
        return

    snapshot = list(snakes)
    for s in snapshot:
        if not s.alive:
            continue

        if not s.is_player:
            ai_decide_direction(s)

        hx, hy = s.head()
        if s.direction == "up":
            hy -= SPACE_SIZE
        elif s.direction == "down":
            hy += SPACE_SIZE
        elif s.direction == "left":
            hx -= SPACE_SIZE
        else:
            hx += SPACE_SIZE
        nx, ny = wrap_coord(hx, hy)
        next_pos = [nx, ny]

        will_grow = False
        # Check if next_pos is food (normal or death)
        if next_pos in food.positions or next_pos in death_food_positions:
            will_grow = True
            # Remove eaten food
            if next_pos in food.positions:
                food.remove_food_at(next_pos)
                # Spawn new normal food after normal food eaten
                food.spawn_food()
            else:
                death_food_positions.remove(next_pos)
                # Remove its oval from canvas (matching id)
                # We rely on the fact the food class draws all food including death food.
                # So remove one oval at the eaten position:
                for idx, pos in enumerate(food.positions):
                    if pos == next_pos:
                        food.remove_food_at(pos)
                        break

            s.score += 1
            if s.is_player:
                if s.score > best_score:
                    best_score = s.score
                    save_best_score(best_score)
                label.config(text=f"Score: {s.score}  Best: {best_score}")

        s.move(grow=will_grow)

        # Check collision: attacker dies if head hits any body
        if check_head_body_collision(s):
            # Drop death food at snake body parts that are not occupied by others
            for part in s.coordinates:
                occupied = False
                for other in snakes:
                    if other is s or not other.alive:
                        continue
                    if part in other.coordinates:
                        occupied = True
                        break
                if not occupied:
                    food.add_death_food(part)

            died_player = s.is_player
            s.destroy()
            if s in snakes:
                snakes.remove(s)

            if died_player:
                running = False
                # Remove existing try again button if any
                global try_again_button
                if try_again_button is not None:
                    try_again_button.destroy()
                canvas.create_text(GAME_WIDTH // 2, GAME_HEIGHT // 3,
                                   text="GAME OVER", fill="red", font=("Arial", 36), tag="gameover")
                try_again_button = Button(window, text="Try Again", command=restart_game)
                try_again_button.place(x=GAME_WIDTH // 2 - 50, y=GAME_HEIGHT // 2)
                return
            else:
                respawn_ai(s)

    game_after_id = window.after(TICK_MS, tick)

# Input handler for arrow keys + WASD
def on_key(event):
    key = event.keysym
    if not player or not player.alive:
        return
    mapping = {
        "Up": "up", "Down": "down", "Left": "left", "Right": "right",
        "w": "up", "s": "down", "a": "left", "d": "right"
    }
    if key in mapping:
        player.set_direction(mapping[key])

# Restart game function
def restart_game():
    global snakes, food, player, running, game_after_id, death_food_positions, try_again_button
    if try_again_button is not None:
        try_again_button.destroy()
        try_again_button = None

    try:
        if game_after_id:
            window.after_cancel(game_after_id)
    except Exception:
        pass

    canvas.delete("all")
    death_food_positions.clear()
    snakes = []
    center = [ (GAME_WIDTH // 2) // SPACE_SIZE * SPACE_SIZE, (GAME_HEIGHT // 2) // SPACE_SIZE * SPACE_SIZE ]
    player = Snake(canvas, PLAYER_COLOR, is_player=True, start_pos=center)
    snakes.append(player)
    for _ in range(NUM_AI):
        spawn_ai()
    food = Food(canvas)
    label.config(text=f"Score: {player.score}  Best: {best_score}")
    running = True
    tick()

# Setup tkinter window
window = Tk()
window.title("Multiplayer Snake with AI and Portal Walls")
window.resizable(False, False)

label = Label(window, text=f"Score: 0  Best: {best_score}", font=("Arial", 16))
label.pack()

canvas = Canvas(window, width=GAME_WIDTH, height=GAME_HEIGHT, bg=BG_COLOR)
canvas.pack()

window.bind("<Key>", on_key)

restart_game()
window.mainloop()
