# Mini-Racing-Game---Python
A fast racing game built in Python where you race small cars on tracks. Avoid obstacles, and try to finish first. Easy controls, quick rounds, and increasing difficulty make it fun and replayable.

✨ Features

🏁 Top-down arcade racing with smooth movement physics
🤖 5 AI opponents — Blaze, Ice, Turbo, Nova, Drift — each with unique speed profiles
⚙️ Configurable difficulty (Easy / Normal / Hard) and lap count (1 / 2 / 3 / 5)
⚠️ Oil slick hazards that spin your car out
🌿 Off-track penalty — grass slows you down, stay on the asphalt!
🎨 Tyre trails, smoke particles, kerb stripes, and a dashed centre line
📊 Live standings board showing your position throughout the race
🏆 Post-race podium with Gold / Silver / Bronze results
🔢 3-2-1-GO! animated countdown before each race
🔁 Instant restart and replayable rounds

Developed by Manav Parikh
🚀 Installation & Setup
Requirements

Python 3.13 — Download here
Pygame 2.x


⚠️ Python 3.14+ is not supported. Pygame does not yet have a pre-built wheel for Python 3.14. Use Python 3.13.

Install Pygame
bashpy -3.13 -m pip install pygame
Run the Game
bashpy -3.13 main.py

🕹️ Controls
KeyActionW / ↑AccelerateS / ↓Brake / ReverseA / ←Steer LeftD / →Steer RightRRestart raceQ / ESCBack to setup menu

⚙️ Race Setup Menu
Use arrow keys to configure before each race:

Difficulty: Easy · Normal · Hard
Laps: 1 · 2 · 3 · 5
Press Enter to start


🗂️ File Structure
apex-racer/
├── main.py       # Entire game — single self-contained file
└── README.md

🧠 Technical Concepts
Concept Implementation Physics Speed, friction, steer-speed coupling, off-track dragAIWaypoint-following with wobble & turn-speed modulation Collision Ray-casting point-in-polygon for track boundary detection Track Polygons built procedurally from waypoint perpendicular normals Particles Tyre trails, off-track smoke, finish celebration bursts Game States Setup Menu → Countdown → Racing → Finish Screen
