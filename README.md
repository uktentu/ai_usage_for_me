# 🧠 AIBoost — AI Usage & Pareto Learning Planner

**Live app → [uktentu.github.io/ai_usage_for_me](https://uktentu.github.io/ai_usage_for_me)**

A focused web application that helps you:

1. **Improve your AI usage** across all major LLMs (GPT-4o, Claude, Gemini, Llama, Perplexity).
2. **Generate a Pareto (80/20) learning plan** for any technology or topic you want to master.
3. **Copy expert prompt templates** for coding, writing, analysis, and more.

---

## Features

| Feature | Description |
|---|---|
| 📚 **Learning Planner** | Enter any topic → AI generates a phased, Pareto-optimal roadmap with key concepts, resources, projects, and success metrics. Works in demo mode with no API key. |
| 🤖 **LLM Guide** | Side-by-side guide for GPT-4o, Claude, Gemini, Llama & Perplexity — strengths, best prompting patterns, and what to avoid. |
| ✨ **Prompt Library** | One-click-to-copy expert prompt templates for learning, coding, writing, and analysis. |
| ⚙️ **API Key Settings** | Enter your OpenAI key directly in the browser — stored in session memory only, never leaves your device except to go to OpenAI. |

---

## 🚀 Using the Live App (GitHub Pages)

1. Open **[uktentu.github.io/ai_usage_for_me](https://uktentu.github.io/ai_usage_for_me)**
2. *(Optional)* Click **⚙️ API Key**, enter your OpenAI key and click **Save Key** to get AI-generated plans.
   - Get a key for free at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - `gpt-4o-mini` costs roughly **$0.0001 per plan**
3. Click **📚 Learning Planner**, type a topic, and hit **⚡ Generate Plan**

> **No API key?** The app works in demo mode with a structured template plan for any topic.

---

## 🖥️ Running Locally (with Flask backend)

The Flask backend lets you store the API key securely in a `.env` file instead of the browser.

### 1. Clone & install

```bash
git clone https://github.com/uktentu/ai_usage_for_me.git
cd ai_usage_for_me
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

### 3. Run

```bash
python app.py
```

Then open **http://localhost:5000**.

---

## Pareto Principle (80/20 Rule)

The learning planner is built around the idea that **20% of a subject's content delivers 80% of practical mastery**. Each generated plan:

- Identifies the critical 20% to focus on first
- Structures learning in 4 progressive phases: Foundations → Core Skills → Real-World Project → Mastery
- Includes a hands-on mini-project at every phase
- Lists success metrics so you know when you are done

---

## Tech Stack

| Layer | Technology |
|---|---|
| Static / GitHub Pages | Vanilla HTML + CSS + JavaScript (zero build step) |
| Local backend | Python + Flask + OpenAI Python SDK |
| Deployment | GitHub Actions → GitHub Pages |
| AI | OpenAI API (gpt-4o-mini by default, configurable) |

---

## Deployment (GitHub Actions)

The `.github/workflows/deploy.yml` workflow automatically deploys the `docs/` folder to GitHub Pages on every push to `main`.

To enable it in your own fork:
1. Go to **Settings → Pages**
2. Set **Source** to **GitHub Actions**
3. Push to `main` — the workflow will deploy automatically

---

## Environment Variables (local Flask only)

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | _(none)_ | Your OpenAI API key |
| `OPENAI_BASE_URL` | OpenAI default | Override for local / other providers |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use for plan generation |
| `FLASK_DEBUG` | `false` | Enable debug mode (local dev only) |
| `PORT` | `5000` | Port to run the server on |
