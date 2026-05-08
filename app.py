"""
AI Usage & Learning Planner – Flask backend
"""

import os
import json
import textwrap

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------
PROVIDERS = {
    "gemini": {
        # Gemini OpenAI-compatible endpoint
        "default_base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "default_model": "gemini-2.5-flash",
    },
    "openai": {
        "default_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
    },
}


def _normalize_provider(value: str | None) -> str:
    provider = (value or "").strip().lower()
    if provider not in PROVIDERS:
        if provider:
            app.logger.warning("Unsupported provider '%s'; falling back to openai", provider)
        return "openai"
    return provider


def _build_client(api_key: str, base_url: str | None = None) -> OpenAI:
    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url.rstrip("/")
    return OpenAI(**kwargs)

# ---------------------------------------------------------------------------
# Static LLM guide data (no API key required)
# ---------------------------------------------------------------------------

LLM_TIPS = [
    {
        "llm": "GPT-4o / GPT-4o mini (OpenAI)",
        "icon": "🤖",
        "color": "#10a37f",
        "strengths": [
            "Excellent at structured output (JSON, tables, code)",
            "Strong reasoning with chain-of-thought prompting",
            "Great for multi-step tasks and long conversations",
            "Supports vision (image input)",
        ],
        "best_prompts": [
            'Use "Think step by step" for complex reasoning',
            "Assign a persona: \"You are an expert Python developer…\"",
            "Ask for output in a specific format: \"Reply in JSON with keys: …\"",
            "Break big tasks into numbered sub-tasks",
        ],
        "avoid": [
            "Vague one-liners without context",
            "Asking multiple unrelated questions at once",
        ],
    },
    {
        "llm": "Claude 3 / Claude 3.5 (Anthropic)",
        "icon": "💬",
        "color": "#c97646",
        "strengths": [
            "Exceptional at following nuanced instructions",
            "Long-context understanding (up to 200 K tokens)",
            "Great for writing, analysis, and summarisation",
            "Safer / more cautious by default",
        ],
        "best_prompts": [
            'Use XML tags to structure your prompt: "<task>…</task><context>…</context>"',
            "Provide examples inside <example> tags for few-shot learning",
            "Ask Claude to reflect or critique its own answer",
            "For documents, paste the full text and ask targeted questions",
        ],
        "avoid": [
            "Very short prompts for complex tasks",
            "Expecting it to break its safety guardrails",
        ],
    },
    {
        "llm": "Gemini 1.5 / 2.0 (Google)",
        "icon": "✨",
        "color": "#4285f4",
        "strengths": [
            "Massive 1 M-token context window",
            "Native multimodal (text, image, audio, video)",
            "Strong at data analysis and Google Workspace tasks",
            "Grounding with Google Search",
        ],
        "best_prompts": [
            "Feed entire codebases or documents for deep analysis",
            "Combine text + image in the same prompt",
            "Use the grounding feature for up-to-date web info",
            "Ask it to compare multiple documents simultaneously",
        ],
        "avoid": [
            "Expecting cutting-edge creative writing (GPT-4o is stronger)",
            "Forgetting to specify the output language/format",
        ],
    },
    {
        "llm": "Llama 3 / Mistral (Open-Source)",
        "icon": "🦙",
        "color": "#7c3aed",
        "strengths": [
            "Runs locally — full data privacy",
            "Free to use with no API costs",
            "Highly customisable via fine-tuning",
            "Great for coding tasks (CodeLlama, Deepseek-Coder)",
        ],
        "best_prompts": [
            "Use system prompts to set role and constraints",
            "Keep prompts concise — smaller models need clear instructions",
            'For coding: specify language, input/output format, and edge cases',
            "Use tools like Ollama or LM Studio for easy local deployment",
        ],
        "avoid": [
            "Expecting GPT-4 level reasoning from smaller 7B models",
            "Neglecting quantisation — use Q4/Q5 for good speed/quality balance",
        ],
    },
    {
        "llm": "Perplexity AI",
        "icon": "🔍",
        "color": "#20b2aa",
        "strengths": [
            "Real-time web search integrated into answers",
            "Provides citations for every claim",
            "Great for research and fact-checking",
            "Summarises multiple sources automatically",
        ],
        "best_prompts": [
            "Ask research questions that need current data",
            'Use "Focus: Academic" for scholarly sources',
            "Follow up with \"List the sources used\"",
            "Ask for a comparison of multiple viewpoints on a topic",
        ],
        "avoid": [
            "Using it for pure creative tasks (no search advantage)",
            "Trusting citations blindly — always verify",
        ],
    },
]

