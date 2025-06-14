# 🧠 Minesweeper AI Solver

An intelligent Python bot that plays Minesweeper using a combination of logical inference, CSP (Constraint Satisfaction Problems), and probabilistic reasoning. This project aims to maximize win rates on standard 9x9 Minesweeper boards with 10 mines.

---

## 🚀 Features

- ✅ **Simple Logical Inference** (e.g., 1-mine adjacent = 1 unopened cell → mine)
- 🧩 **CSP-based Reasoning** (local and global)
- 🔁 **Enumerated Possible Placements (EPP)** fallback logic
- 🎯 **Risk-based heuristics** for random guessing
- 📊 **Statistical tracking** of win/loss reasons per move type
- 💡 Switchable between **local CSP** and **global CSP**

---

## 🧠 AI Strategy

The bot plays in the following order of preference:

1. **Simple Logic**: Basic Minesweeper rules (e.g., all mines flagged → open remaining)
2. **Advanced Logic**:
   - Local CSP on perimeter groups
   - Global CSP on all constrained tiles (if enabled)
3. **Probabilistic Move**: Picks the tile with the lowest inferred mine probability
4. **Random Guess**: Uses heuristics to guess the safest-looking cell
