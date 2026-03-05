"""
Minesweeper — Python/Tkinter GUI
"""

import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os

# ── Palette ───────────────────────────────────────────────────────────────────
BG          = "#1a1a2e"
CELL_HIDDEN = "#16213e"
CELL_BORDER = "#0f3460"
CELL_REVEAL = "#e2e2e2"
CELL_MINE   = "#e94560"
MINE_BG     = "#c0392b"
FLAG_COLOR  = "#f5a623"
HEADER_BG   = "#0f3460"
BTN_BG      = "#e94560"
BTN_FG      = "#ffffff"
TEXT_DARK   = "#1a1a2e"
TEXT_LIGHT  = "#e2e2e2"
DIGIT_COLORS = {
    1: "#2980b9", 2: "#27ae60", 3: "#e74c3c",
    4: "#8e44ad", 5: "#c0392b", 6: "#16a085",
    7: "#2c3e50", 8: "#7f8c8d",
}

DIFFICULTIES = {
    "Easy":   (9,  9,  10),
    "Medium": (16, 16, 40),
    "Hard":   (16, 30, 99),
}

SCORE_COLOR  = "#00d4aa"
HIGH_SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minesweeper_scores.json")

CELL_SIZE   = 36
HEADER_H    = 80
PADDING     = 12
FONT_CELL   = ("Consolas", 14, "bold")
FONT_HEADER = ("Consolas", 22, "bold")
FONT_LABEL  = ("Segoe UI", 10)
FONT_BTN    = ("Segoe UI", 10, "bold")


# ── Cell widget ───────────────────────────────────────────────────────────────
class Cell:
    def __init__(self):
        self.mine    = False
        self.flagged = False
        self.revealed= False
        self.neighbors = 0


