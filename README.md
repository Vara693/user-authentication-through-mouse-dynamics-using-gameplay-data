# User Authentication Through Mouse Dynamics Using Gameplay Data

A **behavioral biometrics** research platform that authenticates and identifies users based on their unique mouse movement patterns. Users play a series of mini-games while the system records granular mouse dynamics data, which is then used to train and evaluate machine learning models for user identification and authentication.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Data Collection Pipeline](#data-collection-pipeline)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Feature Engineering](#feature-engineering)
- [Games](#games)
- [Results & Evaluation](#results--evaluation)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)

---

## Overview

Mouse dynamics authentication is a form of **continuous behavioral biometrics** — it identifies users not by what they know (passwords) or what they have (tokens), but by *how* they naturally interact with a computer. This project implements a full end-to-end research pipeline:

1. **Data Collection** — Users complete 6 structured game sessions that elicit natural mouse behavior
2. **Feature Extraction** — 40+ statistical, kinematic, and behavioral features are computed per session
3. **Model Training** — Two complementary ML approaches: binary (one-vs-all) authentication and multi-class user identification
4. **Evaluation** — Genuine vs. impostor testing with confidence scoring, per-user accuracy breakdowns, and visualization

This system is designed for research purposes in HCI, biometrics, and ML-based authentication.

---

## Features

- **Multi-session data collection** across 6 progressively complex sessions (Training → Validation → Testing)
- **4 distinct mini-games** designed to elicit diverse mouse behavioral signals
- **Dual ML approach**: binary authentication (is this the enrolled user?) + multi-class identification (which user is this?)
- **40+ engineered features** covering velocity, acceleration, trajectory, click dynamics, and timing patterns
- **Per-user model persistence** with serialized scikit-learn pipelines
- **Comprehensive evaluation** with genuine/impostor separation, confidence scoring, and cross-user testing
- **Visualization suite** — feature importance plots, confidence distributions, per-user accuracy charts
- **Tkinter GUI** — fully self-contained desktop application, no browser required

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  main.py (GUI Entry)                    │
│              MouseAuthApp  ─  UserManager               │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │      GameRunner       │  ← orchestrates session flow
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────────┼──────────────┐
    ▼                ▼                    ▼              ▼
TargetHunt      DragDrop           CookieCatcher     MazeRunner
    └────────────────┼────────────────────┼──────────────┘
                     │
              ┌──────▼──────┐
              │  MouseLogger│  ← CSV per session
              └──────┬──────┘
                     │
         ┌───────────▼───────────┐
         │   FeatureExtractor    │  ← 40+ features
         └───────────┬───────────┘
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
  ModelTrainer              MultiClassTrainer
 (binary, per-user)      (multi-class, all users)
       │                           │
       ▼                           ▼
  predict.py                enhanced_testing.py
 (authenticate)             (identify + evaluate)
```

---

## Project Structure

```
mouse-dynamics-auth/
│
├── main.py                        # Application entry point & main GUI
├── game_runner.py                 # Orchestrates game session flow
├── logger.py                      # CSV mouse event logger
├── user_manager.py                # User registration, auth & session tracking
├── model_evaluator.py             # Cross-user genuine/impostor evaluation
│
├── games/
│   ├── base.py                    # Abstract BaseGame (mouse event bindings)
│   ├── target_hunt.py             # Click accuracy mini-game
│   ├── drag_drop.py               # Drag & drop color matching game
│   ├── cookie_catcher.py          # Basket tracking / pursuit game
│   └── maze_runner.py             # Drag-to-navigate maze (6 unique layouts)
│
├── model/
│   ├── feature_extractor.py       # EnhancedFeatureExtractor (40+ features)
│   ├── train_model.py             # Binary (one-vs-all) model trainer
│   ├── multi_class_trainer.py     # Multi-class RandomForest trainer
│   ├── predict.py                 # EnhancedAuthenticationSystem (inference)
│   └── enhanced_testing.py        # GUI testing & identification window
│
├── data/                          # [gitignored] Per-user session CSVs
│   └── <username>/
│       ├── session_1.csv
│       └── ...
│
├── model/                         # [gitignored] Serialized .pkl model files
├── results/                       # [gitignored] Training logs, plots, tables
├── users.json                     # [gitignored] User registry (hashed passwords)
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.8+
- `pip`

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Vara715/user-authentication-through-mouse-dynamics-using-gameplay-data.git
cd user-authentication-through-mouse-dynamics-using-gameplay-data

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Linux / macOS
venv\Scripts\activate             # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

### Dependencies

```text
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
Pillow>=9.5.0
joblib>=1.3.0
```

> **Note:** The GUI uses Python's built-in `tkinter`. On some Linux distributions you may need to install it separately:
> ```bash
> sudo apt-get install python3-tk
> ```

---

## Usage

### 1. Register a User

Launch `main.py`, enter a username and password, and click **Register**.

### 2. Collect Session Data

Click **Start Game Session** to begin. Each session runs 4 mini-games in sequence and takes approximately 3–5 minutes. Complete sessions in order:

| Sessions | Phase     | Purpose                        |
|----------|-----------|-------------------------------|
| 1 – 4    | Training  | Build behavioral baseline      |
| 5        | Validation| Validate model generalization  |
| 6        | Testing   | Final held-out evaluation      |

### 3. Train Your Model

After completing at least 4 sessions, click **Train My Model**. This:
- Extracts features from all your sessions
- Trains a binary (one-vs-all) Random Forest and SVM
- Saves models and generates reports in `results/`

### 4. Evaluate & Test

- **Test Authentication** — Runs your session 6 against your trained binary model
- **User Identification Testing** — Opens the multi-class identification window (requires multiple registered users and a trained multi-class model)
- **Run Comprehensive Test** — Executes cross-user genuine/impostor evaluation across all enrolled users

---

## Data Collection Pipeline

Each mouse event is logged to a CSV with the following schema:

| Column       | Type    | Description                              |
|-------------|---------|------------------------------------------|
| `timestamp`  | float   | Seconds since session start              |
| `event_type` | string  | `motion`, `click`, `drag`                |
| `x`          | int     | Canvas X coordinate                      |
| `y`          | int     | Canvas Y coordinate                      |
| `button`     | string  | Mouse button identifier (`left`, etc.)   |
| `pressed`    | bool    | True on press, False on release          |
| `drag_data`  | string  | Additional drag metadata (optional)      |

Sessions are stored at `data/<username>/session_<N>.csv`.

---

## Machine Learning Pipeline

### Binary Authentication (`train_model.py`)

One model is trained per user using a one-vs-all strategy:

- **Positive samples**: all sessions from the enrolled user
- **Negative samples**: sessions from all other users
- **Models**: Random Forest, SVM (with probability calibration)
- **Evaluation**: Accuracy, cross-validation (5-fold), feature importance
- **Output**: `models/<username>_random_forest.pkl`, `models/<username>_svm.pkl`

### Multi-Class Identification (`multi_class_trainer.py`)

A single model trained across all users simultaneously:

- **Model**: Random Forest (`n_estimators=100`, `class_weight='balanced'`)
- **Labels**: Encoded with `sklearn.LabelEncoder`
- **Evaluation**: Per-class accuracy, top-3 prediction probabilities
- **Output**: `model/multi_class_model.pkl`

### Inference (`predict.py`)

```python
from model.predict import EnhancedAuthenticationSystem

auth = EnhancedAuthenticationSystem()
auth.load_user_model("alice")

result = auth.authenticate_session("alice", session_data_df)
# result = {
#     "authenticated": True,
#     "confidence": 0.87,
#     "reason": "GENUINE_USER",
#     "features_extracted": 42
# }
```

---

## Feature Engineering

`feature_extractor.py` computes 40+ features across six categories:

| Category             | Example Features                                                             |
|----------------------|------------------------------------------------------------------------------|
| **Session Metadata** | Duration, total events, events/second, unique positions                      |
| **Movement**         | Mean/std velocity, max velocity, acceleration stats, directional consistency |
| **Click Dynamics**   | Click count, clicks/min, mean duration, spatial std, inter-click distance    |
| **Timing**           | Mean/std interval, skewness, kurtosis of inter-event gaps                    |
| **Trajectory**       | Straightness ratio, complexity, covered area, mean curvature                 |
| **Behavioral**       | First/second half activity split, activity concentration                     |
| **Statistical**      | Velocity skewness, velocity kurtosis                                         |

All features are scalar-valued and validated before model input.

---

## Games

### Target Hunt
Click a randomly-repositioning red circular target 15 times within 30 seconds. Captures **click precision and movement-to-target trajectories**.

### Drag & Drop
Drag 5 colored circles to their matching colored drop zones. Captures **drag initiation, sustained drag control, and release precision**.

### Cookie Catcher
Move a basket horizontally to catch falling cookies (15 required, max 5 misses). Captures **pursuit tracking and continuous horizontal velocity control**.

### Maze Runner
Navigate a drag-controlled player through a maze to a green exit without hitting walls. Six unique maze layouts (one per session, progressively complex). Captures **fine motor control, wall-avoidance, and path planning behavior**.

---

## Results & Evaluation

After training, results are saved to:

```
results/
├── training_logs.json              # Model accuracy per user per run
├── tables/
│   ├── classification_report.csv   # Per-class precision / recall / F1
│   └── feature_importance.csv      # Ranked feature importances
└── plots/
    ├── user_accuracy.png           # Accuracy bar chart per user
    ├── feature_importance.png      # Top 20 features (horizontal bar)
    └── testing/
        ├── confidence_distribution.png   # Genuine vs impostor confidence histograms
        └── user_accuracy.png             # Cross-user authentication accuracy
```

The `ModelEvaluator` generates a summary report including:

- **Overall Accuracy**
- **Genuine User Acceptance Rate** (True Accept Rate)
- **Impostor Rejection Rate** (True Reject Rate)
- **Per-user breakdown** with genuine and impostor accuracy

---

## Tech Stack

| Component          | Technology                            |
|--------------------|---------------------------------------|
| GUI                | Python `tkinter` / `ttk`              |
| Data Storage       | CSV (mouse logs), JSON (user registry)|
| Feature Extraction | `pandas`, `numpy`, `scipy`            |
| ML Models          | `scikit-learn` (Random Forest, SVM)   |
| Model Persistence  | `pickle`, `joblib`                    |
| Visualization      | `matplotlib`, `seaborn`               |

---

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes with clear messages
4. Push and open a Pull Request

Areas for potential improvement:
- Add LSTM/Transformer-based sequence models for richer temporal modeling
- Implement real-time continuous authentication (not session-level)
- Add more games to diversify behavioral signal coverage
- Export trained models to ONNX for cross-platform deployment
- Add a REST API layer for integration with external systems

---

## License

This project is intended for academic and research use. See `LICENSE` for details.
