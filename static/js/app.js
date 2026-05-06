/* ═══════════════════════════════════════════════════════════
   GradeGuard MVP — Grade Calculator + What-If Solver
   ═══════════════════════════════════════════════════════════ */

// ── State ──────────────────────────────────────────────────
let catSeq  = 0;
let wiSeq   = 0;
let modalTarget = null;   // { catId, isWi }

// ── Tab switching ──────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.add('hidden'));
  document.getElementById('tab-' + name).classList.add('active');
  document.getElementById('panel-' + name).classList.remove('hidden');
}

// ── Category management ────────────────────────────────────
function addCategory() {
  const id = 'cat_' + (++catSeq);
  appendCat('category-list', id, null, false);
  updateWeightBar('category-list', 'weight-fill', 'weight-tag');
}

function addWiCategory() {
  const id = 'wcat_' + (++wiSeq);
  appendCat('wi-category-list', id, null, true);
  updateWeightBar('wi-category-list', 'wi-weight-fill', 'wi-weight-tag');
}

function appendCat(listId, id, data, isWi) {
  const name    = data?.name    || '';
  const weight  = data?.weight  ?? '';
  const bestOf  = data?.best_of || '';
  const dropLow = data?.drop_lowest || false;
  const bestOn  = bestOf ? 'checked' : '';
  const dropOn  = dropLow ? 'checked' : '';
  const bVis    = bestOf ? 'show' : '';
  const cnt     = (data?.assignments || []).length;
  const hasCls  = cnt > 0 ? ' has-scores' : '';
  const onwt    = isWi ? `onWeightChange('wi-category-list','wi-weight-fill','wi-weight-tag')`
                       : `onWeightChange('category-list','weight-fill','weight-tag')`;

  const el = document.createElement('div');
  el.className = 'cat-card';
  el.id = id;
  el.innerHTML = `
    <div class="cat-top">
      <input type="text" class="inp" placeholder="Category name" value="${esc(name)}"/>
      <input type="number" class="inp" placeholder="Wt %" min="0" max="100"
             value="${weight}" oninput="${onwt}"/>
      <button class="btn-del" onclick="delCat('${id}','${listId}',${isWi})" title="Remove">✕</button>
    </div>
    <div class="cat-body">
      <div class="score-pill">
        <span class="score-count${hasCls}" id="cnt_${id}">${cnt} score${cnt!==1?'s':''}</span>
        <button class="btn-scores" onclick="openModal('${id}',${isWi})">✎ Enter Scores</button>
      </div>
      <div class="toggle-row">
        <label class="toggle-label">
          <input type="checkbox" id="drop_${id}" ${dropOn} onchange="onDropChange('${id}')"/>
          <span class="toggle-track"></span>
          Drop lowest
        </label>
        <label class="toggle-label">
          <input type="checkbox" id="bestToggle_${id}" ${bestOn} onchange="onBestToggle('${id}')"/>
          <span class="toggle-track"></span>
          Best of N
        </label>
        <div class="best-n-wrap ${bVis}" id="bestNWrap_${id}">
          <span>Keep top</span>
          <input type="number" class="inp-xs" id="bestN_${id}" value="${bestOf}" min="1" placeholder="N"/>
          <span>scores</span>
        </div>
      </div>
    </div>`;

  el._assignments = data?.assignments || [];
  document.getElementById(listId).appendChild(el);
}

function delCat(id, listId, isWi) {
  document.getElementById(id)?.remove();
  if (isWi) updateWeightBar('wi-category-list','wi-weight-fill','wi-weight-tag');
  else      updateWeightBar('category-list','weight-fill','weight-tag');
}

function onDropChange(id) {
  if (document.getElementById('drop_' + id)?.checked) {
    const bt = document.getElementById('bestToggle_' + id);
    if (bt) bt.checked = false;
    document.getElementById('bestNWrap_' + id)?.classList.remove('show');
  }
}
function onBestToggle(id) {
  const on = document.getElementById('bestToggle_' + id)?.checked;
  document.getElementById('bestNWrap_' + id)?.classList.toggle('show', on);
  if (on) {
    const d = document.getElementById('drop_' + id);
    if (d) d.checked = false;
  }
}

function onWeightChange(listId, fillId, tagId) {
  updateWeightBar(listId, fillId, tagId);
}

function updateWeightBar(listId, fillId, tagId) {
  const cards = document.querySelectorAll('#' + listId + ' .cat-card');
  let total = 0;
  cards.forEach(c => {
    const w = parseFloat(c.querySelectorAll('input')[1]?.value) || 0;
    total += w;
  });
  const pct = Math.min(total, 100);
  const fill = document.getElementById(fillId);
  const tag  = document.getElementById(tagId);
  if (!fill || !tag) return;
  fill.style.width = pct + '%';
  fill.classList.toggle('ok',   total === 100);
  fill.classList.toggle('over', total > 100);
  tag.textContent = total + ' / 100%';
  tag.className = 'weight-sum-tag' + (total === 100 ? ' ok' : total > 100 ? ' over' : '');
}

