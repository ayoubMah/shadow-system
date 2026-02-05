# Gemini 3 Developer Competition: Submission Details

**Project Name**: Shadow System (The Sovereign Engine)
**Category**: Productivity / Gamification

### 🤖 Gemini Features Used
The Shadow System leverages **Gemini 2.5 Flash** and **Gemini 2.0 Flash** to create a persistent, judgemental AI utility.

1.  **Thinking Mode (Reasoning)**: We used `thinking_config(include_thoughts=True)` in the **Auditor Agent**. This allows the AI to "reason" through a user's excuses for missing a quest before delivering a final verdict. It creates a fair but firm "Game Master" persona.
2.  **Tool Use (Function Calling)**: The **Sovereign Agent** uses dynamic tools like `update_player_stats` and `unlock_skill` to modify the SQLite database directly based on the conversation state.
3.  **Multi-Turn Chat Context**: The **Onboarding Agent** (`onboarding.py`) maintains a stateful interview to extract abstract user goals ("I want to be a Founder") and map them to concrete database schemas (Quest Lines).
4.  **Resilience**: We implemented a multi-model fallback strategy that rotates between Flash 2.5 and Flash 2.0 to handle high-frequency request bursts (Rate Limit handling).
5.  **Artifact Generation**: The system generates persistent markdown artifacts (`DAILY_QUEST.md`, `VERDICT.md`) that serve as the user's daily dashboard.

This project demonstrates how LLMs can go beyond "chatbots" to become **State Machines** that manage real-world logic and user habits.
