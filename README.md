# 🧠 AIBoost — AI Usage & Pareto Learning Planner

A focused web application that helps you:

1. **Improve your AI usage** across all major LLMs (GPT-4o, Claude, Gemini, Llama, Perplexity).
2. **Generate a Pareto (80/20) learning plan** for any technology or topic you want to master.
3. **Copy expert prompt templates** for coding, writing, analysis, and more.

---

## Features

| Feature | Description |
|---|---|
| 📚 **Learning Planner** | Enter any topic → AI generates a phased, Pareto-optimal roadmap with key concepts, resources, projects, and success metrics. |
| 🤖 **LLM Guide** | Side-by-side guide for GPT-4o, Claude, Gemini, Llama & Perplexity — strengths, best prompting patterns, and what to avoid. |
| ✨ **Prompt Library** | One-click-to-copy expert prompt templates for learning, coding, writing, and analysis. |

---

## Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/uktentu/ai_usage_for_me.git
cd ai_usage_for_me
pip install -r requirements.txt
```

### 2. Configure your API key (optional)

The app works in **demo mode** without an API key. To get AI-generated learning plans:

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

> **Tip:** The app also works with any OpenAI-compatible endpoint (e.g. local Ollama or LM Studio) — just set `OPENAI_BASE_URL` in `.env`.

### 3. Run the server

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## Pareto Principle (80/20 Rule)

The learning planner is built around the idea that **20% of a subject's content delivers 80% of practical mastery**. Each generated plan:

- Identifies the critical 20% to focus on first
- Structures learning in 4 progressive phases: Foundations → Core Skills → Real-World Project → Mastery
- Includes a hands-on mini-project at every phase
- Lists success metrics so you know when you're done

---

## Tech Stack

- **Backend:** Python + Flask + OpenAI Python SDK
- **Frontend:** Vanilla HTML / CSS / JavaScript (no build step)
- **AI:** OpenAI API (gpt-4o-mini by default, fully configurable)

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | _(none)_ | Your OpenAI API key |
| `OPENAI_BASE_URL` | OpenAI default | Override for local / other providers |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use for plan generation |
| `PORT` | `5000` | Port to run the server on |
