/* ===================================================================
   app.js – AIBoost frontend logic
   =================================================================== */

// ─── Tab Navigation ───────────────────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    // Deactivate all tabs
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));

    // Activate selected tab
    btn.classList.add('active');
    const tabId = 'tab-' + btn.dataset.tab;
    document.getElementById(tabId).classList.remove('hidden');

    // Lazy-load tab content on first visit
    if (btn.dataset.tab === 'llm-guide' && !llmLoaded) loadLlmGuide();
    if (btn.dataset.tab === 'prompts' && !promptsLoaded) loadPrompts();
  });
});

// ─── State flags ──────────────────────────────────────────────────
let llmLoaded = false;
let promptsLoaded = false;

// ─── Learning Planner ─────────────────────────────────────────────
const plannerForm = document.getElementById('planner-form');
const topicInput  = document.getElementById('topic-input');
const generateBtn = document.getElementById('generate-btn');
const loadingEl   = document.getElementById('planner-loading');
const errorEl     = document.getElementById('planner-error');
const resultEl    = document.getElementById('planner-result');

plannerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const topic = topicInput.value.trim();
  if (!topic) return;

  // Reset UI
  errorEl.classList.add('hidden');
  resultEl.classList.add('hidden');
  loadingEl.classList.remove('hidden');
  generateBtn.disabled = true;

  try {
    const res = await fetch('/api/learning-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic }),
    });
    const data = await res.json();

    if (!res.ok || data.error) {
      showError(data.error || 'Something went wrong. Please try again.');
      return;
    }

    renderPlan(data);
  } catch (err) {
    showError('Network error. Make sure the server is running.');
  } finally {
    loadingEl.classList.add('hidden');
    generateBtn.disabled = false;
  }
});

function showError(msg) {
  loadingEl.classList.add('hidden');
  errorEl.textContent = '⚠️ ' + msg;
  errorEl.classList.remove('hidden');
}

