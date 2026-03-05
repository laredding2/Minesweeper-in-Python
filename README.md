# 💣 Minesweeper

A fully-featured Minesweeper clone built in Python with a `tkinter` GUI. Includes a live score system, per-difficulty high scores, and a dark-themed interface.

No third-party packages required — just Python's standard library.

---

## Features

- **3 difficulty levels** — Easy (9×9, 10 mines), Medium (16×16, 40 mines), Hard (16×30, 99 mines)
- **Safe first click** — mines are placed after your first reveal, so you can never start on one
- **Chord reveal** — double-click a numbered cell to auto-reveal its neighbors once the correct number of flags are placed
- **Score tracking** — each revealed numbered cell adds its face value to your score (e.g. revealing a `3` adds 3 points)
- **Per-difficulty high scores** — best score for each difficulty is saved between sessions
- **Live counters** — mine counter and elapsed timer update in real time
- **Dark theme UI** — rounded cells, color-coded digits, distinct states for hidden/flagged/revealed cells

---

## Requirements

- Python 3.x
- `tkinter` (included with most standard Python installations)

To verify tkinter is available:

```bash
python -m tkinter
```

A small test window should appear. If it doesn't, install tkinter for your platform:

```bash
# Debian/Ubuntu
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (via Homebrew)
brew install python-tk
```

---

## Installation

Clone the repository and run the script — no install step needed:

```bash
git clone https://github.com/laredding2/minesweeper.git
cd minesweeper
python minesweeper.py
```
- You can also play this game on my website! https://laredding2.github.io/minesweeper.html
---

## How to Play

| Action | Control |
|---|---|
| Reveal a cell | Left-click |
| Place / remove a flag | Right-click |
| Chord reveal (auto-reveal neighbors) | Double-click a revealed number |
| Start a new game | Click **NEW GAME** |
| Change difficulty | Use the dropdown (top-left) |

**Objective:** Reveal every cell that doesn't contain a mine. Use the numbers on revealed cells to deduce where the mines are hiding, and flag them with 🚩.

### Scoring

Points are awarded for every numbered cell you reveal. The value of each cell equals the number shown — so a cell showing `4` is worth 4 points, and a blank cell (no adjacent mines) is worth nothing.

High scores are tracked per difficulty and saved automatically to `minesweeper_scores.json` in the same directory as the script.

---

## File Structure

```
minesweeper/
├── minesweeper.py          # Main game — run this
└── minesweeper_scores.json # Auto-generated; stores high scores per difficulty
```

---

## License

MIT License. See `LICENSE` for details.