PROMPT_TEMPLATES = [
    {
        "category": "Learning & Teaching",
        "icon": "📚",
        "templates": [
            {
                "title": "ELI5 (Explain Like I'm 5)",
                "prompt": "Explain [TOPIC] as if I am a complete beginner with no prior knowledge. Use simple analogies and avoid jargon.",
            },
            {
                "title": "Socratic Tutor",
                "prompt": "Act as a Socratic tutor. I am learning [TOPIC]. Guide me with questions rather than answers to help me discover the concepts myself.",
            },
            {
                "title": "Common Mistakes",
                "prompt": "What are the top 5 most common mistakes beginners make when learning [TOPIC], and how can I avoid them?",
            },
            {
                "title": "Mental Models",
                "prompt": "What are the key mental models and frameworks I need to understand [TOPIC] deeply? Explain each one briefly.",
            },
        ],
    },
    {
        "category": "Code & Development",
        "icon": "💻",
        "templates": [
            {
                "title": "Code Review",
                "prompt": "Review the following [LANGUAGE] code for bugs, security issues, and style improvements. Explain each issue and suggest a fix:\n\n```\n[PASTE CODE HERE]\n```",
            },
            {
                "title": "Algorithm Explainer",
                "prompt": "Explain how [ALGORITHM] works step by step. Then show me a clean implementation in [LANGUAGE] with comments.",
            },
            {
                "title": "Debug Helper",
                "prompt": "I am getting this error: [ERROR MESSAGE]. Here is my code: [CODE]. What is causing the error and how do I fix it?",
            },
            {
                "title": "Architecture Design",
                "prompt": "Design a scalable architecture for [SYSTEM/FEATURE]. Include components, data flow, and technology choices with justification.",
            },
        ],
    },
    {
        "category": "Writing & Analysis",
        "icon": "✍️",
        "templates": [
            {
                "title": "Structured Summary",
                "prompt": "Summarise the following text in bullet points under these headings: Key Points, Main Arguments, Implications, and Open Questions:\n\n[PASTE TEXT]",
            },
            {
                "title": "Critical Analysis",
                "prompt": "Critically analyse [TOPIC/CLAIM]. Present the strongest arguments for and against, then give your balanced assessment.",
            },
            {
                "title": "First Principles",
                "prompt": "Break down [TOPIC] using first principles thinking. What are the fundamental truths, and how does everything else build from them?",
            },
            {
                "title": "Action Plan",
                "prompt": "I want to achieve [GOAL]. Create a detailed 30-day action plan with weekly milestones, daily habits, and success metrics.",
            },
        ],
    },
]

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/llm-tips")
def llm_tips():
    return jsonify(LLM_TIPS)


@app.route("/api/prompt-templates")
def prompt_templates():
    return jsonify(PROMPT_TEMPLATES)