// ── Collect categories from DOM ────────────────────────────
function collectCats(listId) {
  const cards = document.querySelectorAll('#' + listId + ' .cat-card');
  const result = [];
  cards.forEach(card => {
    const inputs = card.querySelectorAll('input[type=text], input[type=number]');
    const name   = inputs[0]?.value?.trim() || '';
    const weight = parseFloat(inputs[1]?.value) || 0;
    const id     = card.id;
    const dropLow  = document.getElementById('drop_' + id)?.checked || false;
    const bestOn   = document.getElementById('bestToggle_' + id)?.checked || false;
    const bestOf   = bestOn ? (parseInt(document.getElementById('bestN_' + id)?.value) || 0) : 0;
    if (name) result.push({
      name, weight,
      drop_lowest: dropLow,
      best_of: bestOf,
      assignments: card._assignments || []
    });
  });
  return result;
}

// ── Score modal ────────────────────────────────────────────
let tempAssignments = [];

function openModal(catId, isWi) {
  modalTarget = { catId, isWi };
  const card = document.getElementById(catId);
  const catName = card?.querySelectorAll('input')[0]?.value || 'Category';
  tempAssignments = (card?._assignments || []).map(a => ({...a}));

  document.getElementById('modal-title').textContent = catName || 'Enter Scores';
  document.getElementById('modal-count').value = tempAssignments.length || '';
  renderRows(tempAssignments.length);
  document.getElementById('modal-backdrop').classList.remove('hidden');
}

function closeModal() {
  document.getElementById('modal-backdrop').classList.add('hidden');
  modalTarget = null;
  tempAssignments = [];
}

function genRows() {
  const n = parseInt(document.getElementById('modal-count').value) || 0;
  if (n < 1 || n > 200) { alert('Enter a number between 1 and 200.'); return; }
  while (tempAssignments.length < n) tempAssignments.push({ earned: '', max: '' });
  tempAssignments = tempAssignments.slice(0, n);
  renderRows(n);
}

function renderRows(n) {
  const wrap = document.getElementById('score-rows');
  wrap.innerHTML = '';
  for (let i = 0; i < n; i++) {
    const a = tempAssignments[i] || { earned: '', max: '' };
    const row = document.createElement('div');
    row.className = 'score-row';
    row.innerHTML = `
      <span class="sr-num">${i+1}.</span>
      <input type="number" class="inp-score" id="e${i}" value="${a.earned !== '' ? a.earned : ''}"
             placeholder="46" min="0" oninput="liveCalc(${i})"/>
      <span class="sr-slash">/</span>
      <input type="number" class="inp-score" id="m${i}" value="${a.max !== '' ? a.max : ''}"
             placeholder="48" min="0" oninput="liveCalc(${i})"/>
      <span class="sr-pct" id="p${i}">${pctLabel(a.earned, a.max)}</span>`;
    wrap.appendChild(row);
  }
}

function liveCalc(i) {
  const e = parseFloat(document.getElementById('e' + i)?.value);
  const m = parseFloat(document.getElementById('m' + i)?.value);
  document.getElementById('p' + i).textContent = pctLabel(e, m);
}

function pctLabel(e, m) {
  if (e === '' || m === '' || isNaN(e) || isNaN(m) || m === 0) return '—';
  return (e / m * 100).toFixed(1) + '%';
}

function saveScores() {
  const n = document.querySelectorAll('#score-rows .score-row').length;
  const saved = [];
  for (let i = 0; i < n; i++) {
    const e = parseFloat(document.getElementById('e' + i)?.value);
    const m = parseFloat(document.getElementById('m' + i)?.value);
    if (!isNaN(e) && !isNaN(m) && m > 0) saved.push({ earned: e, max: m });
  }
  if (modalTarget) {
    const card = document.getElementById(modalTarget.catId);
    if (card) {
      card._assignments = saved;
      const cnt = document.getElementById('cnt_' + modalTarget.catId);
      if (cnt) {
        cnt.textContent = saved.length + ' score' + (saved.length !== 1 ? 's' : '');
        cnt.className = 'score-count' + (saved.length > 0 ? ' has-scores' : '');
      }
    }
  }
  closeModal();
}

