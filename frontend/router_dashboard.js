const API = 'http://localhost:8000';

// ── Helpers ────────────────────────────────────────────────────────────────

function $(id) { return document.getElementById(id); }

function showFeedback(el, message, isError = false) {
  el.textContent = message;
  el.classList.remove('hidden', 'error');
  if (isError) el.classList.add('error');
  setTimeout(() => el.classList.add('hidden'), 3000);
}

function showError(el, message) {
  el.textContent = message;
  el.classList.remove('hidden');
}

function hideError(el) {
  el.classList.add('hidden');
  el.textContent = '';
}

function makeGroupRow(container) {
  const row = document.createElement('div');
  row.className = 'group-row';
  row.innerHTML = `
    <input class="field-input" type="text" placeholder="Group name" />
    <input class="field-input" type="number" placeholder="GLPI ID" min="1" />
    <button class="btn-icon" title="Remove">×</button>
  `;
  row.querySelector('.btn-icon').addEventListener('click', () => row.remove());
  container.appendChild(row);
}

function collectGroups(container) {
  const rows = container.querySelectorAll('.group-row');
  const groups = [];
  let valid = true;

  rows.forEach(row => {
    const name = row.querySelectorAll('input')[0].value.trim();
    const id   = parseInt(row.querySelectorAll('input')[1].value.trim(), 10);
    if (!name || isNaN(id)) { valid = false; return; }
    groups.push({ glpi_group_name: name, glpi_group_id: id });
  });

  return valid ? groups : null;
}

// ── Status indicator ───────────────────────────────────────────────────────

function setStatus(ready) {
  const dot   = $('status-dot');
  const label = $('status-label');
  dot.className   = 'status-dot ' + (ready ? 'ready' : 'error');
  label.textContent = ready ? 'Router active' : 'Not configured';
}

// ── Tab navigation ─────────────────────────────────────────────────────────

document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    $('tab-' + btn.dataset.tab).classList.add('active');
  });
});

// ── LLM config ────────────────────────────────────────────────────────────

async function loadLlmConfig() {
  try {
    const res  = await fetch(`${API}/llm`);
    const data = await res.json();
    $('model-name').value    = data.model_name   || '';
    $('system-prompt').value = data.system_prompt || '';

    // Match provider by base_url
    const providerMap = {
      'http://localhost:11434/v1/chat/completions': 'Ollama',
      'http://localhost:1234/v1/chat/completions':  'LM Studio',
      'http://localhost:8000/v1/chat/completions':  'vLLM',
      'http://localhost:8080/v1/chat/completions':  'llama.cpp',
    };
    const matched = providerMap[data.base_url] || '';
    $('provider-select').value = matched;
  } catch (e) {
    console.error('Failed to load LLM config', e);
  }
}

$('llm-form').addEventListener('submit', async e => {
  e.preventDefault();
  const btn      = $('llm-save-btn');
  const feedback = $('llm-feedback');
  const provider = $('provider-select').value;
  const model    = $('model-name').value.trim();
  const prompt   = $('system-prompt').value.trim();

  if (!provider || !model) {
    showFeedback(feedback, 'Provider and model name are required.', true);
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    const res = await fetch(`${API}/llm`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, model_name: model, system_prompt: prompt }),
    });

    if (res.ok) {
      showFeedback(feedback, 'Saved.');
    } else {
      showFeedback(feedback, 'Save failed. Check your inputs.', true);
    }
  } catch (e) {
    showFeedback(feedback, 'Could not reach the server.', true);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save changes';
  }
});

// ── Groups tab ────────────────────────────────────────────────────────────

async function loadGroups() {
  const tbody = $('groups-tbody');
  tbody.innerHTML = '';
  try {
    const res    = await fetch(`${API}/setup-status`);
    const data   = await res.json();
    if (!data.configured) {
      tbody.innerHTML = '<tr class="empty-row"><td colspan="2">No groups configured yet.</td></tr>';
      setStatus(false);
      return;
    }

    // Fetch all groups to display — assumes a GET /routing-groups endpoint
    // If that endpoint doesn't exist yet, this section shows empty gracefully.
    try {
      const gr  = await fetch(`${API}/routing-groups`);
      const groups = await gr.json();
      groups.forEach(g => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${g.glpi_group_name}</td><td>${g.glpi_group_id}</td>`;
        tbody.appendChild(tr);
      });
      setStatus(true);
    } catch {
      tbody.innerHTML = '<tr class="empty-row"><td colspan="2">Could not load groups.</td></tr>';
    }
  } catch (e) {
    setStatus(false);
  }
}

$('groups-add-row').addEventListener('click', () => {
  makeGroupRow($('new-groups-list'));
});

$('groups-save-btn').addEventListener('click', async () => {
  const btn      = $('groups-save-btn');
  const feedback = $('groups-feedback');
  const errEl    = $('groups-error');
  hideError(errEl);

  const groups = collectGroups($('new-groups-list'));
  if (!groups || groups.length === 0) {
    showError(errEl, 'Add at least one complete group before saving.');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    const res = await fetch(`${API}/routing-groups`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ groups }),
    });

    if (res.ok) {
      $('new-groups-list').innerHTML = '';
      showFeedback(feedback, 'Groups saved.');
      loadGroups();
    } else {
      showError(errEl, 'Failed to save groups.');
    }
  } catch (e) {
    showError(errEl, 'Could not reach the server.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save groups';
  }
});

// ── Wizard ────────────────────────────────────────────────────────────────

$('wizard-add-row').addEventListener('click', () => {
  makeGroupRow($('wizard-groups-list'));
});

$('wizard-submit').addEventListener('click', async () => {
  const btn   = $('wizard-submit');
  const errEl = $('wizard-error');
  hideError(errEl);

  const groups = collectGroups($('wizard-groups-list'));
  if (!groups || groups.length === 0) {
    showError(errEl, 'Add at least one complete group to continue.');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    const res = await fetch(`${API}/routing-groups`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ groups }),
    });

    if (res.ok) {
      $('wizard-overlay').classList.add('hidden');
      $('app').classList.remove('hidden');
      loadLlmConfig();
      loadGroups();
    } else {
      showError(errEl, 'Failed to save groups. Try again.');
    }
  } catch (e) {
    showError(errEl, 'Could not reach the server.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save groups and continue';
  }
});

// ── Init ──────────────────────────────────────────────────────────────────

async function init() {
  try {
    const res  = await fetch(`${API}/setup-status`);
    const data = await res.json();

    if (!data.configured) {
      // First run — show wizard, add one empty row to start
      $('wizard-overlay').classList.remove('hidden');
      makeGroupRow($('wizard-groups-list'));
    } else {
      $('app').classList.remove('hidden');
      loadLlmConfig();
      loadGroups();
    }
  } catch (e) {
    // Can't reach server — show app anyway, errors will surface per section
    $('app').classList.remove('hidden');
    setStatus(false);
  }
}

init();