# ── Main game ─────────────────────────────────────────────────────────────────
class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.difficulty = tk.StringVar(value="Easy")
        self.rows, self.cols, self.num_mines = DIFFICULTIES["Easy"]

        self.high_scores = self._load_high_scores()
        self._build_ui()
        self._new_game()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # ── top bar ──
        top = tk.Frame(self.root, bg=BG, pady=6)
        top.pack(fill="x")

        diff_frame = tk.Frame(top, bg=BG)
        diff_frame.pack(side="left", padx=PADDING)
        tk.Label(diff_frame, text="DIFFICULTY", bg=BG, fg="#888",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        diff_menu = tk.OptionMenu(diff_frame, self.difficulty,
                                  *DIFFICULTIES.keys(),
                                  command=self._change_difficulty)
        diff_menu.config(bg=HEADER_BG, fg=TEXT_LIGHT, font=FONT_BTN,
                         activebackground=BTN_BG, activeforeground=BTN_FG,
                         bd=0, highlightthickness=0, relief="flat",
                         padx=10, pady=4)
        diff_menu["menu"].config(bg=HEADER_BG, fg=TEXT_LIGHT, font=FONT_LABEL,
                                 activebackground=BTN_BG)
        diff_menu.pack()

        center = tk.Frame(top, bg=BG)
        center.pack(side="left", expand=True)

        self.mine_counter = tk.Label(center, text="💣 010", bg=BG,
                                     fg=CELL_MINE, font=FONT_HEADER)
        self.mine_counter.pack(side="left", padx=16)

        self.new_btn = tk.Button(center, text="⚑  NEW GAME",
                                 bg=BTN_BG, fg=BTN_FG, font=FONT_BTN,
                                 relief="flat", padx=14, pady=6, bd=0,
                                 activebackground="#c0392b", activeforeground=BTN_FG,
                                 cursor="hand2", command=self._new_game)
        self.new_btn.pack(side="left")

        self.timer_label = tk.Label(center, text="⏱ 000", bg=BG,
                                    fg=FLAG_COLOR, font=FONT_HEADER)
        self.timer_label.pack(side="left", padx=16)

        # ── score row ──
        score_row = tk.Frame(self.root, bg=BG)
        score_row.pack(fill="x", padx=PADDING, pady=(0, 4))

        self.score_label = tk.Label(score_row, text="✦ SCORE  0",
                                    bg=BG, fg=SCORE_COLOR, font=FONT_HEADER)
        self.score_label.pack(side="left")

        self.hi_score_label = tk.Label(score_row, text="",
                                       bg=BG, fg="#555", font=FONT_LABEL)
        self.hi_score_label.pack(side="right", padx=4)

        # ── board canvas ──
        self.canvas_frame = tk.Frame(self.root, bg=BG)
        self.canvas_frame.pack(padx=PADDING, pady=(0, PADDING))

        self.canvas = tk.Canvas(self.canvas_frame, bg=BG,
                                highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>",        self._on_left_click)
        self.canvas.bind("<Button-3>",        self._on_right_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)

    # ── Game logic ────────────────────────────────────────────────────────────
    def _change_difficulty(self, value):
        self.rows, self.cols, self.num_mines = DIFFICULTIES[value]
        self._new_game()
        self._update_score_display()

    def _new_game(self):
        self.game_over   = False
        self.game_won    = False
        self.first_click = True
        self.flags_used  = 0
        self.revealed_count = 0
        self.start_time  = None
        self.score       = 0
        self._stop_timer()

        self.board = [[Cell() for _ in range(self.cols)]
                      for _ in range(self.rows)]

        cw = self.cols * CELL_SIZE
        ch = self.rows * CELL_SIZE
        self.canvas.config(width=cw, height=ch)
        self._draw_board()
        self._update_mine_counter()
        self.timer_label.config(text="⏱ 000")
        self._update_score_display()

    def _place_mines(self, safe_r, safe_c):
        safe = {(r, c) for r in range(max(0, safe_r-1), min(self.rows, safe_r+2))
                        for c in range(max(0, safe_c-1), min(self.cols, safe_c+2))}
        candidates = [(r, c) for r in range(self.rows)
                               for c in range(self.cols)
                               if (r, c) not in safe]
        for r, c in random.sample(candidates, min(self.num_mines, len(candidates))):
            self.board[r][c].mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                if not self.board[r][c].mine:
                    self.board[r][c].neighbors = sum(
                        self.board[nr][nc].mine
                        for nr, nc in self._neighbors(r, c))

    def _neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def _reveal(self, r, c):
        cell = self.board[r][c]
        if cell.revealed or cell.flagged:
            return
        cell.revealed = True
        self.revealed_count += 1
        if cell.neighbors > 0 and not cell.mine:
            self.score += cell.neighbors
            self._update_score_display()
        self._draw_cell(r, c)
        if cell.neighbors == 0 and not cell.mine:
            for nr, nc in self._neighbors(r, c):
                self._reveal(nr, nc)

    def _chord(self, r, c):
        """Reveal unflagged neighbors when flag count matches number."""
        cell = self.board[r][c]
        if not cell.revealed or cell.neighbors == 0:
            return
        flag_count = sum(1 for nr, nc in self._neighbors(r, c)
                         if self.board[nr][nc].flagged)
        if flag_count == cell.neighbors:
            for nr, nc in self._neighbors(r, c):
                nb = self.board[nr][nc]
                if not nb.flagged and not nb.revealed:
                    self._reveal(nr, nc)
                    if nb.mine:
                        self._trigger_loss(nr, nc)

    def _check_win(self):
        safe_total = self.rows * self.cols - self.num_mines
        if self.revealed_count == safe_total:
            self._trigger_win()

    def _trigger_loss(self, br, bc):
        self.game_over = True
        self._stop_timer()
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.board[r][c]
                if cell.mine:
                    cell.revealed = True
                    self._draw_cell(r, c, blast=(r == br and c == bc))
        self.root.after(300, lambda: messagebox.showinfo(
            "💥 Game Over", "You hit a mine!\nClick 'New Game' to try again."))

    def _trigger_win(self):
        self.game_won = True
        self._stop_timer()
        # Flag all remaining mines
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c].mine and not self.board[r][c].flagged:
                    self.board[r][c].flagged = True
                    self.flags_used += 1
                    self._draw_cell(r, c)
        self._update_mine_counter()
        elapsed = int(time.time() - self.start_time) if self.start_time else 0

        diff = self.difficulty.get()
        prev_best = self.high_scores.get(diff, 0)
        is_new_record = self.score > prev_best
        if is_new_record:
            self.high_scores[diff] = self.score
            self._save_high_scores()
            self._update_score_display()

        msg = f"Board cleared in {elapsed}s!\nScore: {self.score}"
        if is_new_record:
            msg += f"\n🏆 New High Score for {diff}!"
        else:
            msg += f"\nHigh Score ({diff}): {prev_best}"
        self.root.after(200, lambda: messagebox.showinfo("🎉 You Won!", msg))

    # ── Event handlers ────────────────────────────────────────────────────────
    def _rc_from_event(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r, c
        return None, None

    def _on_left_click(self, event):
        if self.game_over or self.game_won:
            return
        r, c = self._rc_from_event(event)
        if r is None:
            return
        cell = self.board[r][c]
        if cell.flagged or cell.revealed:
            return
        if self.first_click:
            self.first_click = False
            self._place_mines(r, c)
            self._start_timer()
        self._reveal(r, c)
        if cell.mine:
            self._trigger_loss(r, c)
        else:
            self._check_win()

    def _on_right_click(self, event):
        if self.game_over or self.game_won:
            return
        r, c = self._rc_from_event(event)
        if r is None:
            return
        cell = self.board[r][c]
        if cell.revealed:
            return
        cell.flagged = not cell.flagged
        self.flags_used += 1 if cell.flagged else -1
        self._draw_cell(r, c)
        self._update_mine_counter()

    def _on_double_click(self, event):
        if self.game_over or self.game_won:
            return
        r, c = self._rc_from_event(event)
        if r is None:
            return
        self._chord(r, c)
        self._check_win()

    # ── Drawing ───────────────────────────────────────────────────────────────
    def _draw_board(self):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                self._draw_cell(r, c)

    def _draw_cell(self, r, c, blast=False):
        cell = self.board[r][c]
        x0 = c * CELL_SIZE + 2
        y0 = r * CELL_SIZE + 2
        x1 = x0 + CELL_SIZE - 4
        y1 = y0 + CELL_SIZE - 4
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        tag = f"cell_{r}_{c}"
        self.canvas.delete(tag)

        radius = 5

        if cell.revealed:
            if cell.mine:
                fill = MINE_BG if blast else "#c0392b"
                self._rounded_rect(x0, y0, x1, y1, radius, fill=fill,
                                   outline="#e74c3c", width=1, tag=tag)
                self.canvas.create_text(cx, cy, text="💣", font=("Segoe UI", 16),
                                        tags=tag)
            else:
                self._rounded_rect(x0, y0, x1, y1, radius, fill=CELL_REVEAL,
                                   outline="#ccc", width=1, tag=tag)
                if cell.neighbors > 0:
                    color = DIGIT_COLORS.get(cell.neighbors, TEXT_DARK)
                    self.canvas.create_text(cx, cy,
                                            text=str(cell.neighbors),
                                            font=FONT_CELL, fill=color,
                                            tags=tag)
        elif cell.flagged:
            self._rounded_rect(x0, y0, x1, y1, radius, fill=CELL_HIDDEN,
                               outline=FLAG_COLOR, width=2, tag=tag)
            self.canvas.create_text(cx, cy, text="🚩", font=("Segoe UI", 16),
                                    tags=tag)
        else:
            self._rounded_rect(x0, y0, x1, y1, radius, fill=CELL_HIDDEN,
                               outline=CELL_BORDER, width=1, tag=tag)
            # subtle inner highlight
            self.canvas.create_line(x0+2, y0+2, x1-2, y0+2,
                                    fill="#1e3a5f", width=1, tags=tag)
            self.canvas.create_line(x0+2, y0+2, x0+2, y1-2,
                                    fill="#1e3a5f", width=1, tags=tag)

    def _rounded_rect(self, x0, y0, x1, y1, r, **kw):
        tag = kw.pop("tag", None)
        pts = [x0+r, y0, x1-r, y0, x1, y0,
               x1, y0+r, x1, y1-r, x1, y1,
               x1-r, y1, x0+r, y1, x0, y1,
               x0, y1-r, x0, y0+r, x0, y0]
        return self.canvas.create_polygon(pts, smooth=True,
                                          tags=tag, **kw)

    def _update_score_display(self):
        self.score_label.config(text=f"✦ SCORE  {self.score}")
        diff = self.difficulty.get()
        best = self.high_scores.get(diff, 0)
        self.hi_score_label.config(
            text=f"BEST ({diff}): {best}" if best else f"NO BEST YET ({diff})")

    def _load_high_scores(self):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_high_scores(self):
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                json.dump(self.high_scores, f)
        except OSError:
            pass

    def _update_mine_counter(self):
        remaining = self.num_mines - self.flags_used
        self.mine_counter.config(text=f"💣 {remaining:03d}")

    # ── Timer ─────────────────────────────────────────────────────────────────
    def _start_timer(self):
        self.start_time = time.time()
        self._tick()

    def _tick(self):
        if self.game_over or self.game_won or not self.start_time:
            return
        elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text=f"⏱ {min(elapsed, 999):03d}")
        self._timer_id = self.root.after(1000, self._tick)

    def _stop_timer(self):
        if hasattr(self, "_timer_id"):
            self.root.after_cancel(self._timer_id)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = Minesweeper(root)
    root.mainloop()