// ── MODULE 1: Grade Calculator ─────────────────────────────
async function calculateGrade() {
  const courseName = document.getElementById('course-name').value.trim() || 'My Course';
  const categories = collectCats('category-list');
  const resultEl   = document.getElementById('grade-result');

  if (!categories.length) { showErr('grade-result', 'Add at least one category.'); return; }
  const missing = categories.filter(c => !c.assignments.length);
  if (missing.length) {
    showErr('grade-result', `No scores entered for: ${missing.map(c => c.name).join(', ')}`);
    return;
  }

  try {
    const res  = await fetch('/api/grade', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ course_name: courseName, categories })
    });
    const data = await res.json();

    const warnHtml = data.valid ? '' :
      `<div class="invalid-note">⚠ Weights don't sum to 100% — result is partial</div>`;

    const rows = data.category_averages.map(c => {
      let note = `${c.total_submitted} score${c.total_submitted !== 1 ? 's' : ''}`;
      if (c.best_of)      note += ` · best ${c.best_of} kept`;
      if (c.drop_lowest)  note += ` · drop lowest`;
      return `<div class="breakdown-row">
        <div><div class="br-name">${esc(c.name)}</div><div class="br-note">${note} · weight ${c.weight}%</div></div>
        <div class="br-pct">${c.average.toFixed(1)}%</div>
        <div class="br-bar-wrap"><div class="br-bar"><div class="br-bar-fill" style="width:0%"
             data-w="${c.average.toFixed(1)}"></div></div></div>
      </div>`;
    }).join('');

    resultEl.innerHTML = `
      <div class="grade-summary">
        <div class="grade-ring">
          <div class="ring-pct" id="anim-g">0</div>
          <div class="ring-letter">${data.letter_grade}</div>
        </div>
        <div class="grade-text">
          <div class="grade-course">${esc(courseName)}</div>
          <div class="grade-sub">Weighted overall grade</div>
          ${warnHtml}
        </div>
      </div>
      <div class="breakdown">
        <div class="breakdown-head"><span>Category</span><span style="text-align:right">Average</span><span></span></div>
        ${rows}
      </div>`;
    resultEl.classList.remove('hidden');

    countUp(document.getElementById('anim-g'), data.overall_grade, 1);
    setTimeout(() => {
      document.querySelectorAll('.br-bar-fill').forEach(b => {
        b.style.width = b.dataset.w + '%';
      });
    }, 80);
  } catch(e) {
    showErr('grade-result', 'Server error. Is Flask running?');
    console.error(e);
  }
}

// ── MODULE 2: What-If Solver ───────────────────────────────
async function solveWhatIf() {
  const categories  = collectCats('wi-category-list');
  const targetGrade = parseFloat(document.getElementById('target-grade').value);
  const futureWt    = parseFloat(document.getElementById('future-weight').value);
  const resultEl    = document.getElementById('whatif-result');

  if (!categories.length) { showErr('whatif-result', 'Add at least one category.'); return; }
  if (isNaN(targetGrade) || isNaN(futureWt)) {
    showErr('whatif-result', 'Enter both target grade and future assignment weight.'); return;
  }
  const missing = categories.filter(c => !c.assignments.length);
  if (missing.length) {
    showErr('whatif-result', `No scores entered for: ${missing.map(c => c.name).join(', ')}`);
    return;
  }

  try {
    const res  = await fetch('/api/whatif', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ categories, target_grade: targetGrade, future_weight: futureWt })
    });
    const data = await res.json();

    let cls, label, sub;
    if (data.impossible) {
      cls = 'red'; label = 'Mathematically Impossible';
      sub = `Even a perfect score won't get you to ${targetGrade}%.`;
    } else if (data.needed_score > 90) {
      cls = 'amber'; label = "You'll Need to Grind";
      sub = `High bar — possible with serious focus.`;
    } else {
      cls = 'green'; label = 'Totally Doable';
      sub = `Stay consistent — you've got this.`;
    }

    resultEl.innerHTML = `
      <div class="wi-card">
        <div class="wi-num ${cls}" id="anim-wi">0</div>
        <div class="wi-label">${label}</div>
        <div class="wi-sub">${sub}</div>
      </div>`;
    resultEl.classList.remove('hidden');
    countUp(document.getElementById('anim-wi'), data.needed_score, 2);
  } catch(e) {
    showErr('whatif-result', 'Server error.');
    console.error(e);
  }
}

// ── Utilities ──────────────────────────────────────────────
function countUp(el, end, dec) {
  if (!el) return;
  const dur = 650, t0 = performance.now();
  const tick = now => {
    const p = Math.min((now - t0) / dur, 1);
    el.textContent = (end * (1 - Math.pow(1 - p, 3))).toFixed(dec);
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

function showErr(id, msg) {
  const el = document.getElementById(id);
  el.classList.remove('hidden');
  el.innerHTML = `<div class="err-box">⚠ ${msg}</div>`;
}

function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  addCategory(); addCategory();
  addWiCategory(); addWiCategory();
});