@app.route("/api/learning-plan", methods=["POST"])
def learning_plan():
    data = request.get_json(force=True)
    topic = (data.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "topic is required"}), 400

    provider_key = _normalize_provider(data.get("provider"))
    provider = PROVIDERS[provider_key]

    env_api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    env_base_url = (os.getenv("OPENAI_BASE_URL") or "").strip()
    env_model = (os.getenv("OPENAI_MODEL") or "").strip()

    req_api_key = (data.get("apiKey") or data.get("api_key") or "").strip()
    req_model = (data.get("model") or "").strip()
    req_base_url = (data.get("baseUrl") or data.get("base_url") or "").strip()

    api_key = req_api_key or env_api_key
    model = req_model or env_model or provider["default_model"]
    base_url = req_base_url or env_base_url or provider["default_base_url"]

    if not api_key or api_key.startswith("sk-your"):
        # Return a helpful demo plan so the app works without an API key
        return jsonify(_demo_plan(topic))

    system_prompt = textwrap.dedent("""
        You are an expert educator and curriculum designer.
        Your goal is to create a Pareto-optimal (80/20) learning plan:
        focus on the 20% of knowledge that gives 80% of practical mastery.
        Always respond with valid JSON only — no markdown fences, no extra text.
    """).strip()

    user_prompt = textwrap.dedent(f"""
        Create a comprehensive Pareto learning plan for: "{topic}"

        Return a JSON object with exactly these keys:
        {{
          "topic": string,
          "summary": string (2-3 sentences on why this topic matters),
          "pareto_insight": string (the critical 20% to focus on first),
          "phases": [
            {{
              "phase": number,
              "title": string,
              "duration": string (e.g. "Week 1-2"),
              "goal": string,
              "topics": [string],
              "resources": [string],
              "project": string (hands-on mini-project)
            }}
          ],
          "key_concepts": [string] (top 8 must-know concepts),
          "common_pitfalls": [string] (top 5 mistakes learners make),
          "success_metrics": [string] (how to know you have mastered it),
          "next_steps": [string] (what to learn after mastery)
        }}

        Make the plan practical, specific, and actionable.
        Phases should cover: Foundations → Core Skills → Projects → Mastery.
    """).strip()

    try:
        client = _build_client(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        raw = response.choices[0].message.content or "{}"
        plan = json.loads(raw)
        return jsonify(plan)
    except json.JSONDecodeError:
        return jsonify({"error": "Model returned invalid JSON. Try again."}), 500
    except Exception as exc:
        app.logger.error("learning-plan error: %s", exc)
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


def _demo_plan(topic: str) -> dict:
    """Return a hard-coded example plan used when no API key is configured."""
    return {
        "topic": topic,
        "summary": (
            f"{topic} is a valuable skill worth mastering. "
            "This Pareto plan focuses on the 20% of knowledge that delivers 80% of practical results, "
            "so you can become productive as quickly as possible."
        ),
        "pareto_insight": (
            "Master the core primitives and one real-world project before diving into advanced topics. "
            "90% of day-to-day work uses the same foundational 20% of the subject."
        ),
        "phases": [
            {
                "phase": 1,
                "title": "Foundations",
                "duration": "Week 1–2",
                "goal": f"Understand the core concepts of {topic} and get your environment ready.",
                "topics": [
                    "Core terminology and mental models",
                    "Setup and tooling",
                    "Hello-world example",
                    "Official documentation walkthrough",
                ],
                "resources": [
                    "Official documentation / getting-started guide",
                    "FreeCodeCamp or YouTube crash-course",
                    "Anki flashcards for key terminology",
                ],
                "project": f"Build a minimal working example that demonstrates the basics of {topic}.",
            },
            {
                "phase": 2,
                "title": "Core Skills",
                "duration": "Week 3–5",
                "goal": "Apply the fundamentals in progressively harder exercises.",
                "topics": [
                    "Most-used patterns and best practices",
                    "Error handling and debugging",
                    "Reading and writing real code / content",
                    "Common libraries / tools in the ecosystem",
                ],
                "resources": [
                    "Hands-on exercises (Exercism, Leetcode, Kaggle, etc.)",
                    "Community forums (Reddit, Discord, Stack Overflow)",
                    "One highly-rated book or course chapter",
                ],
                "project": f"Extend your Phase 1 project with 2–3 real features relevant to {topic}.",
            },
            {
                "phase": 3,
                "title": "Real-World Project",
                "duration": "Week 6–8",
                "goal": "Solidify knowledge by shipping a complete project.",
                "topics": [
                    "End-to-end project design",
                    "Testing and quality assurance",
                    "Documentation",
                    "Peer review / feedback",
                ],
                "resources": [
                    "GitHub for version control",
                    "Portfolio hosting (Vercel, Netlify, GitHub Pages)",
                    "Peer community for code / work review",
                ],
                "project": f"Build and publish a complete, portfolio-worthy project using {topic}.",
            },
            {
                "phase": 4,
                "title": "Mastery & Beyond",
                "duration": "Week 9+",
                "goal": "Go deep on advanced topics and start teaching others.",
                "topics": [
                    "Advanced patterns and edge cases",
                    "Performance and optimisation",
                    "Contributing to open-source or community",
                    "Teaching: write a blog post or record a tutorial",
                ],
                "resources": [
                    "Advanced books or research papers",
                    "Conference talks (YouTube, InfoQ)",
                    "Mentorship or pair-programming with experts",
                ],
                "project": f"Write a tutorial or give a talk explaining {topic} to beginners.",
            },
        ],
        "key_concepts": [
            f"Core primitives of {topic}",
            "Mental model / how it works under the hood",
            "Most common use-cases",
            "Best practices and conventions",
            "Debugging and troubleshooting",
            "Ecosystem tools and libraries",
            "Performance considerations",
            "Security / quality implications",
        ],
        "common_pitfalls": [
            "Skipping fundamentals and jumping straight to advanced material",
            "Tutorial hell — watching without building",
            "Neglecting official documentation",
            "Isolation — not joining a community for feedback",
            "No real project — practising without a purpose",
        ],
        "success_metrics": [
            f"Can explain {topic} to a beginner without notes",
            "Built and shipped at least one real project",
            "Can debug common errors independently",
            "Comfortable reading advanced documentation",
            "Received positive peer feedback on your work",
        ],
        "next_steps": [
            f"Explore advanced sub-topics within {topic}",
            "Combine with complementary technologies",
            "Contribute to open-source projects",
            "Mentor others to deepen your own understanding",
        ],
        "_demo": True,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, port=port)
