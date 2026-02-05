# 🌑 SWARM ZERO / SHADOW SYSTEM
> *The "Solo Leveling" of Developer Productivity.*

**Shadow System** is a Gamification Engine that turns your life into a Role-Playing Game. It uses Google's **Gemini 2.5 Flash** to analyze your daily habits, GitHub activity, and calendar to assign you a "Character Class" (e.g., *Algorithm Sovereign*, *Octagon Sovereign*) and generate personalized **Daily Quests**.

---

### 🏛️ Architecture (The Monarch Stack)
The system is built on a **Hybrid Agentic Architecture**:

1.  **The Sovereign (`sovereign.py`)**: The central brain. Uses **Gemini 2.5 Flash** with **Thinking Mode** to audit your day and assign XP.
2.  **The Quest Master (`quest_master.py`)**: Runs every morning. Checks your "Weakest Stat" (e.g., Vitality) + Calendar to generate a custom quest.
3.  **The Awakening (`onboarding.py`)**: A multi-turn chat agent (Gemini 2.5) that interviews you to determine your origin story and seed your database.

**Tech Stack**:
-   **Brain**: Gemini 2.5 Flash / 2.0 Flash (Multi-Model Resilience).
-   **Backend**: FastAPI (Python).
-   **Frontend**: Next.js 14 + Tailwind + Framer Motion.
-   **Database**: SQLite (Local State Machine).
-   **Orchestration**: Built with **Google Antigravity** (Agentic IDE).

---

### 🚀 Key Features (Gemini Powered)
-   **🧠 Thinking Mode Audits**: The system doesn't just log stats; it *judges* you. It uses Gemini's reasoning capabilities to determine if your excuses are valid.
-   **🛡️ Vitality Safeguard**: If `Fatigue > Vitality`, the system forces a "Recovery Protocol" (nerfing quest difficulty) to prevent burnout.
-   **🔄 Resilience Protocol**: Implements a "Hydra Strategy" that rotates through `gemini-2.5-flash`, `2.0-flash`, and `lite` to survive Rate Limits.
-   **💬 The Sovereign Interview**: A persistent chat persona that remembers your goals and adapts its tone accordingly.

---

### 📦 Installation
**1. Clone the Repository**
```bash
git clone https://github.com/StartYourOwnRepo/shadow-system.git
cd shadow-system
```

**2. Backend Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your API Key
echo "GEMINI_API_KEY=your_key_here" > .env
echo "SHADOW_MODE=ACTIVE" >> .env

# Initialize Database
python db/init_db.py

# Run the Brain
python -m uvicorn backend.main:app --reload
```

**3. Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

**4. Access the Dashboard**
Open `http://localhost:3000`.

---

### 🤖 Built with Antigravity
This entire system was architected and coded using **Google Antigravity**, an advanced agentic coding assistant. It demonstrates the future of "Human-Agent Pair Programming."