function renderPlan(plan) {
  let html = '';

  // Demo notice
  if (plan._demo) {
    html += `<div class="demo-notice">
      ⚠️ <strong>Demo mode</strong> — add your OpenAI API key in <code>.env</code> to get an AI-generated plan tailored to "${escHtml(plan.topic)}".
    </div>`;
  }

  // Header
  html += `<div class="plan-header card">
    <div class="plan-topic">📘 ${escHtml(plan.topic)}</div>
    <p class="plan-summary">${escHtml(plan.summary)}</p>
    <div class="pareto-box">
      <strong>⚡ Pareto Insight (The Critical 20%):</strong><br/>
      ${escHtml(plan.pareto_insight)}
    </div>
  </div>`;

  // Phases
  if (plan.phases && plan.phases.length) {
    html += `<h2 style="margin: 1.5rem 0 1rem; font-size: 1.2rem;">🗺️ Learning Phases</h2>
    <div class="phases-grid">`;

    plan.phases.forEach(p => {
      const topics = (p.topics || []).map(t => `<li>${escHtml(t)}</li>`).join('');
      const resources = (p.resources || []).map(r => `<li>${escHtml(r)}</li>`).join('');

      html += `<div class="phase-card">
        <div class="phase-num">${p.phase}</div>
        <div class="phase-title">${escHtml(p.title)}</div>
        <div class="phase-duration">⏱ ${escHtml(p.duration)}</div>
        <div class="phase-goal">${escHtml(p.goal)}</div>
        <div class="phase-section-title">Topics</div>
        <ul class="phase-list">${topics}</ul>
        <div class="phase-section-title">Resources</div>
        <ul class="phase-list">${resources}</ul>
        <div class="phase-project"><strong>🛠 Project:</strong> ${escHtml(p.project)}</div>
      </div>`;
    });

    html += `</div>`;
  }

  // Info columns
  html += `<div class="info-cols">`;

  if (plan.key_concepts && plan.key_concepts.length) {
    html += infoCard('🔑 Key Concepts', plan.key_concepts);
  }
  if (plan.common_pitfalls && plan.common_pitfalls.length) {
    html += infoCard('⚠️ Common Pitfalls', plan.common_pitfalls);
  }
  if (plan.success_metrics && plan.success_metrics.length) {
    html += infoCard('✅ Success Metrics', plan.success_metrics);
  }
  if (plan.next_steps && plan.next_steps.length) {
    html += infoCard('🚀 Next Steps', plan.next_steps);
  }

  html += `</div>`;

  resultEl.innerHTML = html;
  resultEl.classList.remove('hidden');
  resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function infoCard(title, items) {
  const listItems = items.map(i => `<li>${escHtml(i)}</li>`).join('');
  return `<div class="info-card">
    <div class="info-card-title">${title}</div>
    <ul class="info-list">${listItems}</ul>
  </div>`;
}

// ─── LLM Guide ────────────────────────────────────────────────────
async function loadLlmGuide() {
  try {
    const res = await fetch('/api/llm-tips');
    const tips = await res.json();
    const grid = document.getElementById('llm-grid');

    grid.innerHTML = tips.map(llm => {
      const strengths = llm.strengths.map(s => `<span class="tag">${escHtml(s)}</span>`).join('');
      const prompts   = llm.best_prompts.map(p => `<li>${escHtml(p)}</li>`).join('');
      const avoid     = llm.avoid.map(a => `<li>${escHtml(a)}</li>`).join('');

      return `<div class="llm-card">
        <div class="llm-card-header">
          <span class="llm-icon">${llm.icon}</span>
          <span class="llm-name">${escHtml(llm.llm)}</span>
        </div>
        <div class="llm-section">
          <div class="llm-section-title" style="color:${escHtml(llm.color)}">✦ Strengths</div>
          <div class="tag-list">${strengths}</div>
        </div>
        <div class="llm-section">
          <div class="llm-section-title" style="color:${escHtml(llm.color)}">💡 Best Prompting Tips</div>
          <ul class="tip-list">${prompts}</ul>
        </div>
        <div class="llm-section">
          <div class="llm-section-title" style="color:#ef4444">✗ Avoid</div>
          <ul class="tip-list">${avoid}</ul>
        </div>
      </div>`;
    }).join('');

    llmLoaded = true;
  } catch (err) {
    document.getElementById('llm-grid').innerHTML =
      '<div class="error-banner">Failed to load LLM guide.</div>';
  }
}

// ─── Prompt Library ───────────────────────────────────────────────
async function loadPrompts() {
  try {
    const res = await fetch('/api/prompt-templates');
    const categories = await res.json();
    const grid = document.getElementById('prompts-grid');

    grid.innerHTML = categories.map(cat => {
      const cards = cat.templates.map(t => `
        <div class="prompt-card" data-prompt="${escAttr(t.prompt)}" title="Click to copy">
          <div class="copy-badge">📋 Copy</div>
          <div class="prompt-card-title">${escHtml(t.title)}</div>
          <div class="prompt-card-text">${escHtml(t.prompt)}</div>
        </div>
      `).join('');

      return `<div class="prompt-category">
        <div class="prompt-category-title">${cat.icon} ${escHtml(cat.category)}</div>
        <div class="prompt-cards-row">${cards}</div>
      </div>`;
    }).join('');

    // Add click-to-copy behaviour
    grid.querySelectorAll('.prompt-card').forEach(card => {
      card.addEventListener('click', () => {
        const text = card.dataset.prompt;
        navigator.clipboard.writeText(text).then(() => showToast('✅ Copied to clipboard!'));
      });
    });

    promptsLoaded = true;
  } catch (err) {
    document.getElementById('prompts-grid').innerHTML =
      '<div class="error-banner">Failed to load prompt templates.</div>';
  }
}

// ─── Toast ────────────────────────────────────────────────────────
const toastEl = document.getElementById('toast');
let toastTimer = null;

function showToast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.remove('hidden');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.add('hidden'), 2200);
}

// ─── Helpers ──────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escAttr(str) {
  if (!str) return '';
  return String(str).replace(/"/g, '&quot;');
}
