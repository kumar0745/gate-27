const API = '/api';
const state = {
  view: 'overview',
  user: null,
  papers: [],
  profile: { paper_code: 'CS', target: 'IIT admission', daily_hours: 5 },
  dashboard: null,
  tasks: [],
  syllabus: null,
  materialCatalog: null,
  materialDetail: null,
  pyqCatalog: null,
  pyqItems: [],
  pyqSummary: null,
  pyqYear: 2026,
  pyqSession: 'all',
  pyqType: 'all',
  pyqSection: 'all',
  pyqQuery: '',
  pyqBookmarked: false,
  mindmapData: null,
  mindmapSection: null,
  mindmapSelected: null,
  mindmapZoom: 1,
  practiceCatalog: null,
  practiceDaily: null,
  practiceSummary: null,
  practiceItems: [],
  practiceFilters: { section_code: 'all', topic_id: 'all', difficulty: 'all', question_type: 'all', q: '' },
  practiceSession: null,
  practiceCurrentIndex: 0,
  practiceQuestionOpenedAt: Date.now(),
  practiceTimerHandle: null,
  practiceFinishedResult: null,
  practiceSearchHandle: null,
  mockCatalog: null,
  mockSession: null,
  mockCurrentIndex: 0,
  mockTimerHandle: null,
  mockQuestionOpenedAt: Date.now(),
  mockAutoSaveTimer: null,
  mockResult: null,
  plannerOverview: null,
  plannerSelectedDate: null,
  tutorStatus: null,
  tutorConversations: [],
  tutorConversationId: null,
  tutorMessages: [],
  tutorImageDataUrl: null,
  tutorImageName: '',
  tutorBusy: false,
  tutorSimilarResult: null,
  analyticsData: null,
  communityFeed: null,
  communitySelectedPost: null,
  communityScope: 'paper',
  communityCategory: '',
  communityQuery: '',
  adminOverview: null,
  adminUsers: null,
  adminReports: [],
  adminCatalog: [],
  adminQueue: null,
  adminPaperCode: 'CS',
  adminContentType: 'all',
  adminUserQuery: '',
  searchOpen: false,
};

const ICONS = {
  grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  book: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21z"/><path d="M4 5.5v13A2.5 2.5 0 0 1 6.5 16H20M8 7h8M8 10h8"/>',
  nodes: '<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="M10.5 7 6.5 15.5M13.5 7l4 8.5M7.5 18h9"/>',
  layers: '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>',
  timer: '<circle cx="12" cy="13" r="8.5"/><path d="M12 8v5l3 2M9 2h6M12 2v2"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18M8 14h2M14 14h2M8 17h2"/>',
  repeat: '<path d="m17 2 4 4-4 4"/><path d="M3 11V9a3 3 0 0 1 3-3h15M7 22l-4-4 4-4"/><path d="M21 13v2a3 3 0 0 1-3 3H3"/>',
  chart: '<path d="M3 3v18h18"/><path d="m7 14 4-4 3 3 6-7"/>',
  sparkles: '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="m19 14 .9 2.1L22 17l-2.1.9L19 20l-.9-2.1L16 17l2.1-.9zM5 2l.7 1.8L7.5 4.5l-1.8.7L5 7l-.7-1.8-1.8-.7 1.8-.7z"/>',
  bookmark: '<path d="M6 4.5A1.5 1.5 0 0 1 7.5 3h9A1.5 1.5 0 0 1 18 4.5V21l-6-4-6 4z"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M10 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM20 8a3 3 0 0 1-2 2.83M22 21v-2a4 4 0 0 0-3-3.87"/>',
  search: '<circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/>',
  moon: '<path d="M20.8 13A8.7 8.7 0 0 1 11 3.2 8.8 8.8 0 1 0 20.8 13Z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  close: '<path d="m18 6-12 12M6 6l12 12"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  graduation: '<path d="m2 10 10-6 10 6-10 6z"/><path d="M6 12v5c4 3 8 3 12 0v-5M22 10v6"/>',
  bookOpen: '<path d="M12 7v14M3 18V5a2 2 0 0 1 2-2h3a4 4 0 0 1 4 4 4 4 0 0 1 4-4h3a2 2 0 0 1 2 2v13h-5a4 4 0 0 0-4 3 4 4 0 0 0-4-3z"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h8"/>',
  wand: '<path d="m15 4 5 5M4 20 16.5 7.5M7 3v3M3 7h3M17 16v3M15 18h4"/>',
  shield: '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m9 12 2 2 4-4"/>',
  flag: '<path d="M4 22V4m0 0c6-4 10 4 16 0v11c-6 4-10-4-16 0"/>',
};

function icon(name, size = 16) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ICONS.file}</svg>`;
}

function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try { const data = await response.json(); detail = data.detail || detail; } catch (_) { /* no body */ }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

function paperByCode(code) {
  return state.papers.find((paper) => paper.code === code) || { code, name: 'Selected GATE paper' };
}

function paperOptions(selected) {
  return state.papers.map((paper) => `<option value="${paper.code}" ${paper.code === selected ? 'selected' : ''}>${paper.code} — ${escapeHTML(paper.name)}</option>`).join('');
}

function formatDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' });
}

function toast(message) {
  const region = document.getElementById('toast-region');
  const node = document.createElement('div');
  node.className = 'toast';
  node.textContent = message;
  region.appendChild(node);
  window.setTimeout(() => node.remove(), 3200);
}

function setIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach((node) => {
    const name = node.getAttribute('data-icon');
    node.innerHTML = icon(name, 16);
  });
}

function setNav(view) {
  if (view !== 'practice') clearPracticeTimer();
  if (view !== 'tests') {
    clearMockTimer();
    if (state.mockAutoSaveTimer) { window.clearTimeout(state.mockAutoSaveTimer); state.mockAutoSaveTimer = null; }
    // Capture the visible response before another view replaces the exam form.
    if (state.view === 'tests' && state.mockSession?.status === 'active') saveMockCurrentResponse();
  }
  state.view = view;
  document.querySelectorAll('.nav-item').forEach((item) => item.classList.toggle('active', item.dataset.view === view));
  const active = document.querySelector(`.nav-item[data-view="${view}"]`);
  document.getElementById('breadcrumb-current').textContent = active ? active.querySelector('span:nth-child(2)')?.textContent || 'Overview' : 'Overview';
  document.getElementById('sidebar').classList.remove('open');
  renderView();
}

function renderTaskRows(tasks) {
  if (!tasks.length) {
    return `<div class="empty-state">${icon('check', 19)}<strong>Your task list is clear</strong><p>Add a small, achievable goal to keep your preparation moving.</p></div>`;
  }
  const plannerTasks = Boolean(tasks[0]?.plan_id);
  return tasks.map((task) => {
    const completed = plannerTasks ? task.status === 'completed' : Boolean(task.completed);
    const action = plannerTasks ? 'planner-toggle-task' : 'toggle-task';
    const taskType = plannerTasks ? ({learn:'Learning',practice:'Practice',revision:'Revision',mock:'Test',custom:'Personal task'}[task.task_type] || 'Study') : (task.subject || 'General');
    return `<div class="task-row ${completed ? 'is-complete' : ''}">
      <button class="task-check ${completed ? 'checked' : ''}" data-action="${action}" ${plannerTasks ? `data-task-id="${task.id}" data-current-status="${escapeHTML(task.status)}"` : `data-id="${task.id}"`} aria-label="${completed ? 'Mark incomplete' : 'Mark complete'}">${completed ? icon('check', 11) : ''}</button>
      <div class="task-main"><b>${escapeHTML(task.title)}</b><small>${escapeHTML(taskType)} · ${task.duration_minutes} min</small></div>
      <span class="priority ${escapeHTML(task.priority || 'Normal')}">${escapeHTML(task.priority || 'Normal')}</span>
      <span class="task-duration">${completed ? 'Done' : 'Today'}</span>
    </div>`;
  }).join('');
}

function renderOverview() {
  const dash = state.dashboard || {};
  const profile = state.profile;
  const paper = paperByCode(profile.paper_code);
  const plannedTasks = state.plannerOverview?.plan ? (state.plannerOverview.selected_day_tasks || []) : null;
  const tasks = plannedTasks || dash.tasks || state.tasks;
  const count = tasks.length;
  const completed = plannedTasks ? tasks.filter((task) => task.status === 'completed').length : (dash.today_completed_count ?? tasks.filter((task) => task.completed).length);
  const examDays = dash.days_until_first_scheduled_exam ?? '—';
  const targetLabel = profile.target || 'IIT admission';
  const dateText = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' });

  return `
    <div class="page-heading">
      <div><span class="eyebrow">YOUR PREPARATION SPACE · ${escapeHTML(dateText.toUpperCase())}</span><h1>Your preparation, in focus.</h1><p>A clear plan turns a big goal into a series of doable steps.</p></div>
      <div class="heading-actions"><select class="select-control" id="paper-switcher" aria-label="Select GATE paper">${paperOptions(profile.paper_code)}</select><button class="btn btn-primary" data-action="create-task">${icon('plus', 14)} Add task</button></div>
    </div>

    <section class="hero-panel">
      <div class="hero-content">
        <div class="hero-kicker"><span class="pulse"></span> YOUR GATE 2027 JOURNEY</div>
        <h2>Make today count. One concept at a time.</h2>
        <p>Your ${escapeHTML(paper.code)} preparation workspace is ready. Start with the official syllabus, make a realistic plan, and build consistency through focused practice.</p>
        <div class="hero-actions"><button class="btn btn-primary" data-action="go-view" data-view="syllabus">Explore your syllabus ${icon('arrow', 13)}</button><button class="btn btn-hero-quiet" data-action="open-profile">Personalise my plan</button></div>
      </div>
      <div class="countdown-card">
        <small>TIME UNTIL FIRST SCHEDULED EXAM</small>
        <div class="countdown-value"><strong>${examDays}</strong><span>days left</span></div>
        <p>6 February 2027 · Current published schedule</p>
        <div class="countdown-foot"><span>GATE 2027</span><a href="https://gate2027.iitm.ac.in/important_dates" target="_blank" rel="noreferrer">Verify dates ↗</a></div>
      </div>
    </section>

    <section class="metrics-grid" aria-label="Preparation overview">
      <div class="metric-card"><span class="metric-icon blue">${icon('book', 17)}</span><div class="metric-copy"><small>Selected paper</small><strong>${escapeHTML(paper.code)}</strong><span>${escapeHTML(paper.name)}</span></div></div>
      <div class="metric-card"><span class="metric-icon teal">${icon('calendar', 17)}</span><div class="metric-copy"><small>Daily study target</small><strong>${profile.daily_hours} hrs</strong><span>Personal goal · ${escapeHTML(targetLabel)}</span></div></div>
      <div class="metric-card"><span class="metric-icon purple">${icon('check', 17)}</span><div class="metric-copy"><small>Today's tasks</small><strong>${completed}/${count}</strong><span>${count ? `${Math.round(completed / count * 100)}% completed` : 'No tasks planned yet'}</span></div></div>
      <div class="metric-card"><span class="metric-icon amber">${icon('chart', 17)}</span><div class="metric-copy"><small>Syllabus progress</small><strong>${dash.syllabus_progress_percent ?? 0}%</strong><span>${dash.syllabus_topic_completed ?? 0} of ${dash.syllabus_topic_total ?? 0} topics complete</span></div></div>
    </section>

    <div class="dashboard-grid">
      <section class="panel">
        <div class="panel-head"><div><h3>Today's focus</h3><p>Keep your next actions clear and manageable.</p></div><button class="text-link" data-action="go-view" data-view="planner">Open planner →</button></div>
        <div class="panel-body"><div class="task-list">${renderTaskRows(tasks)}</div></div>
      </section>
      <section class="panel">
        <div class="panel-head"><div><h3>Your GATE paper</h3><p>Current preparation track</p></div><span class="status-pill">2027 syllabus</span></div>
        <div class="panel-body">
          <div class="paper-card">
            <div class="paper-card-top"><div class="paper-code-large">${escapeHTML(paper.code)}</div><div><b>${escapeHTML(paper.name)}</b><small>Official paper catalogue · IIT Madras</small></div></div>
            <div class="paper-details"><div class="paper-detail"><small>General Aptitude</small><b>15 marks</b></div><div class="paper-detail"><small>Paper-specific section</small><b>85 marks</b></div></div>
            <div class="paper-card-actions"><button class="btn btn-secondary" data-action="go-view" data-view="syllabus">View syllabus</button><a class="btn btn-secondary" href="https://gate2027.iitm.ac.in/question_paper_pattern" target="_blank" rel="noreferrer">Exam pattern ↗</a></div>
          </div>
        </div>
      </section>
    </div>

    <div class="lower-grid">
      <section class="panel activity-panel">
        <div class="panel-head"><div><h3>Study activity</h3><p>Your study rhythm will take shape here.</p></div><span class="status-pill">Live tracking coming next</span></div>
        <div class="panel-body">
          <div class="activity-visual">
            <svg class="activity-chart" viewBox="0 0 520 110" preserveAspectRatio="none" role="img" aria-label="Empty study activity chart">
              <defs><linearGradient id="activity-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#7595ed" stop-opacity=".18"/><stop offset="1" stop-color="#7595ed" stop-opacity="0"/></linearGradient></defs>
              <path class="chart-grid" d="M0 18H520M0 48H520M0 78H520"/><path class="chart-area" d="M0 88 L86 88 L172 88 L258 88 L344 88 L430 88 L520 88 L520 110 L0 110Z"/><path class="chart-line" d="M0 88 L86 88 L172 88 L258 88 L344 88 L430 88 L520 88" stroke-dasharray="3 6" opacity=".65"/>
            </svg>
            <div class="chart-labels"><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span></div>
          </div>
          <div class="activity-note"><span>↗</span> Complete a study session to begin building your weekly activity history.</div>
        </div>
      </section>
      <section class="panel">
        <div class="panel-head"><div><h3>Your learning toolkit</h3><p>Everything will connect to your selected syllabus.</p></div></div>
        <div class="panel-body"><div class="roadmap-list">
          <button class="roadmap-item" data-action="go-view" data-view="syllabus"><span class="roadmap-icon blue">${icon('book', 14)}</span><span class="roadmap-copy"><b>Syllabus explorer</b><small>Verified sections and topics</small></span></button>
          <button class="roadmap-item" data-action="go-view" data-view="mindmaps"><span class="roadmap-icon teal">${icon('nodes', 14)}</span><span class="roadmap-copy"><b>Interactive mind maps</b><small>Connect related concepts</small></span></button>
          <button class="roadmap-item" data-action="go-view" data-view="questions"><span class="roadmap-icon purple">${icon('layers', 14)}</span><span class="roadmap-copy"><b>PYQ bank</b><small>Practise verified questions</small></span></button>
          <button class="roadmap-item" data-action="go-view" data-view="tests"><span class="roadmap-icon amber">${icon('timer', 14)}</span><span class="roadmap-copy"><b>Mock tests</b><small>Build exam-day readiness</small></span></button>
        </div></div>
      </section>
    </div>
  `;
}

async function renderSyllabus() {
  const host = document.getElementById('page-content');
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Loading the syllabus workspace...</span></div>';
  const profile = state.profile;
  const paper = paperByCode(profile.paper_code);
  try {
    state.syllabus = await api(`/syllabus?paper_code=${encodeURIComponent(profile.paper_code)}`);
  } catch (error) {
    toast(error.message);
    return;
  }
  const data = state.syllabus;
  const progress = data.progress || { total: 0, completed: 0, percent: 0 };
  const common = data.common_section;
  host.innerHTML = `
    <div class="page-heading"><div><span class="eyebrow">OFFICIAL SCOPE · PERSONAL PROGRESS</span><h1>Syllabus explorer</h1><p>Follow the GATE 2027 paper structure and open topic notes from the study library.</p></div><div class="heading-actions"><select class="select-control" id="paper-switcher" aria-label="Select GATE paper">${paperOptions(profile.paper_code)}</select><a class="btn btn-secondary" href="${escapeHTML(data.official_url || paper.official_syllabus_url || 'https://gate2027.iitm.ac.in/exam_papers_and_syllabus')}" target="_blank" rel="noreferrer">Official syllabus ↗</a></div></div>
    <div class="notice"><span class="notice-icon">ⓘ</span><div><strong>Use the official PDF as the source of truth.</strong><p>${escapeHTML(data.message || 'Topic-level structure is being reviewed.')} GATEPath notes are supplemental learning aids, not official GATE material.</p></div></div>
    <div class="syllabus-intro" style="margin-top:14px">
      <div class="syllabus-paper-banner"><div class="paper-code-large">${escapeHTML(paper.code)}</div><div><span class="eyebrow" style="color:#b6c8e9">SELECTED PAPER · GATE 2027</span><h2>${escapeHTML(paper.name)}</h2><p>Versioned syllabus workspace · Source checked ${escapeHTML(data.last_checked || 'not recorded')}</p></div><span class="status-pill">${data.verified ? 'Source transcribed' : 'Topic import pending'}</span></div>
      <div class="syllabus-fact"><small>YOUR TOPIC PROGRESS</small><strong>${progress.percent}%</strong><span>${progress.completed} of ${progress.total} topics completed</span></div>
    </div>
    <div class="syllabus-progress-grid">
      <div class="syllabus-stat"><small>TOPICS IN THIS IMPORT</small><strong>${progress.total}</strong></div>
      <div class="syllabus-stat"><small>COMPLETED</small><strong>${progress.completed}</strong></div>
      <div class="syllabus-stat"><small>REMAINING</small><strong>${Math.max(0, progress.total-progress.completed)}</strong></div>
    </div>
    ${common ? `<div class="common-section-card"><span class="common-section-icon">GA</span><div class="common-section-copy"><b>${escapeHTML(common.name || 'General Aptitude')}</b><p>${escapeHTML(common.description || 'Common section for GATE papers.')} Detailed topic cards are being imported from the official shared PDF.</p></div><div class="common-section-meta"><strong>${common.marks || 15} marks</strong><small>Common section</small><a class="text-link" href="${escapeHTML(common.official_url || 'https://gate2027.iitm.ac.in/exam_papers_and_syllabus')}" target="_blank" rel="noreferrer">Open PDF ↗</a></div></div>` : ''}
    ${data.sections?.length ? `
      <div class="syllabus-toolbar"><label class="syllabus-search">${icon('search',14)}<input id="syllabus-topic-search" type="search" placeholder="Search topics and concepts" aria-label="Search syllabus topics"/></label><select id="syllabus-status-filter" class="select-control" aria-label="Filter by topic status"><option value="all">All topic statuses</option><option value="not_started">Not started</option><option value="in_progress">In progress</option><option value="completed">Completed</option></select></div>
      <section class="syllabus-section"><div class="panel-head"><div><h3>${escapeHTML(paper.code)} paper topics</h3><p>Topic labels are a navigational breakdown of the official statements.</p></div><span class="status-label">${data.sections.length} sections</span></div>
      <div id="syllabus-topic-sections">${data.sections.map((section,index)=>`
        <details class="syllabus-accordion" open><summary><span class="section-index">${String(index+1).padStart(2,'0')}</span><span class="section-summary-copy"><b>${escapeHTML(section.name)}</b><small>${section.topics.length} topics · ${escapeHTML(section.code)}</small></span></summary><div class="topic-list">
          ${section.topics.map(topic=>`
            <article class="topic-card" data-topic-card data-topic-id="${escapeHTML(topic.id)}" data-topic-status="${escapeHTML(topic.status || 'not_started')}" data-search="${escapeHTML(`${topic.name} ${topic.official_statement} ${(topic.subtopics||[]).join(' ')}`.toLowerCase())}">
              <div class="topic-card-head"><div class="topic-card-copy"><span class="topic-id">${escapeHTML(topic.id)}</span><h4>${escapeHTML(topic.name)}</h4><p>${escapeHTML(topic.official_statement)}</p></div><select class="topic-status-control status-${escapeHTML(topic.status || 'not_started')}" data-topic-status-select="${escapeHTML(topic.id)}" aria-label="Progress for ${escapeHTML(topic.name)}"><option value="not_started" ${(topic.status||'not_started')==='not_started'?'selected':''}>Not started</option><option value="in_progress" ${topic.status==='in_progress'?'selected':''}>In progress</option><option value="completed" ${topic.status==='completed'?'selected':''}>Completed</option></select></div>
              <div class="subtopic-list">${(topic.subtopics||[]).map(sub=>`<span class="subtopic-chip">${escapeHTML(sub)}</span>`).join('')}</div>
              <div class="topic-card-actions"><span class="topic-prereq">${topic.bookmarked ? '★ Saved to bookmarks' : 'Mapped to GATE 2027 syllabus'}</span><button class="btn btn-secondary btn-small" data-action="open-material" data-topic-id="${escapeHTML(topic.id)}">Open study note ${icon('arrow',12)}</button></div>
            </article>`).join('')}
        </div></details>`).join('')}</div></section>
    ` : `<section class="syllabus-empty"><h3>Structured topic import is not available yet</h3><p>This paper's official PDF is linked above. Topic cards will appear after topic-by-topic transcription and review.</p><a class="btn btn-primary" href="${escapeHTML(data.official_url || paper.official_syllabus_url || 'https://gate2027.iitm.ac.in/exam_papers_and_syllabus')}" target="_blank" rel="noreferrer">Open official syllabus ↗</a></section>`}
  `;
  setIcons(host);
  document.getElementById('syllabus-topic-search')?.addEventListener('input', filterSyllabusTopics);
  document.getElementById('syllabus-status-filter')?.addEventListener('change', filterSyllabusTopics);
}

function filterSyllabusTopics() {
  const query = (document.getElementById('syllabus-topic-search')?.value || '').trim().toLowerCase();
  const status = document.getElementById('syllabus-status-filter')?.value || 'all';
  document.querySelectorAll('[data-topic-card]').forEach((card) => {
    const textMatch = !query || card.dataset.search.includes(query);
    const statusMatch = status === 'all' || card.dataset.topicStatus === status;
    card.hidden = !(textMatch && statusMatch);
  });
  document.querySelectorAll('.syllabus-accordion').forEach((section) => {
    const visible = [...section.querySelectorAll('[data-topic-card]')].some((card) => !card.hidden);
    section.hidden = !visible;
  });
}


function localDateKey(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function plannerTaskCard(task) {
  const typeLabels = { learn: 'Learn', practice: 'Practice', revision: 'Revision', mock: 'Test', custom: 'Personal task', review: 'Review' };
  const statusLabel = task.status === 'completed' ? 'Completed' : task.status === 'skipped' ? 'Skipped' : 'Pending';
  return `<article class="planner-task-card ${task.status === 'completed' ? 'is-complete' : ''}">
    <div class="planner-task-check"><button class="task-check ${task.status === 'completed' ? 'checked' : ''}" data-action="planner-toggle-task" data-task-id="${task.id}" data-current-status="${escapeHTML(task.status)}" aria-label="${task.status === 'completed' ? 'Reopen task' : 'Complete task'}">${task.status === 'completed' ? icon('check', 11) : ''}</button></div>
    <div class="planner-task-copy"><div class="planner-task-tags"><span class="planner-type-tag type-${escapeHTML(task.task_type)}">${escapeHTML(typeLabels[task.task_type] || 'Study')}</span><span>${escapeHTML(task.duration_minutes)} min</span><span class="planner-priority priority-${escapeHTML(task.priority)}">${escapeHTML(task.priority)} priority</span>${task.status !== 'pending' ? `<span class="planner-state-tag">${statusLabel}</span>` : ''}</div><h4>${escapeHTML(task.title)}</h4><p>${escapeHTML(task.description || '')}</p>${task.topic_id ? `<small class="planner-topic-id">${escapeHTML(task.topic_id)}</small>` : ''}</div>
    <div class="planner-task-actions">${task.topic_id && task.task_type !== 'custom' ? `<button class="btn btn-quiet btn-small" data-action="planner-open-topic" data-topic-id="${escapeHTML(task.topic_id)}">Open notes</button>` : ''}${task.status === 'pending' ? `<button class="btn btn-secondary btn-small" data-action="planner-move-task" data-task-id="${task.id}" data-scheduled-date="${escapeHTML(task.scheduled_date)}">Move to tomorrow</button>` : ''}</div>
  </article>`;
}

function plannerPlanForm(plan = null) {
  const start = plan?.start_date || localDateKey();
  const hours = plan?.daily_hours || state.profile.daily_hours || 5;
  return `<form class="planner-plan-form" id="planner-plan-form">
    <div class="planner-form-fields">
      <label class="planner-field"><span>Plan duration</span><select class="form-control" name="plan_days"><option value="30" ${plan?.plan_days === 30 ? 'selected' : ''}>30 days · Focused revision</option><option value="60" ${(!plan || plan.plan_days === 60) ? 'selected' : ''}>60 days · Balanced preparation</option><option value="90" ${plan?.plan_days === 90 ? 'selected' : ''}>90 days · Full preparation cycle</option></select></label>
      <label class="planner-field"><span>Daily study hours</span><select class="form-control" name="daily_hours">${[1,2,3,4,5,6,7,8,9,10,12,14,16].map((value) => `<option value="${value}" ${Number(hours) === value ? 'selected' : ''}>${value} ${value === 1 ? 'hour' : 'hours'} / day</option>`).join('')}</select></label>
      <label class="planner-field"><span>Start date</span><input class="form-control" type="date" name="start_date" value="${escapeHTML(start)}" required /></label>
    </div>
    <div class="planner-option-row"><label><input type="checkbox" name="include_general_aptitude" checked /> Include shared General Aptitude study blocks</label><label><input type="checkbox" name="include_weekly_mock" checked /> Include weekly mock / review blocks</label></div>
    <div class="planner-form-footer"><small>Generating a new plan archives the currently active plan. Completed task history remains available in the archived plan.</small><button class="btn btn-primary" type="submit">${plan ? 'Regenerate my plan' : 'Generate my study plan'} ${icon('arrow', 13)}</button></div>
  </form>`;
}

async function renderPlanner(selectedDate = null) {
  const host = document.getElementById('page-content');
  const day = selectedDate || state.plannerSelectedDate || localDateKey();
  state.plannerSelectedDate = day;
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Building your personalised preparation view...</span></div>';
  try {
    state.plannerOverview = await api(`/planner/overview?paper_code=${encodeURIComponent(state.profile.paper_code)}&selected_date=${encodeURIComponent(day)}`);
  } catch (error) {
    host.innerHTML = `<section class="panel content-placeholder"><div><div class="placeholder-icon">${icon('calendar', 24)}</div><h2>Could not load your planner</h2><p>${escapeHTML(error.message)}</p><button class="btn btn-secondary" data-action="refresh-planner">Try again</button></div></section>`;
    return;
  }
  const data = state.plannerOverview;
  const plan = data.plan;
  const paper = paperByCode(state.profile.paper_code);
  if (!plan) {
    const setupContent = data.content_available === false
      ? `<section class="panel planner-pending-panel"><div class="placeholder-icon">${icon('book', 24)}</div><h2>Verified topic import is still pending for ${escapeHTML(paper.code)}</h2><p>We will not generate a plan from guessed topics. The ${escapeHTML(paper.code)} planner will become available after its official GATE 2027 syllabus has been structured and reviewed.</p><a class="btn btn-primary" href="${escapeHTML(data.official_syllabus_url || 'https://gate2027.iitm.ac.in/exam_papers_and_syllabus')}" target="_blank" rel="noreferrer">Open official syllabus ↗</a></section>`
      : `<section class="panel planner-setup-panel"><div class="panel-head"><div><h3>Create your preparation plan</h3><p>Start with the hours you can consistently protect.</p></div><span class="status-pill">30 · 60 · 90 days</span></div><div class="panel-body">${plannerPlanForm()}</div></section><section class="planner-principles"><div><b>Prioritises weak areas</b><span>Low-accuracy topics are scheduled earlier.</span></div><div><b>Respects your time</b><span>Daily blocks are based on your available hours.</span></div><div><b>Builds revision into the plan</b><span>Spaced reviews are scheduled after learning.</span></div></section>`;
    host.innerHTML = `<div class="page-heading"><div><span class="eyebrow">STAGE 10 · PERSONAL PREPARATION SYSTEM</span><h1>Your study plan, built around you.</h1><p>Choose a realistic timeline and your available hours. GATEPath will schedule topic learning, practice, reviews and weekly checks.</p></div><span class="status-pill">Personalised planner</span></div>
      <section class="planner-welcome"><div class="planner-welcome-icon">${icon('calendar', 25)}</div><div><span class="eyebrow">${escapeHTML(paper.code)} PREPARATION TRACK</span><h2>Turn the syllabus into a daily routine.</h2><p>The planner uses your imported syllabus, topic progress and latest practice performance. It will not create topic schedules for papers whose syllabus has not yet been structured.</p></div></section>${setupContent}`;
    document.getElementById('planner-plan-form')?.addEventListener('submit', handlePlannerPlanSubmit);
    setIcons(host);
    return;
  }

  const selectedTasks = data.selected_day_tasks || [];
  const upcoming = data.upcoming_tasks || [];
  const completedToday = selectedTasks.filter((task) => task.status === 'completed').length;
  const totalMinutes = plan.daily_hours * 60;
  const loadPercent = totalMinutes ? Math.min(100, Math.round((data.selected_day_minutes || 0) / totalMinutes * 100)) : 0;
  const weekCards = (data.week_summary || []).map((item) => `<button class="planner-week-day ${item.date === day ? 'is-selected' : ''} ${item.date === data.today ? 'is-today' : ''}" data-action="planner-select-date" data-date="${escapeHTML(item.date)}"><small>${escapeHTML(formatDate(item.date).split(' ')[0])}</small><b>${escapeHTML(item.date.slice(8, 10))}</b><span>${item.completed_count}/${item.task_count} done</span></button>`).join('');
  const groups = {};
  upcoming.forEach((task) => { (groups[task.scheduled_date] ||= []).push(task); });
  const upcomingHTML = Object.keys(groups).sort().map((dateKey) => `<section class="planner-upcoming-day"><div class="planner-day-heading"><b>${escapeHTML(formatDate(dateKey))}</b><span>${groups[dateKey].length} task(s)</span></div><div class="planner-task-stack">${groups[dateKey].map(plannerTaskCard).join('')}</div></section>`).join('');
  host.innerHTML = `<div class="page-heading"><div><span class="eyebrow">STAGE 10 · PERSONAL PREPARATION SYSTEM</span><h1>Your study planner</h1><p>${escapeHTML(plan.title)} · ${escapeHTML(paper.name)}</p></div><div class="heading-actions"><button class="btn btn-secondary" data-action="planner-reschedule-overdue">Reschedule overdue</button></div></div>
    <section class="planner-plan-banner"><div><span class="eyebrow">ACTIVE PREPARATION PLAN</span><h2>${escapeHTML(plan.title)}</h2><p>${escapeHTML(formatDate(plan.start_date))} — ${escapeHTML(formatDate(plan.end_date))} · ${plan.daily_hours} study hours per day</p></div><div class="planner-plan-progress"><strong>${plan.completion_percent}%</strong><span>tasks completed</span><div class="planner-progress-track"><i style="width:${plan.completion_percent}%"></i></div></div></section>
    <div class="planner-metrics-grid"><div class="planner-metric"><small>TOPICS SCHEDULED</small><strong>${plan.planned_topic_count}</strong><span>${plan.unplanned_topic_count ? `${plan.unplanned_topic_count} outside this plan` : 'All imported topics'}</span></div><div class="planner-metric"><small>TASKS COMPLETED</small><strong>${plan.completed_count}<em> / ${plan.task_count}</em></strong><span>${plan.skipped_count} skipped</span></div><div class="planner-metric"><small>OVERDUE TASKS</small><strong>${plan.overdue_count}</strong><span>Pending before today</span></div><div class="planner-metric"><small>DAYS REMAINING</small><strong>${plan.days_remaining}</strong><span>In this plan</span></div></div>
    <details class="panel planner-config-panel"><summary><span><b>Adjust your plan</b><small>Change timeline, start date or daily study hours</small></span><span>＋</span></summary><div class="panel-body">${plannerPlanForm(plan)}</div></details>
    <div class="planner-main-grid"><section class="panel planner-today-panel"><div class="panel-head"><div><h3>Daily focus</h3><p>${escapeHTML(formatDate(day))} · ${completedToday} of ${selectedTasks.length} tasks completed</p></div><input class="form-control planner-date-picker" id="planner-selected-date" type="date" value="${escapeHTML(day)}" aria-label="Select planner date" /></div><div class="panel-body"><div class="planner-load-summary"><div><b>${data.selected_day_minutes || 0} min</b><span>scheduled of ${totalMinutes} min daily target</span></div><strong>${loadPercent}%</strong></div><div class="planner-progress-track"><i style="width:${loadPercent}%"></i></div><div class="planner-task-stack">${selectedTasks.length ? selectedTasks.map(plannerTaskCard).join('') : '<div class="empty-state"><strong>No tasks on this date</strong><p>Choose another day or add a personal task below.</p></div>'}</div><form class="planner-custom-form" id="planner-custom-form"><input class="form-control" name="title" minlength="2" maxlength="140" placeholder="Add your own study task..." required/><input class="form-control" name="scheduled_date" type="date" value="${escapeHTML(day)}" aria-label="Task date"/><select class="form-control" name="duration_minutes"><option value="25">25 min</option><option value="45" selected>45 min</option><option value="60">60 min</option><option value="90">90 min</option></select><button class="btn btn-primary" type="submit">Add task ${icon('plus', 12)}</button></form></div></section>
      <aside class="planner-side-stack"><section class="panel"><div class="panel-head"><div><h3>Study week</h3><p>Choose a day to inspect its tasks.</p></div></div><div class="planner-week-strip">${weekCards || '<p class="muted-note">No scheduled days to show.</p>'}</div></section><section class="panel"><div class="panel-head"><div><h3>Revision queue</h3><p>Reviews due within the next seven days.</p></div><span class="status-pill">${data.revision_due?.length || 0} due</span></div><div class="panel-body planner-compact-list">${data.revision_due?.length ? data.revision_due.slice(0,5).map(item => `<div class="planner-compact-item"><span><b>${escapeHTML(item.topic_name)}</b><small>Due ${escapeHTML(formatDate(item.due_date))} · ${item.review_count} reviews</small></span><button class="btn btn-quiet btn-small" data-action="planner-open-topic" data-topic-id="${escapeHTML(item.topic_id)}">Review</button></div>`).join('') : '<div class="empty-state"><strong>No revision reminders</strong><p>Complete a learning block to seed a spaced review.</p></div>'}</div></section></aside></div>
    <div class="planner-bottom-grid"><section class="panel"><div class="panel-head"><div><h3>Upcoming tasks</h3><p>Next seven days from the selected date.</p></div><span class="status-pill">${upcoming.length} scheduled</span></div><div class="panel-body planner-upcoming-list">${upcomingHTML || '<div class="empty-state"><strong>No upcoming tasks</strong><p>Your schedule is clear for this week.</p></div>'}</div></section><section class="panel"><div class="panel-head"><div><h3>Topics to strengthen</h3><p>Based on the latest attempt for each practice question.</p></div></div><div class="panel-body planner-weak-list">${data.weak_topics?.length ? data.weak_topics.map(item => `<div class="planner-weak-row"><span><b>${escapeHTML(item.topic_name)}</b><small>${item.correct}/${item.attempted} correct</small></span><strong>${item.accuracy_percent}%</strong></div>`).join('') : '<div class="empty-state"><strong>No weak topics detected yet</strong><p>Complete topic practice to personalise your priority order.</p></div>'}</div></section></div>
    ${plan.unplanned_topic_count ? `<div class="notice planner-capacity-note"><b>Plan capacity note</b><p>${escapeHTML(`${plan.unplanned_topic_count} imported topic(s) could not fit within this plan at your selected daily study hours. Extend the plan or increase your available time to schedule them.`)}</p></div>` : ''}`;
  document.getElementById('planner-plan-form')?.addEventListener('submit', handlePlannerPlanSubmit);
  document.getElementById('planner-custom-form')?.addEventListener('submit', handlePlannerCustomTaskSubmit);
  document.getElementById('planner-selected-date')?.addEventListener('change', (event) => renderPlanner(event.target.value));
  setIcons(host);
}

async function handlePlannerPlanSubmit(event) {
  event.preventDefault();
  if (state.plannerOverview?.plan && !window.confirm('Generate a new plan? Your current active plan will be archived; its history will be kept.')) return;
  const form = new FormData(event.currentTarget);
  const payload = {
    paper_code: state.profile.paper_code,
    plan_days: Number(form.get('plan_days')),
    daily_hours: Number(form.get('daily_hours')),
    start_date: String(form.get('start_date')),
    include_general_aptitude: form.has('include_general_aptitude'),
    include_weekly_mock: form.has('include_weekly_mock'),
  };
  const submit = event.currentTarget.querySelector('button[type="submit"]');
  if (submit) { submit.disabled = true; submit.textContent = 'Generating your plan...'; }
  try {
    const plan = await api('/planner/plans', { method: 'POST', body: JSON.stringify(payload) });
    state.plannerSelectedDate = plan.start_date;
    toast(`Your ${plan.plan_days}-day plan is ready.`);
    await renderPlanner(plan.start_date);
  } catch (error) {
    toast(error.message);
    if (submit) { submit.disabled = false; submit.innerHTML = 'Try again'; }
  }
}

async function handlePlannerCustomTaskSubmit(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  try {
    await api('/planner/tasks', { method: 'POST', body: JSON.stringify({
      title: String(form.get('title')).trim(), scheduled_date: String(form.get('scheduled_date')),
      duration_minutes: Number(form.get('duration_minutes')), priority: 'normal',
    }) });
    toast('Personal task added to your plan.');
    await renderPlanner(state.plannerSelectedDate);
  } catch (error) { toast(error.message); }
}

async function updatePlannerTask(taskId, payload) {
  const currentView = state.view;
  try {
    await api(`/planner/tasks/${encodeURIComponent(taskId)}`, { method: 'PATCH', body: JSON.stringify(payload) });
    toast(payload.status === 'completed' ? 'Task completed. Keep going.' : payload.scheduled_date ? 'Task rescheduled.' : 'Task updated.');
    if (currentView === 'overview') { await refreshOverview(); renderView(); }
    else await renderPlanner(state.plannerSelectedDate);
  } catch (error) { toast(error.message); }
}

async function reschedulePlannerOverdue() {
  try {
    const result = await api('/planner/reschedule-overdue', { method: 'POST', body: '{}' });
    toast(result.message);
    await renderPlanner(state.plannerSelectedDate);
  } catch (error) { toast(error.message); }
}

const PLACEHOLDERS = {
  mindmaps: { title: 'Interactive mind maps', subtitle: 'Explore how the concepts in your GATE paper connect.', text: 'Choose a subject to open its concept map, inspect prerequisites and jump to related study notes.', icon: 'nodes', stage: 'Stage 6', action: 'Open mind maps', view: 'mindmaps' },
  questions: { title: 'Previous-year question bank', subtitle: 'Practise against verified official answer keys.', text: 'Open the PYQ bank to filter GATE papers, enter answers, review marks and save questions for later.', icon: 'layers', stage: 'Stage 7', action: 'Open PYQ bank', view: 'questions' },
  practice: { title: 'Focused practice', subtitle: 'Turn each lesson into measurable mastery.', text: 'Topic-wise practice, daily challenges and timed quizzes.', icon: 'target', stage: 'Stage 8', action: 'Start practice', view: 'practice' },
  tests: { title: 'GATE-style mock tests are on the roadmap', subtitle: 'A realistic computer-based test experience.', text: 'The test player will include an exam timer, question palette, answer navigation, review marking, autosave, paper-specific sections and configurable scoring rules. It will be tested against the official GATE 2027 pattern before release.', icon: 'timer', stage: 'Stage 9', action: 'View official exam pattern', external: 'https://gate2027.iitm.ac.in/question_paper_pattern' },
  revision: { title: 'A smarter revision centre is planned', subtitle: 'Bring important concepts back at the right time.', text: 'Flashcards, formula revision, saved questions, an error notebook and spaced-repetition scheduling will connect to the topics you study and the mistakes you make.', icon: 'repeat', stage: 'Stage 10', action: 'Open study planner', view: 'planner' },
  analytics: { title: 'Preparation analytics', subtitle: 'Measure learning, not just time spent.', text: 'Review recorded syllabus completion, practice accuracy, mock-test history, active days and topics to revisit.', icon: 'chart', stage: 'Stage 12', action: 'Open study planner', view: 'planner' },
  tutor: { title: 'Your AI GATE tutor is planned', subtitle: 'Understand the reasoning behind every answer.', text: 'The tutor will use approved learning materials and syllabus context, cite its sources, explain solutions step by step and distinguish verified content from generated practice. It will not invent official questions or guaranteed rank predictions.', icon: 'sparkles', stage: 'Stage 11', action: 'Explore learning structure', view: 'syllabus' },
  resources: { title: 'Resource library foundation', subtitle: 'A trusted home for your study references.', text: 'The library will bring together original notes, formula sheets, diagrams, licensed PDFs and curated lecture links. Each item will show the paper, topic, source, rights and review status.', icon: 'bookmark', stage: 'Stage 5', action: 'Visit official GATE resources', external: 'https://gate2027.iitm.ac.in/exam_papers_and_syllabus' },
  community: { title: 'GATEPath community', subtitle: 'Learn with other aspirants in a structured space.', text: 'Ask paper-specific doubts, share learning resources and discuss preparation strategies with moderation and reporting tools.', icon: 'users', stage: 'Stage 12', action: 'Return to overview', view: 'overview' },
};

function renderPlaceholder(view) {
  const info = PLACEHOLDERS[view] || PLACEHOLDERS.resources;
  const action = info.external
    ? `<a class="btn btn-primary" href="${info.external}" target="_blank" rel="noreferrer">${escapeHTML(info.action)} ↗</a>`
    : `<button class="btn btn-primary" data-action="go-view" data-view="${info.view}">${escapeHTML(info.action)} ${icon('arrow', 13)}</button>`;
  return `
    <div class="page-heading"><div><span class="eyebrow">${escapeHTML(info.stage.toUpperCase())} · DEVELOPMENT ROADMAP</span><h1>${escapeHTML(info.title)}</h1><p>${escapeHTML(info.subtitle)}</p></div><span class="status-pill">Planned module</span></div>
    <section class="panel content-placeholder"><div><div class="placeholder-icon">${icon(info.icon, 24)}</div><h2>${escapeHTML(info.title)}</h2><p>${escapeHTML(info.text)}</p>${action}</div></section>
  `;
}

function tutorSourceCards(sources = []) {
  if (!sources.length) return '';
  return `<div class="tutor-source-list"><b>Sources used</b>${sources.map((source) => {
    const label = `${source.source_id || 'Source'} · ${source.section_name || 'Study source'} — ${source.topic_name || 'Reference'}`;
    const link = /^https:\/\//i.test(source.source_url || '')
      ? `<a href="${escapeHTML(source.source_url)}" target="_blank" rel="noreferrer">Official syllabus ↗</a>`
      : '<span>Local indexed note</span>';
    return `<div class="tutor-source-item"><div><strong>${escapeHTML(label)}</strong><small>${escapeHTML(source.source_label || 'GATEPath learning reference')} · ${escapeHTML(source.content_status || '')}</small></div>${link}</div>`;
  }).join('')}</div>`;
}

function tutorMessageHTML(message) {
  const assistant = message.role === 'assistant';
  return `<article class="tutor-message ${assistant ? 'is-assistant' : 'is-student'}"><div class="tutor-message-avatar">${assistant ? icon('sparkles', 15) : escapeHTML((state.user?.full_name || 'S').slice(0, 1).toUpperCase())}</div><div class="tutor-message-content"><div class="tutor-message-meta"><b>${assistant ? 'GATEPath Tutor' : 'You'}</b><span>${assistant ? escapeHTML(message.provider || 'Tutor') : 'Question'}${message.image_attached ? ' · image attached' : ''}</span></div><div class="tutor-message-text">${escapeHTML(message.content || '').replace(/\n/g, '<br>')}</div>${assistant ? tutorSourceCards(message.sources || []) : ''}</div></article>`;
}

async function loadTutorConversation(conversationId) {
  const data = await api(`/tutor/conversations/${encodeURIComponent(conversationId)}`);
  state.tutorConversationId = conversationId;
  state.tutorMessages = data.messages || [];
  state.tutorSimilarResult = null;
  renderTutorContent();
}

async function renderTutor() {
  const host = document.getElementById('page-content');
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Preparing your AI tutor...</span></div>';
  try {
    const [status, conversations] = await Promise.all([
      api('/tutor/status'), api('/tutor/conversations?limit=30'),
    ]);
    state.tutorStatus = status;
    state.tutorConversations = conversations.items || [];
    if (state.tutorConversationId) {
      const found = state.tutorConversations.some((item) => item.id === state.tutorConversationId);
      if (!found) { state.tutorConversationId = null; state.tutorMessages = []; }
      else {
        const detail = await api(`/tutor/conversations/${encodeURIComponent(state.tutorConversationId)}`);
        state.tutorMessages = detail.messages || [];
      }
    }
    renderTutorContent();
  } catch (error) {
    host.innerHTML = `<section class="panel content-placeholder"><div><div class="placeholder-icon">${icon('sparkles', 24)}</div><h2>AI tutor could not load</h2><p>${escapeHTML(error.message)}</p></div></section>`;
  }
}

function renderTutorContent() {
  const host = document.getElementById('page-content');
  if (!host || state.view !== 'tutor' || !state.tutorStatus) return;
  const status = state.tutorStatus;
  const aiReady = Boolean(status.ai_available);
  const topics = status.indexed_topics || [];
  const selectedTopic = document.getElementById('tutor-topic-select')?.value || '';
  const messagesHTML = state.tutorMessages.length
    ? state.tutorMessages.map(tutorMessageHTML).join('')
    : `<div class="tutor-welcome"><div class="tutor-welcome-icon">${icon('sparkles', 25)}</div><span class="eyebrow">YOUR PAPER-AWARE STUDY COMPANION</span><h2>What are you working through today?</h2><p>Ask a concept question, share a numerical problem or upload a question image. Answers use the indexed study library when available and show their sources.</p><div class="tutor-starters"><button data-action="tutor-starter" data-message="Explain the difference between process and thread with a simple example.">Explain a concept</button><button data-action="tutor-starter" data-message="Help me solve a numerical GATE-style question step by step. State assumptions and verify the final answer.">Solve a numerical</button><button data-action="tutor-starter" data-message="Give me a concise revision summary and the common mistakes for this topic.">Revise a topic</button></div></div>`;
  const historyHTML = state.tutorConversations.length ? state.tutorConversations.map((item) => `<button class="tutor-history-item ${item.id === state.tutorConversationId ? 'is-active' : ''}" data-action="open-tutor-conversation" data-conversation-id="${escapeHTML(item.id)}"><b>${escapeHTML(item.title)}</b><small>${escapeHTML(item.paper_code)} · ${escapeHTML(item.updated_at)}</small></button>`).join('') : '<div class="tutor-history-empty">Your conversations will appear here.</div>';
  const generated = state.tutorSimilarResult ? `<section class="panel tutor-generated-panel"><div class="panel-head"><div><h3>Similar practice questions</h3><p>${escapeHTML(state.tutorSimilarResult.message || state.tutorSimilarResult.content_label || 'Original practice questions')}</p></div><button class="icon-button" data-action="dismiss-tutor-generated" aria-label="Close generated questions">×</button></div><div class="panel-body">${state.tutorSimilarResult.generated ? `<span class="status-pill">AI-generated original practice · not official PYQs</span><div class="tutor-generated-text">${escapeHTML(state.tutorSimilarResult.content || '').replace(/\n/g,'<br>')}</div>` : (state.tutorSimilarResult.related_questions || []).map((item) => `<div class="tutor-related-question"><b>${escapeHTML(item.id)} · ${escapeHTML(item.question_type)} · ${escapeHTML(item.difficulty)}</b><p>${escapeHTML(item.prompt)}</p><small>${escapeHTML(item.content_label)}</small></div>`).join('') || '<p class="muted-copy">No existing practice questions are mapped to this topic yet.</p>'}</div></section>` : '';
  host.innerHTML = `
    <div class="page-heading"><div><span class="eyebrow">STAGE 11 · PAPER-AWARE LEARNING ASSISTANT</span><h1>AI GATE tutor</h1><p>Ask, understand, practise and revise with references to your selected paper.</p></div><div class="heading-actions"><span class="tutor-mode-pill ${aiReady ? 'is-live' : 'is-local'}">${aiReady ? 'AI + grounded notes' : (topics.length ? 'Knowledge-only mode' : 'Official source mode')}</span><button class="btn btn-secondary" data-action="new-tutor-chat">${icon('plus',13)} New conversation</button></div></div>
    <div class="tutor-privacy-note"><span>${icon('shield',14)}</span><span>${escapeHTML(status.privacy_note || 'Conversation history is private to your account.')}</span></div>
    <div class="tutor-layout">
      <aside class="panel tutor-history-panel"><div class="panel-head"><div><h3>Recent conversations</h3><p>${state.tutorConversations.length} saved</p></div></div><div class="tutor-history-list">${historyHTML}</div><div class="tutor-paper-context"><small>YOUR SELECTED PAPER</small><b>${escapeHTML(status.paper_code)} · ${escapeHTML(status.paper_name)}</b><span>${topics.length} indexed study topics</span><a href="${escapeHTML(status.official_syllabus_url || '#')}" target="_blank" rel="noreferrer">Official syllabus ↗</a></div></aside>
      <section class="panel tutor-chat-panel"><div class="tutor-chat-top"><div><b>GATEPath Tutor</b><small>${aiReady ? `Connected · ${escapeHTML(status.model || status.provider || 'AI provider')}` : 'Local notes retrieval is available · configure an API key for generated answers'}</small></div><span class="status-dot ${aiReady ? 'is-live' : ''}"></span></div>
        <div class="tutor-chat-messages" id="tutor-chat-messages">${messagesHTML}</div>
        ${generated}
        <form class="tutor-chat-form" id="tutor-chat-form"><div class="tutor-composer-options"><label>Explanation level<select id="tutor-explanation-level"><option value="beginner">Beginner · build intuition</option><option value="advanced">Advanced · exam depth</option></select></label><label>Focus topic<select id="tutor-topic-select"><option value="">Auto-detect from question</option>${topics.map((topic) => `<option value="${escapeHTML(topic.id)}" ${selectedTopic === topic.id ? 'selected' : ''}>${escapeHTML(topic.section)} · ${escapeHTML(topic.name)}</option>`).join('')}</select></label></div>
          <div class="tutor-image-preview" id="tutor-image-preview" ${state.tutorImageDataUrl ? '' : 'hidden'}>${state.tutorImageDataUrl ? `<img src="${state.tutorImageDataUrl}" alt="Selected question image preview"><span>${escapeHTML(state.tutorImageName)}</span><button type="button" data-action="tutor-clear-image" aria-label="Remove image">×</button>` : ''}</div>
          <div class="tutor-composer"><label class="tutor-image-button" for="tutor-image-input" title="Attach a question image">${icon('file',17)}<span>Image</span></label><input type="file" id="tutor-image-input" accept="image/png,image/jpeg,image/webp" hidden><textarea id="tutor-message-input" rows="3" maxlength="5000" placeholder="Ask your GATE question..." required></textarea><button class="btn btn-primary tutor-send-button" id="tutor-send-button" type="submit" ${state.tutorBusy ? 'disabled' : ''}>${state.tutorBusy ? 'Thinking…' : 'Send'} ${icon('arrow',14)}</button></div><div class="tutor-composer-footer"><span>Check calculations and references before relying on an explanation.</span><button type="button" class="text-link" data-action="tutor-generate-similar">Generate similar questions</button></div>
        </form>
      </section>
    </div>`;
  const form = document.getElementById('tutor-chat-form');
  form?.addEventListener('submit', submitTutorMessage);
  document.getElementById('tutor-image-input')?.addEventListener('change', handleTutorImage);
  const messageBox = document.getElementById('tutor-message-input');
  messageBox?.addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form?.requestSubmit(); } });
  const scroll = document.getElementById('tutor-chat-messages');
  if (scroll) scroll.scrollTop = scroll.scrollHeight;
}

async function handleTutorImage(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
    toast('Choose a PNG, JPEG or WEBP image under 5 MB.'); event.target.value = ''; return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    state.tutorImageDataUrl = String(reader.result || '');
    state.tutorImageName = file.name;
    renderTutorContent();
  };
  reader.onerror = () => toast('The selected image could not be read.');
  reader.readAsDataURL(file);
}

async function submitTutorMessage(event, suppliedMessage = '') {
  event?.preventDefault?.();
  if (state.tutorBusy) return;
  const input = document.getElementById('tutor-message-input');
  const message = String(suppliedMessage || input?.value || '').trim();
  if (message.length < 3 && !state.tutorImageDataUrl) { toast('Enter a question or attach an image.'); return; }
  state.tutorBusy = true;
  const send = document.getElementById('tutor-send-button');
  if (send) { send.disabled = true; send.textContent = 'Thinking…'; }
  try {
    const result = await api('/tutor/chat', { method: 'POST', body: JSON.stringify({
      message: message || 'Please read and explain the GATE question in this image.',
      conversation_id: state.tutorConversationId,
      paper_code: state.profile.paper_code,
      topic_id: document.getElementById('tutor-topic-select')?.value || null,
      explanation_level: document.getElementById('tutor-explanation-level')?.value || 'beginner',
      image_data_url: state.tutorImageDataUrl,
    }) });
    state.tutorConversationId = result.conversation_id;
    state.tutorImageDataUrl = null;
    state.tutorImageName = '';
    state.tutorBusy = false;
    await renderTutor();
    if (result.ai_used) toast('Tutor response received. Verify the reasoning before using it in a test.');
    else toast('Knowledge-mode response saved. Configure an AI key for generated explanations.');
  } catch (error) {
    state.tutorBusy = false;
    toast(error.message);
    renderTutorContent();
  }
}

async function generateTutorSimilarQuestions() {
  const topicId = document.getElementById('tutor-topic-select')?.value || '';
  if (!topicId) { toast('Select a topic to generate related questions.'); return; }
  const button = document.querySelector('[data-action="tutor-generate-similar"]');
  if (button) { button.disabled = true; button.textContent = 'Preparing…'; }
  try {
    state.tutorSimilarResult = await api('/tutor/similar-questions', { method: 'POST', body: JSON.stringify({ topic_id: topicId, difficulty: 'Intermediate', count: 3 }) });
    renderTutorContent();
  } catch (error) { toast(error.message); }
}

async function renderResources() {
  const host = document.getElementById('page-content');
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Opening your study library...</span></div>';
  try {
    state.materialCatalog = await api(`/materials?paper_code=${encodeURIComponent(state.profile.paper_code)}`);
  } catch (error) {
    host.innerHTML = `<section class="panel content-placeholder"><div><h2>Study library could not load</h2><p>${escapeHTML(error.message)}</p></div></section>`;
    return;
  }
  const catalog = state.materialCatalog;
  const summary = catalog.summary || { total: 0, completed: 0, in_progress: 0, bookmarked: 0 };
  host.innerHTML = `
    <div class="page-heading"><div><span class="eyebrow">STAGE 5 · LEARN WITH STRUCTURE</span><h1>Study material library</h1><p>Original topic notes, concept explanations, worked examples, formula cards and curated external courses.</p></div><a class="btn btn-secondary" href="${escapeHTML(catalog.official_syllabus_url || 'https://gate2027.iitm.ac.in/exam_papers_and_syllabus')}" target="_blank" rel="noreferrer">Official syllabus ↗</a></div>
    <div class="notice"><span class="notice-icon">ⓘ</span><div><strong>Know what each resource is.</strong><p>${escapeHTML(catalog.notice || 'Supplemental learning material.')} GATEPath notes are original editorial explanations; external courses remain on their providers' websites.</p></div></div>
    ${catalog.items?.length ? `
      <div class="material-metrics">
        <div class="syllabus-stat"><small>TOPIC NOTES</small><strong>${summary.total}</strong></div>
        <div class="syllabus-stat"><small>COMPLETED</small><strong>${summary.completed}</strong></div>
        <div class="syllabus-stat"><small>IN PROGRESS</small><strong>${summary.in_progress}</strong></div>
        <div class="syllabus-stat"><small>BOOKMARKED</small><strong>${summary.bookmarked}</strong></div>
      </div>
      <div class="material-toolbar"><label class="syllabus-search">${icon('search',14)}<input type="search" id="material-search" placeholder="Search a topic, concept or subject" aria-label="Search study notes"/></label><select class="select-control" id="material-section-filter" aria-label="Filter by subject"><option value="all">All subjects</option>${(catalog.sections||[]).map(s=>`<option value="${escapeHTML(s.code)}">${escapeHTML(s.name)}</option>`).join('')}</select><select class="select-control" id="material-status-filter" aria-label="Filter by progress"><option value="all">All progress</option><option value="not_started">Not started</option><option value="in_progress">In progress</option><option value="completed">Completed</option><option value="bookmarked">Bookmarked</option></select></div>
      <div id="material-card-groups" class="material-card-groups"></div>
    ` : `<section class="syllabus-empty"><h3>Topic-wise notes are being prepared for this paper</h3><p>${escapeHTML(catalog.notice || 'The official syllabus PDF is available. The topic library will appear after a verified content import.')}</p><a class="btn btn-primary" href="${escapeHTML(catalog.official_syllabus_url || 'https://gate2027.iitm.ac.in/exam_papers_and_syllabus')}" target="_blank" rel="noreferrer">Open official syllabus ↗</a></section>`}
    <div class="material-resource-footnote"><b>Resource policy</b><span>Course links open on NPTEL/SWAYAM or the named provider. Course availability, enrolment windows and certificate rules can change; GATEPath does not host third-party videos or books.</span></div>
  `;
  setIcons(host);
  document.getElementById('material-search')?.addEventListener('input', renderMaterialCards);
  document.getElementById('material-section-filter')?.addEventListener('change', renderMaterialCards);
  document.getElementById('material-status-filter')?.addEventListener('change', renderMaterialCards);
  renderMaterialCards();
}

function renderMaterialCards() {
  const target = document.getElementById('material-card-groups');
  if (!target || !state.materialCatalog) return;
  const query = (document.getElementById('material-search')?.value || '').trim().toLowerCase();
  const sectionCode = document.getElementById('material-section-filter')?.value || 'all';
  const status = document.getElementById('material-status-filter')?.value || 'all';
  const items = state.materialCatalog.items.filter((item) => {
    const textMatch = !query || `${item.topic_name} ${item.section_name} ${item.overview}`.toLowerCase().includes(query);
    const sectionMatch = sectionCode === 'all' || item.section_code === sectionCode;
    const statusMatch = status === 'all' || (status === 'bookmarked' ? item.bookmarked : item.status === status);
    return textMatch && sectionMatch && statusMatch;
  });
  if (!items.length) {
    target.innerHTML = '<div class="syllabus-empty"><h3>No matching study notes</h3><p>Change the search phrase or filters to see other topics.</p></div>';
    return;
  }
  const grouped = new Map();
  items.forEach((item) => {
    if (!grouped.has(item.section_code)) grouped.set(item.section_code, { name: item.section_name, items: [] });
    grouped.get(item.section_code).items.push(item);
  });
  target.innerHTML = [...grouped.entries()].map(([code, group]) => `
    <section class="material-section"><div class="material-section-head"><div><span class="eyebrow">${escapeHTML(code)}</span><h3>${escapeHTML(group.name)}</h3></div><small>${group.items.length} notes</small></div>
      <div class="material-grid">${group.items.map(item => `
        <article class="material-card"><div class="material-card-top"><span class="material-id">${escapeHTML(item.id)}</span><span class="material-status ${escapeHTML(item.status)}">${item.status === 'completed' ? 'Completed' : item.status === 'in_progress' ? 'In progress' : 'Not started'}</span></div><h4>${escapeHTML(item.topic_name)}</h4><p>${escapeHTML(item.overview)}</p><div class="material-card-foot"><span>${item.reading_minutes} min · ${escapeHTML(item.difficulty)}</span><span>${item.bookmarked ? '★ Saved' : 'Study note'}</span></div><button class="btn btn-secondary btn-small" data-action="open-material" data-topic-id="${escapeHTML(item.id)}">Read topic note ${icon('arrow',12)}</button></article>
      `).join('')}</div>
    </section>`).join('');
  setIcons(target);
}

async function openMaterial(topicId) {
  try {
    state.materialDetail = await api(`/materials/${encodeURIComponent(topicId)}?paper_code=${encodeURIComponent(state.profile.paper_code)}`);
    state.view = 'material';
    document.querySelectorAll('.nav-item').forEach((item) => item.classList.toggle('active', item.dataset.view === 'resources'));
    document.getElementById('breadcrumb-current').textContent = 'Study materials';
    renderMaterialDetail();
  } catch (error) { toast(error.message); }
}

function renderMaterialDetail() {
  const host = document.getElementById('page-content');
  const material = state.materialDetail;
  if (!material) return;
  const progress = material.progress || { status: 'not_started', bookmarked: false, personal_note: '' };
  host.innerHTML = `
    <div class="page-heading"><div><span class="eyebrow">${escapeHTML(material.section_code)} · ${escapeHTML(material.id)}</span><h1>${escapeHTML(material.topic_name)}</h1><p>${escapeHTML(material.section_name)} · ${material.reading_minutes} minute learning note · ${escapeHTML(material.difficulty)}</p></div><div class="heading-actions"><button class="btn btn-secondary" data-action="back-materials">← Library</button><button class="btn btn-secondary" data-action="print-material">Print / Save PDF</button></div></div>
    <div class="notice"><span class="notice-icon">ⓘ</span><div><strong>${escapeHTML(material.content_label)}</strong><p>This is an original learning aid. Its topic scope is mapped to the official syllabus statement below; it is not an official GATE question or coaching-provider handout.</p></div></div>
    <section class="material-detail-hero"><div><span class="eyebrow">START WITH THE BIG IDEA</span><h2>Understand the concept before memorising it.</h2><p>${escapeHTML(material.overview)}</p></div><div class="material-detail-actions"><label>My progress<select class="select-control" id="material-detail-status"><option value="not_started" ${progress.status==='not_started'?'selected':''}>Not started</option><option value="in_progress" ${progress.status==='in_progress'?'selected':''}>In progress</option><option value="completed" ${progress.status==='completed'?'selected':''}>Completed</option></select></label><button class="btn btn-secondary" data-action="toggle-material-bookmark">${progress.bookmarked ? '★ Bookmarked' : '☆ Bookmark topic'}</button></div></section>
    <div class="material-content-layout"><main class="material-content-main">
      <section class="panel material-content-panel"><div class="panel-head"><div><h3>Official syllabus statement</h3><p>Use this to keep the scope precise.</p></div></div><div class="panel-body"><blockquote class="material-official-statement">${escapeHTML(material.official_statement)}</blockquote></div></section>
      <section class="panel material-content-panel"><div class="panel-head"><div><h3>Learning outcomes</h3><p>After this note, you should be able to:</p></div></div><div class="panel-body"><ul class="material-bullet-list">${material.learning_outcomes.map(x=>`<li>${escapeHTML(x)}</li>`).join('')}</ul></div></section>
      ${material.concepts.map((concept,i)=>`<section class="panel material-content-panel"><div class="panel-head"><div><span class="eyebrow">CONCEPT ${String(i+1).padStart(2,'0')}</span><h3>${escapeHTML(concept.heading)}</h3></div></div><div class="panel-body"><p>${escapeHTML(concept.explanation)}</p></div></section>`).join('')}
      <section class="panel material-content-panel"><div class="panel-head"><div><h3>Worked illustration</h3><p>Original example for understanding the method.</p></div></div><div class="panel-body"><div class="worked-example"><p>${escapeHTML(material.worked_example.prompt)}</p><small>${escapeHTML(material.worked_example.note)}</small></div></div></section>
      ${material.formula_cards.length ? `<section class="panel material-content-panel"><div class="panel-head"><div><h3>Formula and rule cards</h3><p>Review the expression and its assumptions.</p></div></div><div class="panel-body formula-card-grid">${material.formula_cards.map(f=>`<article class="formula-card"><b>${escapeHTML(f.name)}</b><code>${escapeHTML(f.expression)}</code><p>${escapeHTML(f.note)}</p></article>`).join('')}</div></section>` : ''}
      <section class="panel material-content-panel"><div class="panel-head"><div><h3>Common mistakes</h3><p>Check these before moving to practice.</p></div></div><div class="panel-body"><ul class="material-bullet-list warning-list">${material.common_mistakes.map(x=>`<li>${escapeHTML(x)}</li>`).join('')}</ul></div></section>
      <section class="panel material-content-panel"><div class="panel-head"><div><h3>Quick revision</h3><p>Use this as a short recap after solving questions.</p></div></div><div class="panel-body"><ul class="material-bullet-list">${material.quick_revision.map(x=>`<li>${escapeHTML(x)}</li>`).join('')}</ul></div></section>
      <section class="panel material-content-panel"><div class="panel-head"><div><h3>My personal notes</h3><p>Private notes saved to your student account.</p></div></div><div class="panel-body"><textarea id="material-personal-note" class="material-personal-note" maxlength="5000" placeholder="Write your own explanation, doubts or memory cues...">${escapeHTML(progress.personal_note || '')}</textarea><div class="material-note-actions"><small>Up to 5,000 characters · Private to your account</small><button class="btn btn-primary btn-small" data-action="save-material-note">Save my notes</button></div></div></section>
    </main><aside class="material-content-aside"><section class="panel"><div class="panel-head"><div><h3>Learning resources</h3><p>Curated references and external courses.</p></div></div><div class="panel-body material-resource-list">${material.resources.map(r=>`<article class="material-resource-item"><span class="resource-type">${escapeHTML(r.type.replaceAll('_',' '))}</span><b>${escapeHTML(r.title)}</b><small>${escapeHTML(r.provider)}</small><p>${escapeHTML(r.access_note)}</p>${r.url ? `<a href="${escapeHTML(r.url)}" target="_blank" rel="noreferrer">Open resource ↗</a>` : ''}</article>`).join('')}</div></section></aside></div>
  `;
  setIcons(host);
  document.getElementById('material-detail-status')?.addEventListener('change', async (event) => updateMaterial({ status: event.target.value }));
}

async function updateMaterial(payload) {
  const material = state.materialDetail;
  if (!material) return;
  try {
    await api(`/materials/${encodeURIComponent(material.id)}/progress?paper_code=${encodeURIComponent(state.profile.paper_code)}`, { method: 'PATCH', body: JSON.stringify(payload) });
    state.materialDetail = await api(`/materials/${encodeURIComponent(material.id)}?paper_code=${encodeURIComponent(state.profile.paper_code)}`);
    renderMaterialDetail();
    toast('Your study progress was saved.');
  } catch (error) { toast(error.message); }
}


async function renderMindmaps() {
  const host = document.getElementById('page-content');
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Building your concept map...</span></div>';
  const code = state.profile.paper_code;
  const sectionCode = state.mindmapSection || '';
  try {
    const data = await api(`/mindmaps?paper_code=${encodeURIComponent(code)}${sectionCode ? `&section_code=${encodeURIComponent(sectionCode)}` : ''}`);
    state.mindmapData = data;
    if (data.content_status === 'awaiting_structured_import' || !data.sections?.length) {
      host.innerHTML = `<div class="page-heading"><div><span class="eyebrow">STAGE 6 · VISUAL LEARNING</span><h1>Interactive mind maps</h1><p>Explore how the concepts in your GATE paper connect.</p></div></div><section class="syllabus-empty"><h3>Verified syllabus map is not imported for this paper yet</h3><p>GATEPath will create a map only after the paper's syllabus has been transcribed and reviewed. No speculative topic map is shown.</p><a class="btn btn-primary" href="${escapeHTML(data.official_syllabus_url || 'https://gate2027.iitm.ac.in/exam_papers_and_syllabus')}" target="_blank" rel="noreferrer">Open official syllabus ↗</a></section>`;
      return;
    }
    const topics = data.nodes.filter(node => node.type === 'topic');
    if (!state.mindmapSelected || !topics.some(node => node.topic_id === state.mindmapSelected)) state.mindmapSelected = topics[0]?.topic_id || null;
    host.innerHTML = `
      <div class="page-heading"><div><span class="eyebrow">STAGE 6 · VISUAL LEARNING</span><h1>Interactive mind maps</h1><p>Explore topics, subtopics and prerequisite relationships in ${escapeHTML(data.paper_code)}.</p></div><div class="heading-actions"><select class="select-control" id="mindmap-section-select" aria-label="Choose a subject">${data.sections.map(section=>`<option value="${escapeHTML(section.code)}" ${section.code===data.active_section.code?'selected':''}>${escapeHTML(section.name)}</option>`).join('')}</select><a class="btn btn-secondary" href="${escapeHTML(data.official_syllabus_url || '#')}" target="_blank" rel="noreferrer">Official syllabus ↗</a></div></div>
      <div class="material-metrics mindmap-metrics"><div class="syllabus-stat"><small>TOPICS</small><strong>${data.summary.topics}</strong></div><div class="syllabus-stat"><small>SUBTOPICS</small><strong>${data.summary.subtopics}</strong></div><div class="syllabus-stat"><small>PREREQUISITES</small><strong>${data.relationships.length}</strong></div><div class="syllabus-stat"><small>SYLLABUS VERSION</small><strong>2027</strong></div></div>
      <div class="mindmap-layout mindmap-workspace"><section class="panel mindmap-panel"><div class="panel-head"><div><h3>${escapeHTML(data.active_section.name)}</h3><p>Choose a topic node to open its learning details.</p></div><div class="mindmap-controls"><button class="icon-button" id="mindmap-zoom-out" aria-label="Zoom out">−</button><button class="icon-button" id="mindmap-zoom-in" aria-label="Zoom in">+</button><button class="btn btn-secondary btn-small" id="mindmap-fullscreen">Full screen</button><button class="btn btn-secondary btn-small" id="mindmap-export">Export SVG</button></div></div><div class="mindmap-legend"><span><i class="legend-root"></i>Subject</span><span><i class="legend-topic"></i>Topic</span><span><i class="legend-subtopic"></i>Subtopic</span><span><i class="legend-prerequisite"></i>Prerequisite</span></div><div class="mindmap-scroll" id="mindmap-scroll"><div class="mindmap-svg-wrap" id="mindmap-svg-wrap">${buildMindmapSvg(data)}</div></div><div class="mindmap-footnote">Topic relationships reflect the structured GATEPath prerequisite map. Verify official examination scope using the linked syllabus PDF.</div></section><aside class="panel mindmap-detail-panel" id="mindmap-detail-panel">${renderMindmapDetail(data)}</aside></div>
    `;
    setIcons(host);
    applyMindmapZoom();
  } catch (error) {
    host.innerHTML = `<section class="panel content-placeholder"><div><h2>Mind maps could not load</h2><p>${escapeHTML(error.message)}</p></div></section>`;
  }
}

function buildMindmapSvg(data) {
  const root = data.nodes.find(node => node.type === 'root');
  const topics = data.nodes.filter(node => node.type === 'topic');
  const subtopics = data.nodes.filter(node => node.type === 'subtopic');
  const width = 1080;
  const maxSubs = Math.max(1, ...topics.map(topic => subtopics.filter(node => node.parent_id === topic.id).length));
  const height = Math.max(560, topics.length * 125 + maxSubs * 25);
  const positions = new Map();
  positions.set(root.id, { x: 105, y: height / 2 });
  const topicX = 380;
  const subX = 760;
  const topicGap = (height - 100) / Math.max(topics.length, 1);
  topics.forEach((topic, index) => {
    const y = 50 + topicGap * (index + 0.5);
    positions.set(topic.id, { x: topicX, y });
    const children = subtopics.filter(node => node.parent_id === topic.id);
    const spread = Math.max(27, Math.min(43, 180 / Math.max(children.length, 1)));
    children.forEach((child, childIndex) => positions.set(child.id, { x: subX, y: y + (childIndex - (children.length - 1) / 2) * spread }));
  });
  const edges = data.edges.map(edge => {
    const from = positions.get(edge.source), to = positions.get(edge.target);
    if (!from || !to) return '';
    const x1 = from.x + (edge.source === root.id ? 88 : 112);
    const x2 = to.x - (edge.type === 'hierarchy' && edge.target.includes(':sub:') ? 100 : 112);
    const path = `M ${x1} ${from.y} C ${(x1+x2)/2} ${from.y}, ${(x1+x2)/2} ${to.y}, ${x2} ${to.y}`;
    return `<path class="mindmap-edge ${edge.type}" d="${path}"/>`;
  }).join('');
  const rootNode = `<g class="mindmap-svg-node root-node"><rect x="17" y="${height/2-38}" width="176" height="76" rx="15"/><text x="105" y="${height/2-3}" text-anchor="middle">${escapeHTML(root.label)}</text><text class="node-kicker" x="105" y="${height/2+17}" text-anchor="middle">GATE ${escapeHTML(data.paper_code)}</text></g>`;
  const topicNodes = topics.map(topic => {
    const pos = positions.get(topic.id);
    const selected = topic.topic_id === state.mindmapSelected;
    const statusText = topic.status === 'completed' ? 'Completed' : topic.status === 'in_progress' ? 'In progress' : 'Not started';
    return `<g class="mindmap-svg-node topic-node ${selected?'selected':''}" data-action="select-mindmap-topic" data-topic-id="${escapeHTML(topic.topic_id)}" tabindex="0" role="button" aria-label="Open ${escapeHTML(topic.label)}"><rect x="${pos.x-112}" y="${pos.y-32}" width="224" height="64" rx="12"/><text x="${pos.x}" y="${pos.y-5}" text-anchor="middle">${escapeHTML(topic.label)}</text><text class="node-kicker" x="${pos.x}" y="${pos.y+15}" text-anchor="middle">${escapeHTML(statusText)}${topic.bookmarked?' · Saved':''}</text></g>`;
  }).join('');
  const subNodes = subtopics.map(node => {
    const pos = positions.get(node.id);
    return `<g class="mindmap-svg-node subtopic-node" data-action="select-mindmap-topic" data-topic-id="${escapeHTML(node.topic_id)}" tabindex="0" role="button" aria-label="View parent topic for ${escapeHTML(node.label)}"><rect x="${pos.x-105}" y="${pos.y-14}" width="210" height="28" rx="8"/><text x="${pos.x}" y="${pos.y+4}" text-anchor="middle">${escapeHTML(node.label)}</text></g>`;
  }).join('');
  const prerequisites = data.edges.filter(edge => edge.type === 'prerequisite').map(edge => {
    const from=positions.get(edge.source),to=positions.get(edge.target); if(!from||!to)return '';
    return `<path class="mindmap-edge prerequisite" d="M ${from.x} ${from.y-27} C ${from.x+45} ${from.y-75}, ${to.x-45} ${to.y-75}, ${to.x} ${to.y-32}"/>`;
  }).join('');
  return `<svg id="mindmap-svg" class="mindmap-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHTML(data.active_section.name)} concept mind map">${edges}${prerequisites}${rootNode}${topicNodes}${subNodes}</svg>`;
}

function renderMindmapDetail(data) {
  const topic = data.nodes.find(node => node.type === 'topic' && node.topic_id === state.mindmapSelected);
  if (!topic) return '<div class="mindmap-detail-empty">Select a topic to inspect its learning path.</div>';
  const relationships = data.relationships.filter(item => item.topic_id === topic.topic_id);
  const materialAvailable = topic.note_available;
  return `<div class="mindmap-detail-inner"><span class="eyebrow">SELECTED TOPIC</span><h3>${escapeHTML(topic.label)}</h3><p class="mindmap-topic-id">${escapeHTML(topic.topic_id)} · ${escapeHTML(topic.status.replaceAll('_',' '))}</p><div class="mindmap-detail-actions">${materialAvailable?`<button class="btn btn-primary" data-action="open-material" data-topic-id="${escapeHTML(topic.topic_id)}">Open study notes ${icon('arrow',13)}</button>`:'<span class="status-pill">Study note unavailable</span>'}<button class="btn btn-secondary" data-action="go-view" data-view="syllabus">View syllabus</button></div><div class="mindmap-prerequisites"><b>Prerequisites</b>${relationships.length?relationships.map(item=>`<button data-action="open-mindmap-prerequisite" data-section-code="${escapeHTML(item.section_code)}" data-topic-id="${escapeHTML(item.prerequisite_id)}"><span>${escapeHTML(item.prerequisite_name)}</span><small>${item.available_in_map?'Open in this map':'Open subject map'} ↗</small></button>`).join(''):'<p>No prerequisite relationship is recorded for this topic.</p>'}</div><div class="mindmap-detail-tip">Use this map to understand topic structure. Topic prerequisites are learning guidance, not additional official syllabus requirements.</div></div>`;
}

function applyMindmapZoom() {
  const wrap = document.getElementById('mindmap-svg-wrap');
  if (wrap) wrap.style.transform = `scale(${state.mindmapZoom})`;
}

function downloadMindmapSvg() {
  const svg = document.getElementById('mindmap-svg');
  if (!svg) return toast('Open a mind map before exporting.');
  const clone = svg.cloneNode(true);
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  clone.setAttribute('width', '1080');
  const source = new XMLSerializer().serializeToString(clone);
  const blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `GATEPath-${state.profile.paper_code}-${state.mindmapSection || 'mindmap'}.svg`;
  link.click();
  URL.revokeObjectURL(url);
}

async function changeMindmapSection(sectionCode, topicId = null) {
  state.mindmapSection = sectionCode;
  state.mindmapSelected = topicId;
  await renderMindmaps();
}

async function renderPyqBank() {
  const host = document.getElementById('page-content');
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Loading verified previous-year question records...</span></div>';
  try {
    const code = state.profile.paper_code;
    const [catalog, summary] = await Promise.all([
      api(`/pyq/catalog?paper_code=${encodeURIComponent(code)}`),
      api(`/pyq/summary?paper_code=${encodeURIComponent(code)}`),
    ]);
    state.pyqCatalog = catalog;
    state.pyqSummary = summary;
    state.pyqYear = 2026;
    state.pyqSession = 'all';
    state.pyqType = 'all';
    state.pyqSection = 'all';
    state.pyqQuery = '';
    state.pyqBookmarked = false;
    await loadPyqQuestionItems();
  } catch (error) {
    host.innerHTML = `<section class="panel content-placeholder"><div><h2>PYQ bank could not load</h2><p>${escapeHTML(error.message)}</p></div></section>`;
  }
}

async function loadPyqQuestionItems() {
  const host = document.getElementById('page-content');
  if (!state.pyqCatalog) return;
  const params = new URLSearchParams({ paper_code: state.profile.paper_code, year: String(state.pyqYear) });
  if (state.pyqSession !== 'all') params.set('session', state.pyqSession);
  if (state.pyqType !== 'all') params.set('question_type', state.pyqType);
  if (state.pyqSection !== 'all') params.set('section_code', state.pyqSection);
  if (state.pyqQuery.trim()) params.set('q', state.pyqQuery.trim());
  if (state.pyqBookmarked) params.set('bookmarked_only', 'true');
  try {
    const result = await api(`/pyq/questions?${params.toString()}`);
    state.pyqItems = result.items || [];
    renderPyqBankContent(result);
  } catch (error) {
    host.innerHTML = `<section class="panel content-placeholder"><div><h2>Questions could not be loaded</h2><p>${escapeHTML(error.message)}</p></div></section>`;
  }
}

function renderPyqBankContent(result) {
  const host = document.getElementById('page-content');
  const catalog = state.pyqCatalog || {};
  const summary = state.pyqSummary || {};
  const paper = paperByCode(state.profile.paper_code);
  const imported = result.content_status === 'official_keys_metadata_imported';
  const yearOptions = [2026, 2025, 2024, 2023, 2022, 2021].map((year) => `<option value="${year}" ${Number(state.pyqYear) === year ? 'selected' : ''}>GATE ${year}</option>`).join('');
  const sessionOptions = [`<option value="all">All sessions</option>`, ...(catalog.sessions || []).map((session) => `<option value="${escapeHTML(session.session)}" ${state.pyqSession === session.session ? 'selected' : ''}>${escapeHTML(session.session)} · ${session.question_count} Qs</option>`)].join('');
  const sectionOptions = `<option value="all">All sections</option><option value="GA" ${state.pyqSection === 'GA' ? 'selected' : ''}>General Aptitude</option><option value="CS" ${state.pyqSection === 'CS' ? 'selected' : ''}>Computer Science subject</option>`;
  host.innerHTML = `
    <div class="page-heading"><div><span class="eyebrow">STAGE 7 · VERIFIED PREVIOUS PAPERS</span><h1>Previous-year question bank</h1><p>Practise against official GATE papers and final answer keys. Your attempts and bookmarks stay private to your account.</p></div><div class="heading-actions"><select class="select-control" id="paper-switcher" aria-label="Select GATE paper">${paperOptions(state.profile.paper_code)}</select></div></div>
    <div class="notice pyq-provenance"><span class="notice-icon">✓</span><div><strong>Question provenance matters.</strong><p>GATEPath stores verified question metadata and answer-key results. The original question wording and figures stay in the official IIT-hosted PDF; open the paper beside this workspace when attempting a question.</p></div></div>
    <div class="material-metrics pyq-metrics">
      <div class="syllabus-stat"><small>INTERACTIVE QUESTIONS</small><strong>${summary.total_questions || 0}</strong></div>
      <div class="syllabus-stat"><small>ATTEMPTED</small><strong>${summary.attempted_questions || 0}</strong></div>
      <div class="syllabus-stat"><small>LATEST ACCURACY</small><strong>${summary.accuracy_percent || 0}%</strong></div>
      <div class="syllabus-stat"><small>BOOKMARKED</small><strong>${summary.bookmarked_questions || 0}</strong></div>
    </div>
    <section class="panel pyq-toolbar-panel">
      <div class="panel-head"><div><h3>Find a question</h3><p>${escapeHTML(paper.code)} · Interactive answer checking currently imported for GATE 2026 CS-1 and CS-2.</p></div><span class="status-pill">${catalog.interactive_question_count || 0} verified keys</span></div>
      <div class="pyq-filters">
        <label class="form-field"><span>Year</span><select class="select-control" id="pyq-year-filter">${yearOptions}</select></label>
        <label class="form-field"><span>Session</span><select class="select-control" id="pyq-session-filter">${sessionOptions}</select></label>
        <label class="form-field"><span>Question type</span><select class="select-control" id="pyq-type-filter"><option value="all">All types</option><option value="MCQ" ${state.pyqType==='MCQ'?'selected':''}>MCQ</option><option value="MSQ" ${state.pyqType==='MSQ'?'selected':''}>MSQ</option><option value="NAT" ${state.pyqType==='NAT'?'selected':''}>NAT</option></select></label>
        <label class="form-field"><span>Section</span><select class="select-control" id="pyq-section-filter">${sectionOptions}</select></label>
        <label class="syllabus-search pyq-search">${icon('search',14)}<input type="search" id="pyq-search" placeholder="Search topic, question ID or session" value="${escapeHTML(state.pyqQuery)}" aria-label="Search PYQs"/></label>
        <label class="pyq-bookmark-filter"><input type="checkbox" id="pyq-bookmarked-filter" ${state.pyqBookmarked?'checked':''}/> Bookmarked only</label>
      </div>
    </section>
    <div class="pyq-results-head"><div><span class="eyebrow">${imported ? 'OFFICIAL ANSWER KEY METADATA' : 'OFFICIAL ARCHIVE'}</span><h2>${imported ? `${result.count} matching questions` : `GATE ${state.pyqYear} archive`}</h2></div>${imported ? '<small>Answer key is checked after you submit.</small>' : ''}</div>
    ${imported ? `<div class="pyq-question-grid">${state.pyqItems.map(renderPyqCard).join('') || '<div class="empty-state"><strong>No questions match these filters</strong><p>Try another session, type or search term.</p></div>'}</div>` : `<section class="syllabus-empty"><h3>Interactive import is not available for this year yet</h3><p>${escapeHTML(result.notice || 'Open the official archive to access the paper and answer key. This year is not represented as an imported question set.')}</p><a class="btn btn-primary" href="${escapeHTML((catalog.archive_sources||[]).find((source)=>String(source.year)===String(state.pyqYear))?.url || 'https://gate2026.iitg.ac.in/download.html')}" target="_blank" rel="noreferrer">Open official GATE archive ↗</a></section>`}
    <section class="panel pyq-archive-panel"><div class="panel-head"><div><h3>Official paper archives</h3><p>Original question papers and keys hosted by GATE organising institutes.</p></div></div><div class="pyq-archive-list">${(catalog.archive_sources||[]).map(source=>`<a class="pyq-archive-item" href="${escapeHTML(source.url)}" target="_blank" rel="noreferrer"><span class="pyq-archive-year">${escapeHTML(String(source.year))}</span><span><b>${escapeHTML(source.title)}</b><small>${escapeHTML(source.status.replaceAll('_',' '))}</small></span><span aria-hidden="true">↗</span></a>`).join('')}</div></section>
    <p class="pyq-footer-note">GATEPath’s interactive 2026 import contains answer-key metadata, verified answer/range values, source references and a small set of original worked explanations. Additional year/paper imports and editorial solutions require review before publication.</p>
  `;
  setIcons(host);
}

function renderPyqCard(item) {
  const attempt = item.last_attempt;
  const topic = item.topic_name || item.section_name;
  const stateLabel = attempt ? (attempt.is_correct ? 'Correct last attempt' : 'Review last attempt') : 'Not attempted';
  return `<article class="pyq-card">
    <div class="pyq-card-top"><span class="pyq-id">${escapeHTML(item.session)} · Q${String(item.question_number).padStart(2,'0')}</span><span class="pyq-type ${escapeHTML(item.question_type.toLowerCase())}">${escapeHTML(item.question_type)}</span></div>
    <h3>${escapeHTML(item.editorial_label || topic || 'Official GATE question')}</h3>
    <div class="pyq-card-meta"><span>${item.marks} mark${item.marks===1?'':'s'}</span><span>${escapeHTML(item.source_section_code)}</span><span>${escapeHTML(stateLabel)}</span></div>
    ${item.topic_id ? `<div class="pyq-topic-tag">${escapeHTML(item.topic_name)} · ${escapeHTML(item.topic_id)}</div>` : '<div class="pyq-topic-tag">Topic mapping pending editorial review</div>'}
    <div class="pyq-card-actions"><a class="btn btn-secondary btn-small" href="${escapeHTML(item.paper_url)}${item.pdf_page ? `#page=${item.pdf_page}` : ''}" target="_blank" rel="noreferrer">Open official paper ↗</a><button class="btn btn-primary btn-small" data-action="open-pyq-attempt" data-question-id="${escapeHTML(item.id)}">${attempt ? 'Try again' : 'Enter answer'}</button><button class="pyq-bookmark-button ${item.bookmarked?'active':''}" data-action="toggle-pyq-bookmark" data-question-id="${escapeHTML(item.id)}" data-bookmarked="${item.bookmarked?'true':'false'}" aria-label="${item.bookmarked?'Remove bookmark':'Bookmark question'}">${icon('bookmark',14)}</button></div>
  </article>`;
}

async function openPyqAttempt(questionId) {
  try {
    const question = await api(`/pyq/questions/${encodeURIComponent(questionId)}`);
    const sourceHref = `${question.paper_url}${question.pdf_page ? `#page=${question.pdf_page}` : ''}`;
    let answerControl = '';
    if (question.question_type === 'MCQ') {
      answerControl = `<div class="pyq-answer-options">${['A','B','C','D'].map(option=>`<label><input type="radio" name="pyq-answer" value="${option}" required/><span>${option}</span></label>`).join('')}</div>`;
    } else if (question.question_type === 'MSQ') {
      answerControl = `<div class="pyq-answer-options">${['A','B','C','D'].map(option=>`<label><input type="checkbox" name="pyq-answer" value="${option}"/><span>${option}</span></label>`).join('')}</div><small class="pyq-hint">Select every option you believe is correct. GATE MSQ scoring is all-or-nothing.</small>`;
    } else {
      answerControl = `<label class="form-field"><span>Your numerical answer</span><input class="form-control" id="pyq-nat-answer" name="pyq-answer" type="number" step="any" required placeholder="Enter a number"/></label>`;
    }
    openModal(`${question.session} · Question ${question.question_number}`, `${question.year} · ${question.question_type} · ${question.marks} MARK${question.marks===1?'':'S'}`, `
      <div class="pyq-attempt-context"><p>${escapeHTML(question.editorial_label || question.topic_name || question.section_name)}</p><a class="btn btn-secondary btn-small" href="${escapeHTML(sourceHref)}" target="_blank" rel="noreferrer">Open official question paper ↗</a><small>${escapeHTML(question.question_text_notice)}</small></div>
      <form id="pyq-answer-form" data-question-id="${escapeHTML(question.id)}" data-opened-at="${Date.now()}">
        <div class="form-field"><span class="pyq-field-label">${question.question_type==='MSQ'?'Choose your options':question.question_type==='MCQ'?'Choose one option':'Enter your answer'}</span>${answerControl}</div>
        <div class="modal-actions"><button class="btn btn-secondary" type="button" data-action="close-modal">Cancel</button><button class="btn btn-primary" type="submit">Submit answer ${icon('arrow',13)}</button></div>
      </form>`);
    document.getElementById('pyq-answer-form')?.addEventListener('submit', submitPyqAnswer);
  } catch (error) { toast(error.message); }
}

async function submitPyqAnswer(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const questionId = form.dataset.questionId;
  const question = await api(`/pyq/questions/${encodeURIComponent(questionId)}`);
  let answer = '';
  if (question.question_type === 'MSQ') answer = [...form.querySelectorAll('input[name="pyq-answer"]:checked')].map(input=>input.value).join(',');
  else if (question.question_type === 'MCQ') answer = form.querySelector('input[name="pyq-answer"]:checked')?.value || '';
  else answer = form.querySelector('#pyq-nat-answer')?.value || '';
  if (!answer) return toast('Please enter or select your answer.');
  const spent = Math.max(0, Math.floor((Date.now() - Number(form.dataset.openedAt || Date.now())) / 1000));
  try {
    const result = await api(`/pyq/questions/${encodeURIComponent(questionId)}/attempt`, { method: 'POST', body: JSON.stringify({ answer, spent_seconds: spent }) });
    const status = result.is_correct ? 'Correct answer' : 'Answer needs review';
    const solutionHTML = result.solution ? `<section class="pyq-solution"><h4>${escapeHTML(result.solution.title)}</h4><ol>${result.solution.steps.map(step=>`<li>${escapeHTML(step)}</li>`).join('')}</ol><small>${escapeHTML(result.solution.note || '')}</small></section>` : `<div class="notice pyq-pending-solution"><div><strong>Verified final key available</strong><p>A step-by-step editorial explanation has not yet been reviewed for this question. Use the official question and key PDFs for reference.</p></div></div>`;
    openModal(status, `${result.awarded_marks >= 0 ? '+' : ''}${Number(result.awarded_marks).toFixed(2)} / ${result.maximum_marks} MARKS`, `
      <div class="pyq-result ${result.is_correct?'is-correct':'is-incorrect'}"><div class="pyq-result-icon">${result.is_correct?'✓':'↻'}</div><div><h3>${result.is_correct?'Well done!':'Keep learning.'}</h3><p>Your answer: <b>${escapeHTML(result.submitted_answer)}</b> · Correct answer: <b>${escapeHTML(result.correct_answer)}</b></p><small>${escapeHTML(result.scoring_note)}</small></div></div>
      ${result.answer_range ? `<p class="pyq-answer-range">Accepted numerical range: ${escapeHTML(String(result.answer_range[0]))} – ${escapeHTML(String(result.answer_range[1]))}</p>` : ''}
      ${solutionHTML}
      <div class="pyq-result-links"><a href="${escapeHTML(result.paper_url)}" target="_blank" rel="noreferrer">Official paper ↗</a><a href="${escapeHTML(result.answer_key_url)}" target="_blank" rel="noreferrer">Official answer key ↗</a></div>
      <div class="modal-actions"><button class="btn btn-secondary" type="button" data-action="close-modal">Close</button><button class="btn btn-primary" type="button" data-action="refresh-pyq">Back to question bank</button></div>`);
    await refreshPyqSummary();
  } catch (error) { toast(error.message); }
}

async function refreshPyqSummary() {
  try { state.pyqSummary = await api(`/pyq/summary?paper_code=${encodeURIComponent(state.profile.paper_code)}`); }
  catch (_) { /* Keep the last successful summary visible. */ }
}

async function togglePyqBookmark(questionId, currentlyBookmarked) {
  try {
    await api(`/pyq/bookmarks/${encodeURIComponent(questionId)}`, { method: 'PUT', body: JSON.stringify({ bookmarked: !currentlyBookmarked }) });
    await refreshPyqSummary();
    await loadPyqQuestionItems();
    toast(currentlyBookmarked ? 'Question removed from bookmarks.' : 'Question saved to bookmarks.');
  } catch (error) { toast(error.message); }
}

function practiceDifficultyLabel(value) {
  return value === 'Beginner' ? 'Beginner' : value === 'Intermediate' ? 'Intermediate' : value === 'Advanced' ? 'Advanced' : 'All levels';
}

async function loadPracticeQuestions() {
  const filters = state.practiceFilters;
  const params = new URLSearchParams({ paper_code: state.profile.paper_code, limit: '100' });
  if (filters.section_code !== 'all') params.set('section_code', filters.section_code);
  if (filters.topic_id !== 'all') params.set('topic_id', filters.topic_id);
  if (filters.difficulty !== 'all') params.set('difficulty', filters.difficulty);
  if (filters.question_type !== 'all') params.set('question_type', filters.question_type);
  if (filters.q.trim()) params.set('q', filters.q.trim());
  const payload = await api(`/practice/questions?${params.toString()}`);
  state.practiceItems = payload.items || [];
  return payload;
}

function practiceQuestionCard(item) {
  const status = item.attempted
    ? (item.last_attempt?.is_correct ? '<span class="practice-status is-correct">Solved correctly</span>' : '<span class="practice-status is-wrong">Review mistake</span>')
    : '<span class="practice-status">Not attempted</span>';
  return `<article class="practice-question-card"><div class="practice-card-top"><span class="practice-question-id">${escapeHTML(item.id)}</span><span class="practice-type ${item.question_type.toLowerCase()}">${escapeHTML(item.question_type)}</span></div><h3>${escapeHTML(item.prompt)}</h3><div class="practice-meta"><span>${escapeHTML(item.section_name)}</span><span>${escapeHTML(item.topic_name)}</span><span>${escapeHTML(practiceDifficultyLabel(item.difficulty))}</span><span>${item.marks} mark${item.marks === 1 ? '' : 's'}</span></div><div class="practice-card-bottom">${status}<small>Original GATEPath practice</small></div></article>`;
}

async function renderPractice() {
  const host = document.getElementById('page-content');
  // Resume an in-progress server-side session when navigating back or refreshing.
  const savedSessionId = sessionStorage.getItem('gatepath-practice-session');
  const sessionId = state.practiceSession?.id || savedSessionId;
  if (sessionId) {
    try {
      const session = await api(`/practice/sessions/${encodeURIComponent(sessionId)}`);
      if (session.status === 'active') {
        state.practiceSession = session;
        state.practiceCurrentIndex = Math.min(state.practiceCurrentIndex, Math.max(0, session.questions.length - 1));
        renderPracticeSession();
        return;
      }
      sessionStorage.removeItem('gatepath-practice-session');
      state.practiceSession = null;
      if (session.result) {
        state.practiceFinishedResult = { ...session.result, status: session.status, question_count: session.question_count };
        state.practiceSummary = await api(`/practice/summary?paper_code=${encodeURIComponent(state.profile.paper_code)}`);
        renderPracticeResult(session.status === 'expired');
        return;
      }
    } catch (_) {
      sessionStorage.removeItem('gatepath-practice-session');
      state.practiceSession = null;
    }
  }

  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Preparing your practice workspace...</span></div>';
  try {
    const code = state.profile.paper_code;
    const [catalog, daily, summary] = await Promise.all([
      api(`/practice/catalog?paper_code=${encodeURIComponent(code)}`),
      api(`/practice/daily-challenge?paper_code=${encodeURIComponent(code)}`),
      api(`/practice/summary?paper_code=${encodeURIComponent(code)}`),
    ]);
    state.practiceCatalog = catalog;
    state.practiceDaily = daily;
    state.practiceSummary = summary;
    if (!catalog.total_questions) {
      host.innerHTML = `<div class="page-heading"><div><span class="eyebrow">STAGE 8 · PRACTICE ENGINE</span><h1>Practice centre</h1><p>Build mastery through focused questions and timed sessions.</p></div></div><section class="syllabus-empty"><h3>Practice content is not imported for ${escapeHTML(code)} yet</h3><p>The CS practice pilot is available first. Other paper question sets will appear after they are authored, mapped and reviewed. No generic questions are presented as verified GATE content.</p><a class="btn btn-primary" href="${escapeHTML(catalog.official_syllabus_url || 'https://gate2027.iitm.ac.in/exam_papers_and_syllabus')}" target="_blank" rel="noreferrer">Open official syllabus ↗</a></section>`;
      return;
    }
    await loadPracticeQuestions();
    renderPracticeCatalogue();
  } catch (error) {
    host.innerHTML = `<section class="panel content-placeholder"><div><h2>Practice centre could not load</h2><p>${escapeHTML(error.message)}</p></div></section>`;
  }
}

function renderPracticeCatalogue() {
  const host = document.getElementById('page-content');
  const catalog = state.practiceCatalog;
  const daily = state.practiceDaily;
  const summary = state.practiceSummary || {};
  const filters = state.practiceFilters;
  const sections = catalog.sections || [];
  const activeSection = sections.find(section => section.code === filters.section_code);
  const topicList = activeSection?.topics || sections.flatMap(section => section.topics || []);
  const topics = filters.section_code === 'all' ? topicList : topicList;
  const dailyButton = daily.completed
    ? '<span class="practice-status is-correct">Today’s challenge completed</span>'
    : `<button class="btn btn-primary" data-action="practice-start-daily">Start daily challenge ${icon('arrow',13)}</button>`;
  host.innerHTML = `
    <div class="page-heading"><div><span class="eyebrow">STAGE 8 · BUILD MASTERY</span><h1>Practice centre</h1><p>Practise original questions mapped to your ${escapeHTML(catalog.paper_code)} syllabus. Your attempts and mistakes are saved privately.</p></div><span class="status-pill">${catalog.total_questions} pilot questions</span></div>
    <div class="notice practice-origin-notice"><span class="notice-icon">ⓘ</span><div><strong>Content transparency</strong><p>${escapeHTML(catalog.content_origin || 'GATEPath original practice material.')} ${escapeHTML(catalog.editorial_status || '')} These are not official GATE questions or PYQs. Verify concepts against the official syllabus and standard references.</p></div></div>
    <section class="practice-daily-panel"><div class="practice-daily-copy"><span class="eyebrow">DAILY GATE CHALLENGE · ${escapeHTML(daily.date || 'TODAY')}</span><h2>Five questions. A focused session.</h2><p>A short mixed-topic set selected for today. Your challenge resets with the date.</p><div class="practice-daily-meta"><span>${daily.question_count || 5} questions</span><span>~${daily.estimated_minutes || 10} minutes</span><span>MCQ · MSQ · NAT</span></div></div><div class="practice-daily-action">${dailyButton}</div></section>
    <div class="practice-metrics-grid"><div class="practice-metric"><small>QUESTIONS ATTEMPTED</small><strong>${summary.attempted_questions || 0}</strong><span>Unique questions</span></div><div class="practice-metric"><small>ACCURACY</small><strong>${summary.accuracy_percent || 0}%</strong><span>Latest attempt per question</span></div><div class="practice-metric"><small>QUIZZES COMPLETED</small><strong>${summary.sessions_completed || 0}</strong><span>${summary.sessions_total || 0} total sessions</span></div><div class="practice-metric"><small>QUESTIONS AVAILABLE</small><strong>${catalog.total_questions}</strong><span>Original pilot set</span></div></div>
    <section class="panel practice-builder-panel"><div class="panel-head"><div><h3>Build a focused practice set</h3><p>Choose a subject, topic and difficulty, then set your time limit.</p></div><span class="status-pill">Custom practice</span></div><div class="practice-filter-grid">
      <label class="practice-filter-field"><span>Subject</span><select class="select-control" id="practice-section-filter"><option value="all">All subjects</option>${sections.map(section=>`<option value="${escapeHTML(section.code)}" ${filters.section_code===section.code?'selected':''}>${escapeHTML(section.name)}</option>`).join('')}</select></label>
      <label class="practice-filter-field"><span>Topic</span><select class="select-control" id="practice-topic-filter"><option value="all">All topics</option>${topics.map(topic=>`<option value="${escapeHTML(topic.id)}" ${filters.topic_id===topic.id?'selected':''}>${escapeHTML(topic.name)}</option>`).join('')}</select></label>
      <label class="practice-filter-field"><span>Difficulty</span><select class="select-control" id="practice-difficulty-filter"><option value="all" ${filters.difficulty==='all'?'selected':''}>All levels</option><option value="Beginner" ${filters.difficulty==='Beginner'?'selected':''}>Beginner</option><option value="Intermediate" ${filters.difficulty==='Intermediate'?'selected':''}>Intermediate</option><option value="Advanced" ${filters.difficulty==='Advanced'?'selected':''}>Advanced</option></select></label>
      <label class="practice-filter-field"><span>Question type</span><select class="select-control" id="practice-type-filter"><option value="all" ${filters.question_type==='all'?'selected':''}>All types</option><option value="MCQ" ${filters.question_type==='MCQ'?'selected':''}>MCQ</option><option value="MSQ" ${filters.question_type==='MSQ'?'selected':''}>MSQ</option><option value="NAT" ${filters.question_type==='NAT'?'selected':''}>NAT</option></select></label>
      <label class="practice-filter-field"><span>Questions</span><select class="select-control" id="practice-count-filter"><option>5</option><option selected>10</option><option>15</option><option>20</option><option>30</option></select></label>
      <label class="practice-filter-field"><span>Time limit</span><select class="select-control" id="practice-duration-filter"><option value="5">5 minutes</option><option value="10">10 minutes</option><option value="15" selected>15 minutes</option><option value="20">20 minutes</option><option value="30">30 minutes</option><option value="45">45 minutes</option></select></label>
    </div><div class="practice-builder-actions"><label class="practice-search">${icon('search',14)}<input id="practice-search" type="search" placeholder="Search question or concept" value="${escapeHTML(filters.q)}"/></label><button class="btn btn-secondary" data-action="practice-clear-filters">Clear filters</button><button class="btn btn-primary" data-action="practice-start-filtered">Start practice ${icon('arrow',13)}</button></div></section>
    <div class="practice-results-head"><div><h3>Available practice questions</h3><p>${state.practiceItems.length} questions match your filters</p></div><span class="practice-question-total">${catalog.total_questions} in this pilot</span></div>
    <div class="practice-question-grid">${state.practiceItems.length ? state.practiceItems.map(practiceQuestionCard).join('') : '<div class="empty-state"><strong>No questions match these filters</strong><p>Change the topic or difficulty to see more practice questions.</p></div>'}</div>
    <div class="practice-insights-grid"><section class="panel"><div class="panel-head"><div><h3>Topics to strengthen</h3><p>Based on your latest attempt for each question.</p></div></div><div class="panel-body practice-weak-list">${summary.weak_topics?.length ? summary.weak_topics.map(topic=>`<div class="practice-weak-item"><span><b>${escapeHTML(topic.topic_name)}</b><small>${topic.attempted} attempted · ${topic.correct} correct</small></span><strong>${topic.accuracy_percent}%</strong></div>`).join('') : '<div class="empty-state"><strong>No weak topics yet</strong><p>Complete a practice session to receive topic-level feedback.</p></div>'}</div></section><section class="panel"><div class="panel-head"><div><h3>Recent mistakes</h3><p>Questions that need another look.</p></div></div><div class="panel-body practice-mistake-list">${summary.recent_mistakes?.length ? summary.recent_mistakes.slice(0,5).map(item=>`<div class="practice-mistake-item"><b>${escapeHTML(item.topic_name)}</b><p>${escapeHTML(item.prompt)}</p><small>Your answer: ${escapeHTML(item.submitted_answer)} · Expected: ${escapeHTML(item.correct_answer)}</small></div>`).join('') : '<div class="empty-state"><strong>No recorded mistakes</strong><p>Your incorrect answers will appear here for review.</p></div>'}</div></section></div>
    <p class="practice-content-footnote">Practice content is GATEPath-authored and is marked as a draft pilot pending academic review. Official GATE questions remain in the separate PYQ bank.</p>
  `;
  setIcons(host);
}

async function updatePracticeFiltersFromUI() {
  const section = document.getElementById('practice-section-filter')?.value || 'all';
  const topic = document.getElementById('practice-topic-filter')?.value || 'all';
  state.practiceFilters.section_code = section;
  state.practiceFilters.topic_id = topic;
  state.practiceFilters.difficulty = document.getElementById('practice-difficulty-filter')?.value || 'all';
  state.practiceFilters.question_type = document.getElementById('practice-type-filter')?.value || 'all';
  state.practiceFilters.q = document.getElementById('practice-search')?.value || '';
  try {
    await loadPracticeQuestions();
    renderPracticeCatalogue();
  } catch (error) { toast(error.message); }
}

async function startPracticeSession(mode = 'custom') {
  const filters = state.practiceFilters;
  const payload = {
    paper_code: state.profile.paper_code,
    mode,
    section_code: mode === 'daily' || filters.section_code === 'all' ? null : filters.section_code,
    topic_id: mode === 'daily' || filters.topic_id === 'all' ? null : filters.topic_id,
    difficulty: mode === 'daily' || filters.difficulty === 'all' ? null : filters.difficulty,
    question_type: mode === 'daily' || filters.question_type === 'all' ? null : filters.question_type,
    question_count: mode === 'daily' ? 5 : Number(document.getElementById('practice-count-filter')?.value || 10),
    duration_minutes: mode === 'daily' ? 10 : Number(document.getElementById('practice-duration-filter')?.value || 15),
  };
  if (mode === 'custom' && (payload.topic_id || payload.section_code)) payload.mode = 'topic';
  try {
    const session = await api('/practice/sessions', { method: 'POST', body: JSON.stringify(payload) });
    state.practiceSession = session;
    state.practiceCurrentIndex = 0;
    state.practiceQuestionOpenedAt = Date.now();
    state.practiceFinishedResult = null;
    sessionStorage.setItem('gatepath-practice-session', session.id);
    renderPracticeSession();
  } catch (error) { toast(error.message); }
}

function clearPracticeTimer() {
  if (state.practiceTimerHandle) window.clearInterval(state.practiceTimerHandle);
  state.practiceTimerHandle = null;
}

function formatPracticeClock(seconds) {
  const safe = Math.max(0, Number(seconds) || 0);
  return `${String(Math.floor(safe / 60)).padStart(2, '0')}:${String(safe % 60).padStart(2, '0')}`;
}

function startPracticeCountdown() {
  clearPracticeTimer();
  const session = state.practiceSession;
  if (!session || session.status !== 'active') return;
  const update = () => {
    const remaining = Math.max(0, Math.ceil(Number(session.expires_at) - Date.now() / 1000));
    const output = document.getElementById('practice-countdown');
    if (output) output.textContent = formatPracticeClock(remaining);
    output?.classList.toggle('is-urgent', remaining <= 60);
    if (remaining <= 0) {
      clearPracticeTimer();
      finishPracticeSession(true);
    }
  };
  update();
  state.practiceTimerHandle = window.setInterval(update, 1000);
}

function practiceAnswerControl(question) {
  if (question.question_type === 'MCQ') {
    return `<div class="practice-answer-options">${(question.options || []).map(option=>`<label><input type="radio" name="practice-answer" value="${escapeHTML(option.key)}" required/><span><b>${escapeHTML(option.key)}</b>${escapeHTML(option.text)}</span></label>`).join('')}</div>`;
  }
  if (question.question_type === 'MSQ') {
    return `<div class="practice-answer-options">${(question.options || []).map(option=>`<label><input type="checkbox" name="practice-answer" value="${escapeHTML(option.key)}"/><span><b>${escapeHTML(option.key)}</b>${escapeHTML(option.text)}</span></label>`).join('')}</div><small class="practice-answer-hint">Select every option you believe is correct. Exact option set required.</small>`;
  }
  return '<label class="practice-nat-field"><span>Your numerical answer</span><input class="form-control" id="practice-nat-answer" type="number" step="any" required placeholder="Enter a number"/></label>';
}

function renderPracticeSession() {
  clearPracticeTimer();
  const host = document.getElementById('page-content');
  const session = state.practiceSession;
  if (!session || !session.questions?.length) { renderPractice(); return; }
  const question = session.questions[state.practiceCurrentIndex] || session.questions[0];
  const result = question.result;
  const answered = question.attempted;
  const solution = result?.solution ? `<section class="practice-solution"><h4>${escapeHTML(result.solution.title)}</h4><ol>${result.solution.steps.map(step=>`<li>${escapeHTML(step)}</li>`).join('')}</ol><small>${escapeHTML(result.solution.note || '')}</small></section>` : '';
  const resultHTML = result ? `<div class="practice-result ${result.is_correct?'is-correct':'is-incorrect'}"><div><b>${result.is_correct?'Correct — well done':'Review this answer'}</b><p>Your answer: ${escapeHTML(question.last_attempt?.submitted_answer || '')} · Correct answer: ${escapeHTML(result.correct_answer)}</p><strong>${result.awarded_marks >= 0 ? '+' : ''}${Number(result.awarded_marks).toFixed(2)} / ${question.marks} marks</strong></div></div>${solution}` : '';
  const palette = session.questions.map((item,index)=>`<button class="practice-palette-button ${index===state.practiceCurrentIndex?'is-current':''} ${item.attempted?'is-answered':''}" data-action="practice-palette" data-index="${index}" aria-label="Open question ${index+1}">${index+1}</button>`).join('');
  host.innerHTML = `
    <div class="practice-session-top"><button class="btn btn-secondary btn-small" data-action="practice-back">← Practice centre</button><div><span class="eyebrow">${escapeHTML(session.mode.toUpperCase())} SESSION · ${escapeHTML(session.paper_code)}</span><h1>Focused practice</h1></div><div class="practice-timer-box"><small>TIME REMAINING</small><strong id="practice-countdown">--:--</strong></div></div>
    <div class="practice-session-layout"><section class="panel practice-player-panel"><div class="practice-player-head"><div><span class="practice-question-id">QUESTION ${state.practiceCurrentIndex+1} OF ${session.questions.length}</span><h2>${escapeHTML(question.topic_name)}</h2></div><div class="practice-player-tags"><span class="practice-type ${question.question_type.toLowerCase()}">${escapeHTML(question.question_type)}</span><span>${escapeHTML(question.difficulty)}</span><span>${question.marks} mark${question.marks===1?'':'s'}</span></div></div><div class="practice-question-prompt">${escapeHTML(question.prompt)}</div>${answered ? resultHTML : `<form id="practice-answer-form" data-question-id="${escapeHTML(question.id)}" data-opened-at="${Date.now()}"><div class="practice-answer-label">${question.question_type==='MSQ'?'Select all correct options':question.question_type==='MCQ'?'Select one option':'Enter your numerical answer'}</div>${practiceAnswerControl(question)}<div class="practice-answer-actions"><small>Answer is checked when you submit. You cannot change it later in this session.</small><button class="btn btn-primary" type="submit">Check answer ${icon('arrow',13)}</button></div></form>`}<div class="practice-player-nav"><button class="btn btn-secondary" data-action="practice-prev" ${state.practiceCurrentIndex===0?'disabled':''}>← Previous</button><button class="btn btn-secondary" data-action="practice-next" ${state.practiceCurrentIndex===session.questions.length-1?'disabled':''}>Next question →</button></div></section><aside class="panel practice-palette-panel"><div class="panel-head"><div><h3>Question palette</h3><p>${session.questions.filter(item=>item.attempted).length} of ${session.questions.length} answered</p></div></div><div class="practice-palette-grid">${palette}</div><div class="practice-palette-legend"><span><i class="answered"></i> Answered</span><span><i class="current"></i> Current</span><span><i></i> Pending</span></div><div class="practice-session-progress"><div><span>Attempted</span><b>${session.questions.filter(item=>item.attempted).length}/${session.questions.length}</b></div><div class="practice-progress-track"><span style="width:${session.questions.filter(item=>item.attempted).length/session.questions.length*100}%"></span></div></div><button class="btn btn-primary practice-finish-button" data-action="practice-finish">Finish session</button><small class="practice-finish-note">Unanswered questions receive zero marks. An incorrect MCQ has a one-third mark penalty.</small></aside></div>
  `;
  setIcons(host);
  const form = document.getElementById('practice-answer-form');
  form?.addEventListener('submit', submitPracticeAnswer);
  startPracticeCountdown();
}

async function submitPracticeAnswer(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const questionId = form.dataset.questionId;
  const question = state.practiceSession?.questions.find(item=>item.id===questionId);
  if (!question) return;
  let answer = '';
  if (question.question_type === 'MSQ') answer = [...form.querySelectorAll('input[name="practice-answer"]:checked')].map(input=>input.value).join(',');
  else if (question.question_type === 'MCQ') answer = form.querySelector('input[name="practice-answer"]:checked')?.value || '';
  else answer = form.querySelector('#practice-nat-answer')?.value || '';
  if (!answer) return toast('Please select or enter your answer.');
  const spent = Math.max(0, Math.floor((Date.now() - Number(form.dataset.openedAt || Date.now())) / 1000));
  try {
    await api(`/practice/sessions/${encodeURIComponent(state.practiceSession.id)}/attempt`, { method: 'POST', body: JSON.stringify({ question_id: questionId, answer, spent_seconds: spent }) });
    state.practiceSession = await api(`/practice/sessions/${encodeURIComponent(state.practiceSession.id)}`);
    state.practiceQuestionOpenedAt = Date.now();
    renderPracticeSession();
    toast('Answer checked. Review the explanation before moving on.');
  } catch (error) { toast(error.message); }
}

async function finishPracticeSession(fromTimer = false) {
  const sessionId = state.practiceSession?.id || sessionStorage.getItem('gatepath-practice-session');
  if (!sessionId) return;
  try {
    const result = await api(`/practice/sessions/${encodeURIComponent(sessionId)}/finish`, { method: 'POST', body: '{}' });
    clearPracticeTimer();
    sessionStorage.removeItem('gatepath-practice-session');
    state.practiceFinishedResult = result;
    state.practiceSession = null;
    state.practiceSummary = await api(`/practice/summary?paper_code=${encodeURIComponent(state.profile.paper_code)}`);
    renderPracticeResult(fromTimer);
  } catch (error) { toast(error.message); }
}

function renderPracticeResult(fromTimer = false) {
  const host = document.getElementById('page-content');
  const result = state.practiceFinishedResult || {};
  const summary = state.practiceSummary || {};
  const score = Number(result.awarded_marks || 0);
  host.innerHTML = `<div class="page-heading"><div><span class="eyebrow">PRACTICE SESSION · ${escapeHTML(result.status || 'completed')}</span><h1>${fromTimer ? 'Time is up' : 'Session complete'}</h1><p>Your attempt has been saved. Review topic-level feedback and keep improving.</p></div><button class="btn btn-primary" data-action="practice-return">Back to practice centre ${icon('arrow',13)}</button></div><section class="practice-finish-hero"><div><span class="eyebrow">YOUR SESSION SCORE</span><strong>${score >= 0 ? '+' : ''}${score.toFixed(2)} <small>/ ${Number(result.maximum_marks || 0).toFixed(2)}</small></strong><p>${result.correct_count || 0} correct · ${result.attempted_count || 0} attempted · ${result.question_count || 0} total questions</p></div><div class="practice-finish-accuracy"><strong>${result.accuracy_percent || 0}%</strong><small>Accuracy</small></div></section><div class="practice-metrics-grid"><div class="practice-metric"><small>UNIQUE QUESTIONS</small><strong>${summary.attempted_questions || 0}</strong></div><div class="practice-metric"><small>OVERALL ACCURACY</small><strong>${summary.accuracy_percent || 0}%</strong></div><div class="practice-metric"><small>COMPLETED SESSIONS</small><strong>${summary.sessions_completed || 0}</strong></div><div class="practice-metric"><small>RECENT MISTAKES</small><strong>${summary.recent_mistakes?.length || 0}</strong></div></div><div class="practice-insights-grid"><section class="panel"><div class="panel-head"><div><h3>Topics to strengthen</h3><p>Based on latest attempts.</p></div></div><div class="panel-body practice-weak-list">${summary.weak_topics?.length ? summary.weak_topics.map(topic=>`<div class="practice-weak-item"><span><b>${escapeHTML(topic.topic_name)}</b><small>${topic.attempted} attempted · ${topic.correct} correct</small></span><strong>${topic.accuracy_percent}%</strong></div>`).join('') : '<p class="muted">No topic-level results yet.</p>'}</div></section><section class="panel"><div class="panel-head"><div><h3>What to do next</h3><p>Use your results to guide the next session.</p></div></div><div class="panel-body"><p class="practice-next-tip">Revisit any topic below 70% accuracy, read its study notes, and try a fresh practice set. A score is a diagnostic signal—not a guaranteed GATE rank.</p><button class="btn btn-secondary" data-action="practice-return">Choose another practice set</button></div></section></div>`;
  setIcons(host);
}


// ------------------------- Stage 9: mock tests -------------------------
function clearMockTimer() {
  if (state.mockTimerHandle) window.clearInterval(state.mockTimerHandle);
  state.mockTimerHandle = null;
}

function formatMockClock(seconds) {
  const safe = Math.max(0, Number(seconds) || 0);
  const hours = Math.floor(safe / 3600);
  const minutes = Math.floor((safe % 3600) / 60);
  const secs = safe % 60;
  return hours > 0
    ? `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
    : `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function mockQuestionGroupLabel(group) {
  if (group === 'GENERAL_APTITUDE') return 'General Aptitude';
  if (group === 'ENGINEERING_MATHEMATICS') return 'Engineering Mathematics';
  return 'Subject questions';
}

async function renderMockTests() {
  const host = document.getElementById('page-content');
  const savedId = state.mockSession?.id || sessionStorage.getItem('gatepath-mock-session');
  if (savedId) {
    try {
      const session = await api(`/mock-tests/sessions/${encodeURIComponent(savedId)}`);
      if (session.status === 'active') {
        state.mockSession = session;
        const savedIndex = Number(sessionStorage.getItem(`gatepath-mock-index:${session.id}`) || 0);
        state.mockCurrentIndex = Number.isFinite(savedIndex) ? Math.max(0, Math.min(savedIndex, session.questions.length - 1)) : 0;
        renderMockSession();
        return;
      }
      sessionStorage.removeItem('gatepath-mock-session');
      sessionStorage.removeItem(`gatepath-mock-index:${savedId}`);
      state.mockSession = null;
      state.mockResult = session.result || null;
      if (state.mockResult) {
        renderMockResult();
        return;
      }
    } catch (_) {
      sessionStorage.removeItem('gatepath-mock-session');
      sessionStorage.removeItem(`gatepath-mock-index:${savedId}`);
      state.mockSession = null;
    }
  }
  if (state.mockResult) {
    renderMockResult();
    return;
  }
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Preparing your mock-test centre...</span></div>';
  try {
    const code = state.profile.paper_code;
    const catalog = await api(`/mock-tests/catalog?paper_code=${encodeURIComponent(code)}`);
    state.mockCatalog = catalog;
    const pattern = catalog.pattern?.common || {};
    const tests = catalog.tests || [];
    const available = tests.filter(test => test.available);
    const testCards = tests.map(test => `
      <article class="mock-test-card">
        <div class="mock-test-card-top"><span class="mock-test-pill">FULL LENGTH · ${escapeHTML(code)}</span><span class="status-pill ${test.available ? 'is-ready' : 'is-pending'}">${test.available ? 'Ready to start' : 'Content pending'}</span></div>
        <h2>${escapeHTML(test.title)}</h2><p>${escapeHTML(test.subtitle || 'Full computer-based mock examination')}</p>
        <div class="mock-test-stats"><span><b>${test.question_count}</b><small>Questions</small></span><span><b>${test.duration_minutes} min</b><small>Duration</small></span><span><b>${test.total_marks}</b><small>Total marks</small></span></div>
        <div class="mock-test-section-summary">${(test.section_summary || []).map(section => `<span><b>${escapeHTML(section.name)}</b><small>${section.question_count} questions · ${section.marks} marks</small></span>`).join('')}</div>
        <div class="notice mock-content-note"><span class="notice-icon">ⓘ</span><div><strong>Original GATEPath mock content</strong><p>${escapeHTML(test.content_origin || '')} ${escapeHTML(test.editorial_status || '')}</p></div></div>
        <button class="btn btn-primary" data-action="mock-start" data-test-id="${escapeHTML(test.test_id)}" ${test.available ? '' : 'disabled'}>${test.available ? 'Start full mock test ' + icon('arrow', 13) : 'Not available yet'}</button>
      </article>`).join('');
    const recent = catalog.recent_attempts || [];
    host.innerHTML = `
      <div class="page-heading"><div><span class="eyebrow">STAGE 9 · EXAM-DAY SIMULATION</span><h1>Full mock tests</h1><p>Practise in a timed computer-based test environment with saved responses, review flags and a detailed scorecard.</p></div><a class="btn btn-secondary" href="${escapeHTML(catalog.official_pattern_url || 'https://gate2027.iitm.ac.in/question_paper_pattern')}" target="_blank" rel="noreferrer">Official GATE 2027 pattern ↗</a></div>
      <div class="mock-pattern-strip"><div><small>QUESTIONS</small><strong>${pattern.total_questions || 65}</strong></div><div><small>DURATION</small><strong>${pattern.duration_minutes || 180} min</strong></div><div><small>TOTAL MARKS</small><strong>${pattern.total_marks || 100}</strong></div><div><small>GENERAL APTITUDE</small><strong>${pattern.general_aptitude?.marks || 15} marks</strong></div></div>
      <div class="notice mock-official-note"><span class="notice-icon">ⓘ</span><div><strong>Pattern and content are different things.</strong><p>The timer, navigation and marking rules follow the official GATE 2027 pattern. The available CS question set is original GATEPath pilot content, not an official paper or prediction, and requires academic review before high-stakes use.</p></div></div>
      <section class="mock-test-list"><div class="section-heading-inline"><div><h2>Available examinations</h2><p>${available.length} full-length mock${available.length === 1 ? '' : 's'} available for ${escapeHTML(code)}</p></div><span class="status-pill">${escapeHTML(catalog.paper_name)}</span></div>
      ${testCards || `<section class="syllabus-empty"><h3>Full mock content is not imported for ${escapeHTML(code)} yet</h3><p>The official pattern is available, but GATEPath will only enable a full mock when a complete, validated paper manifest is present. We will not fill missing question slots with duplicates or fabricated PYQs.</p><a class="btn btn-primary" href="${escapeHTML(catalog.official_pattern_url || 'https://gate2027.iitm.ac.in/question_paper_pattern')}" target="_blank" rel="noreferrer">Read official paper pattern ↗</a></section>`}
      </section>
      <section class="panel mock-history-panel"><div class="panel-head"><div><h3>Recent mock attempts</h3><p>Your submitted papers and saved results.</p></div></div><div class="panel-body">${recent.length ? `<div class="mock-history-list">${recent.map(item => `<div class="mock-history-row"><span><b>${escapeHTML(item.test_id)}</b><small>${escapeHTML(item.status)} · ${escapeHTML(item.created_at || '')}</small></span><strong>${Number(item.score || 0).toFixed(2)} / ${Number(item.maximum_marks || 0).toFixed(0)}</strong><button class="btn btn-secondary btn-small" data-action="mock-open-result" data-session-id="${escapeHTML(item.id)}">View report</button></div>`).join('')}</div>` : '<div class="empty-state"><strong>No completed mock attempts yet</strong><p>Your first result will appear here after you submit a full mock.</p></div>'}</div></section>
      <p class="practice-content-footnote">GATE 2027 pattern source: IIT Madras official website. Mock-test questions are independently authored and must not be mistaken for official GATE questions.</p>`;
    setIcons(host);
  } catch (error) {
    host.innerHTML = `<section class="panel content-placeholder"><div><h2>Mock-test centre could not load</h2><p>${escapeHTML(error.message)}</p></div></section>`;
  }
}

async function startMockTest(testId) {
  try {
    const session = await api('/mock-tests/sessions', {
      method: 'POST', body: JSON.stringify({ paper_code: state.profile.paper_code, test_id: testId }),
    });
    state.mockSession = session;
    state.mockResult = null;
    state.mockCurrentIndex = 0;
    state.mockQuestionOpenedAt = Date.now();
    sessionStorage.setItem('gatepath-mock-session', session.id);
    sessionStorage.setItem(`gatepath-mock-index:${session.id}`, '0');
    renderMockSession();
    toast('Mock test started. Your 180-minute timer is running.');
  } catch (error) { toast(error.message); }
}

function mockAnswerFromForm(question) {
  const form = document.getElementById('mock-answer-form');
  if (!form) return question.response?.answer || '';
  if (question.question_type === 'MCQ') return form.querySelector('input[name="mock-answer"]:checked')?.value || '';
  if (question.question_type === 'MSQ') return [...form.querySelectorAll('input[name="mock-answer"]:checked')].map(input => input.value).join(',');
  return form.querySelector('#mock-nat-answer')?.value.trim() || '';
}

async function saveMockCurrentResponse(extra = {}) {
  const session = state.mockSession;
  const question = session?.questions?.[state.mockCurrentIndex];
  if (!session || !question || session.status !== 'active') return false;
  if (state.mockAutoSaveTimer) { window.clearTimeout(state.mockAutoSaveTimer); state.mockAutoSaveTimer = null; }
  const answer = Object.prototype.hasOwnProperty.call(extra, 'answer') ? extra.answer : mockAnswerFromForm(question);
  const spent = Math.max(0, Math.floor((Date.now() - state.mockQuestionOpenedAt) / 1000));
  const payload = { answer, visited: true, spent_seconds: spent };
  if (Object.prototype.hasOwnProperty.call(extra, 'marked_for_review')) payload.marked_for_review = extra.marked_for_review;
  try {
    const saved = await api(`/mock-tests/sessions/${encodeURIComponent(session.id)}/responses/${encodeURIComponent(question.id)}`, {
      method: 'PATCH', body: JSON.stringify(payload),
    });
    question.response = saved.response;
    state.mockQuestionOpenedAt = Date.now();
    refreshMockPaletteUI();
    return true;
  } catch (error) {
    if (error.message.toLowerCase().includes('expired')) {
      await submitMockTest(true, false);
      return false;
    }
    toast(`Answer could not be saved: ${error.message}`);
    return false;
  }
}

function refreshMockPaletteUI() {
  const session = state.mockSession;
  if (!session) return;
  const answered = session.questions.filter(item => Boolean(item.response?.answer)).length;
  const marked = session.questions.filter(item => item.response?.marked_for_review).length;
  session.questions.forEach((item, index) => {
    const button = document.querySelector(`.mock-palette-button[data-index="${index}"]`);
    if (button) {
      button.classList.toggle('is-answered', Boolean(item.response?.answer));
      button.classList.toggle('is-marked', Boolean(item.response?.marked_for_review));
    }
  });
  const labels = document.querySelectorAll('.mock-exam-progress>div:first-child>span');
  if (labels[0]) labels[0].textContent = `${answered} answered`;
  if (labels[1]) labels[1].textContent = `${marked} marked for review`;
  if (labels[2]) labels[2].textContent = `${session.questions.length - answered} unanswered`;
  const progress = document.querySelector('.mock-exam-progress .practice-progress-track span');
  if (progress) progress.style.width = `${answered / session.questions.length * 100}%`;
  const stats = document.querySelectorAll('.mock-palette-stats b');
  if (stats[0]) stats[0].textContent = answered;
  if (stats[1]) stats[1].textContent = marked;
  if (stats[2]) stats[2].textContent = session.questions.length - answered;
}

function scheduleMockAutosave() {
  if (state.mockAutoSaveTimer) window.clearTimeout(state.mockAutoSaveTimer);
  state.mockAutoSaveTimer = window.setTimeout(() => {
    state.mockAutoSaveTimer = null;
    saveMockCurrentResponse();
  }, 450);
}

async function navigateMockQuestion(index) {
  if (!state.mockSession || index < 0 || index >= state.mockSession.questions.length) return;
  const saved = await saveMockCurrentResponse();
  if (!saved || !state.mockSession) return;
  state.mockCurrentIndex = index;
  sessionStorage.setItem(`gatepath-mock-index:${state.mockSession.id}`, String(index));
  renderMockSession();
}

function mockAnswerControl(question) {
  const answer = question.response?.answer || '';
  const selected = question.question_type === 'MSQ' ? answer.split(/[;,]/).filter(Boolean) : [answer];
  if (question.question_type === 'MCQ') {
    return `<div class="practice-answer-options mock-answer-list">${(question.options || []).map(option => `<label><input type="radio" name="mock-answer" value="${escapeHTML(option.key)}" ${selected.includes(option.key) ? 'checked' : ''}/><span><b>${escapeHTML(option.key)}</b>${escapeHTML(option.text)}</span></label>`).join('')}</div>`;
  }
  if (question.question_type === 'MSQ') {
    return `<div class="practice-answer-options mock-answer-list">${(question.options || []).map(option => `<label><input type="checkbox" name="mock-answer" value="${escapeHTML(option.key)}" ${selected.includes(option.key) ? 'checked' : ''}/><span><b>${escapeHTML(option.key)}</b>${escapeHTML(option.text)}</span></label>`).join('')}</div><small class="practice-answer-hint">Select every option you believe is correct. There is no partial marking for MSQ.</small>`;
  }
  return `<label class="practice-nat-field"><span>Enter your numerical answer</span><input class="form-control" id="mock-nat-answer" type="number" step="any" value="${escapeHTML(answer)}" placeholder="Enter a number" autocomplete="off"/></label>`;
}

function renderMockSession() {
  clearMockTimer();
  const host = document.getElementById('page-content');
  const session = state.mockSession;
  if (!session || !session.questions?.length) { renderMockTests(); return; }
  if (session.status !== 'active') {
    state.mockResult = session.result;
    renderMockResult();
    return;
  }
  state.mockCurrentIndex = Math.max(0, Math.min(state.mockCurrentIndex, session.questions.length - 1));
  const index = state.mockCurrentIndex;
  const question = session.questions[index];
  const response = question.response || { answer: '', marked_for_review: false, visited: false };
  const answered = Boolean(response.answer);
  const questions = session.questions;
  const answeredCount = questions.filter(item => Boolean(item.response?.answer)).length;
  const markedCount = questions.filter(item => item.response?.marked_for_review).length;
  const palette = questions.map((item, i) => `<button class="mock-palette-button ${i === index ? 'is-current' : ''} ${item.response?.answer ? 'is-answered' : ''} ${item.response?.marked_for_review ? 'is-marked' : ''}" data-action="mock-go-question" data-index="${i}" aria-label="Question ${i + 1}${item.response?.answer ? ', answered' : ''}${item.response?.marked_for_review ? ', marked for review' : ''}">${i + 1}</button>`).join('');
  const sectionSummary = ['GENERAL_APTITUDE', 'ENGINEERING_MATHEMATICS', 'SUBJECT'].map(group => {
    const subset = questions.filter(item => item.section_group === group);
    return `<span class="mock-section-counter ${question.section_group === group ? 'is-active' : ''}"><b>${subset.filter(item => item.response?.answer).length}/${subset.length}</b><small>${escapeHTML(mockQuestionGroupLabel(group))}</small></span>`;
  }).join('');
  const controls = question.question_type === 'MCQ' ? 'Select one option' : question.question_type === 'MSQ' ? 'Select one or more options' : 'Enter a numerical value';
  host.innerHTML = `
    <div class="mock-session-top"><div><span class="eyebrow">GATE-STYLE COMPUTER BASED TEST · ${escapeHTML(session.paper_code)}</span><h1>${escapeHTML(session.title || 'Full-length mock test')}</h1><p>Question ${index + 1} of ${questions.length} · ${escapeHTML(mockQuestionGroupLabel(question.section_group))}</p></div><div class="mock-timer-card"><small>TIME REMAINING</small><strong id="mock-countdown">${formatMockClock(session.remaining_seconds)}</strong><span>Auto-submits at zero</span></div></div>
    <div class="mock-exam-progress"><div><span>${answeredCount} answered</span><span>${markedCount} marked for review</span><span>${questions.length - answeredCount} unanswered</span></div><div class="practice-progress-track"><span style="width:${answeredCount / questions.length * 100}%"></span></div></div>
    <div class="mock-section-counters">${sectionSummary}</div>
    <div class="mock-player-layout"><section class="panel mock-player-panel"><div class="mock-question-head"><div><span class="mock-question-number">QUESTION ${index + 1}</span><h2>${escapeHTML(question.section_name || question.topic_name || 'Question')}</h2><small>${escapeHTML(question.topic_name || mockQuestionGroupLabel(question.section_group))}</small></div><div class="mock-question-tags"><span>${escapeHTML(question.question_type)}</span><span>${question.marks} mark${question.marks === 1 ? '' : 's'}</span></div></div>
      <div class="mock-question-prompt">${escapeHTML(question.prompt)}</div>
      <form id="mock-answer-form"><div class="practice-answer-label">${controls}</div>${mockAnswerControl(question)}</form>
      <div class="mock-action-row"><button class="btn btn-secondary btn-small" data-action="mock-clear-answer">Clear response</button><div><button class="btn btn-secondary btn-small" data-action="mock-mark-review">${response.marked_for_review ? 'Unmark review' : 'Mark for review'}</button><button class="btn btn-primary btn-small" data-action="mock-save-next">Save &amp; Next ${icon('arrow',12)}</button></div></div>
      <div class="practice-player-nav"><button class="btn btn-secondary" data-action="mock-previous" ${index === 0 ? 'disabled' : ''}>← Previous</button><button class="btn btn-secondary" data-action="mock-next" ${index === questions.length - 1 ? 'disabled' : ''}>Next question →</button></div>
      <small class="mock-save-hint" id="mock-save-hint">Responses save automatically when you change an answer and when you navigate.</small>
    </section><aside class="panel mock-palette-panel"><div class="panel-head"><div><h3>Question palette</h3><p>Jump to any question</p></div></div><div class="mock-palette-grid">${palette}</div><div class="mock-palette-legend"><span><i class="answered"></i> Answered</span><span><i class="marked"></i> Review</span><span><i class="current"></i> Current</span><span><i class="unanswered"></i> Unanswered</span></div><div class="mock-palette-stats"><div><b>${answeredCount}</b><small>Answered</small></div><div><b>${markedCount}</b><small>Review flags</small></div><div><b>${questions.length - answeredCount}</b><small>Unanswered</small></div></div><button class="btn btn-primary mock-submit-button" data-action="mock-submit">Submit examination</button><small class="mock-submit-note">Unanswered questions receive zero. Incorrect MCQs have one-third or two-thirds negative marking as applicable.</small></aside></div>`;
  setIcons(host);
  const form = document.getElementById('mock-answer-form');
  form?.addEventListener('change', scheduleMockAutosave);
  form?.addEventListener('input', (event) => { if (event.target?.id === 'mock-nat-answer') scheduleMockAutosave(); });
  if (!response.visited) {
    response.visited = true;
    api(`/mock-tests/sessions/${encodeURIComponent(session.id)}/responses/${encodeURIComponent(question.id)}`, { method: 'PATCH', body: JSON.stringify({ visited: true }) })
      .then(saved => { question.response = saved.response; }).catch(() => {});
  }
  state.mockQuestionOpenedAt = Date.now();
  startMockCountdown();
}

function startMockCountdown() {
  clearMockTimer();
  const session = state.mockSession;
  if (!session || session.status !== 'active') return;
  const tick = () => {
    const remaining = Math.max(0, Math.ceil(Number(session.expires_at) - Date.now() / 1000));
    const output = document.getElementById('mock-countdown');
    if (output) output.textContent = formatMockClock(remaining);
    output?.classList.toggle('is-urgent', remaining <= 300);
    if (remaining <= 0) {
      clearMockTimer();
      submitMockTest(true);
    }
  };
  tick();
  state.mockTimerHandle = window.setInterval(tick, 1000);
}

async function submitMockTest(autoSubmitted = false, saveCurrent = true) {
  if (!state.mockSession) return;
  if (state.mockAutoSaveTimer) { window.clearTimeout(state.mockAutoSaveTimer); state.mockAutoSaveTimer = null; }
  if (saveCurrent && state.mockSession.status === 'active') await saveMockCurrentResponse();
  const sessionId = state.mockSession?.id;
  if (!sessionId) return;
  try {
    const result = await api(`/mock-tests/sessions/${encodeURIComponent(sessionId)}/submit`, { method: 'POST', body: '{}' });
    clearMockTimer();
    sessionStorage.removeItem('gatepath-mock-session');
    sessionStorage.removeItem(`gatepath-mock-index:${sessionId}`);
    state.mockResult = result;
    state.mockSession = null;
    renderMockResult(autoSubmitted || result.status === 'expired');
  } catch (error) { toast(error.message); }
}

function renderMockResult(autoSubmitted = false) {
  clearMockTimer();
  const host = document.getElementById('page-content');
  const result = state.mockResult;
  if (!result) { renderMockTests(); return; }
  const score = Number(result.score || 0);
  const status = result.status === 'expired' ? 'Time expired · automatically submitted' : autoSubmitted ? 'Time is up · paper submitted' : 'Paper submitted';
  const sections = result.section_breakdown || [];
  const subjects = result.subject_breakdown || [];
  const questions = result.questions || [];
  const details = questions.map(question => {
    const res = question.result || {};
    const answer = res.submitted_answer || 'Not answered';
    const stateLabel = !res.submitted_answer ? 'Unattempted' : res.is_correct ? 'Correct' : 'Incorrect';
    return `<details class="mock-review-question"><summary><span>Q${question.question_number} · ${escapeHTML(question.topic_name || mockQuestionGroupLabel(question.section_group))}</span><b class="${!res.submitted_answer ? 'is-unanswered' : res.is_correct ? 'is-correct' : 'is-wrong'}">${stateLabel} · ${Number(res.awarded_marks || 0) >= 0 ? '+' : ''}${Number(res.awarded_marks || 0).toFixed(2)}</b></summary><div class="mock-review-body"><p>${escapeHTML(question.prompt)}</p><p><b>Your answer:</b> ${escapeHTML(answer)} · <b>Correct answer:</b> ${escapeHTML(res.correct_answer || '')}</p>${res.solution?.steps?.length ? `<section class="practice-solution"><h4>${escapeHTML(res.solution.title || 'Solution')}</h4><ol>${res.solution.steps.map(step => `<li>${escapeHTML(step)}</li>`).join('')}</ol><small>${escapeHTML(res.solution.note || '')}</small></section>` : ''}</div></details>`;
  }).join('');
  host.innerHTML = `
    <div class="page-heading"><div><span class="eyebrow">STAGE 9 · MOCK TEST REPORT</span><h1>${escapeHTML(result.test_id || 'Full mock result')}</h1><p>${status}. Review your responses, scoring and topic-wise performance.</p></div><button class="btn btn-primary" data-action="mock-return">Back to mock tests ${icon('arrow',13)}</button></div>
    <section class="mock-result-hero"><div><small>YOUR GATE-STYLE SCORE</small><strong>${score >= 0 ? '+' : ''}${score.toFixed(2)} <span>/ ${Number(result.maximum_marks || 100).toFixed(0)}</span></strong><p>${result.correct_count} correct · ${result.wrong_count} incorrect · ${result.unattempted_count} unanswered</p></div><div class="mock-result-ring"><strong>${Number(result.accuracy_percent || 0)}%</strong><small>Attempt accuracy</small></div></section>
    <div class="mock-result-metrics"><div><small>ATTEMPTED</small><b>${result.attempted_count}</b></div><div><small>UNATTEMPTED</small><b>${result.unattempted_count}</b></div><div><small>TIME USED</small><b>${formatMockClock(result.elapsed_seconds)}</b></div><div><small>SCORE / 100</small><b>${score.toFixed(2)}</b></div></div>
    <section class="panel mock-breakdown-panel"><div class="panel-head"><div><h3>Section-wise performance</h3><p>Marks awarded after GATE-style negative marking.</p></div></div><div class="panel-body"><div class="mock-breakdown-grid">${sections.map(item => `<div class="mock-breakdown-item"><small>${escapeHTML(mockQuestionGroupLabel(item.code))}</small><strong>${Number(item.score).toFixed(2)} <span>/ ${Number(item.maximum_marks).toFixed(0)}</span></strong><div class="practice-progress-track"><span style="width:${Math.max(0,Math.min(100,Number(item.score)/Math.max(1,Number(item.maximum_marks))*100))}%"></span></div><p>${item.correct} correct · ${item.wrong} wrong · ${item.unattempted} blank</p></div>`).join('')}</div></div></section>
    <section class="panel mock-breakdown-panel"><div class="panel-head"><div><h3>Subject-wise performance</h3><p>Use low-accuracy subjects to plan your next revision block.</p></div></div><div class="panel-body"><div class="mock-subject-list">${subjects.map(item => `<div class="mock-subject-row"><span><b>${escapeHTML(item.name)}</b><small>${item.correct}/${item.attempted} correct · ${item.unattempted} unattempted</small></span><strong>${Number(item.score).toFixed(2)} / ${Number(item.maximum_marks).toFixed(0)}</strong><em>${item.accuracy_percent}%</em></div>`).join('')}</div></div></section>
    <section class="panel mock-review-panel"><div class="panel-head"><div><h3>Question-by-question review</h3><p>Open any question to view your response, correct answer and worked solution.</p></div><span class="status-pill">${questions.length} questions</span></div><div class="panel-body mock-review-list">${details}</div></section>
    <div class="notice mock-content-note"><span class="notice-icon">ⓘ</span><div><strong>Interpretation</strong><p>This is a GATEPath original pilot mock. Its structure follows the published GATE 2027 CS pattern, but its questions are not official GATE questions and its score is not an AIR or GATE score prediction.</p></div></div>`;
  setIcons(host);
}

async function openMockResult(sessionId) {
  try {
    const session = await api(`/mock-tests/sessions/${encodeURIComponent(sessionId)}`);
    if (session.status === 'active') {
      state.mockSession = session;
      const savedIndex = Number(sessionStorage.getItem(`gatepath-mock-index:${session.id}`) || 0);
      state.mockCurrentIndex = Number.isFinite(savedIndex) ? Math.max(0, Math.min(savedIndex, session.questions.length - 1)) : 0;
      sessionStorage.setItem('gatepath-mock-session', session.id);
      renderMockSession();
    } else {
      state.mockResult = session.result;
      renderMockResult();
    }
  } catch (error) { toast(error.message); }
}

// ---------------- Stage 12: student analytics, community and admin UI ----------------

function analyticsMetric(label, value, note, symbol = 'chart') {
  return `<div class="metric-card"><span class="metric-icon teal">${icon(symbol,17)}</span><div class="metric-copy"><small>${escapeHTML(label)}</small><strong>${escapeHTML(value)}</strong><span>${escapeHTML(note)}</span></div></div>`;
}

async function renderAnalytics() {
  const host = document.getElementById('page-content');
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Building your performance report...</span></div>';
  try {
    state.analyticsData = await api(`/analytics?paper_code=${encodeURIComponent(state.profile.paper_code)}`);
    const data = state.analyticsData;
    const bars = (data.activity || []).map(item => {
      const minutes = Number(item.study_minutes || 0);
      const attempts = Number(item.practice_attempts || 0);
      const height = Math.max(5, Math.min(100, minutes / Math.max(30, ...data.activity.map(x => Number(x.study_minutes || 0))) * 100));
      return `<div class="analytics-day"><div class="analytics-bar-wrap"><span class="analytics-bar" style="height:${height}%" title="${minutes} study minutes · ${attempts} practice attempts"></span></div><small>${new Date(`${item.date}T00:00:00`).toLocaleDateString('en-IN',{weekday:'short'}).slice(0,2)}</small><b>${minutes ? `${Math.round(minutes/60*10)/10}h` : attempts ? `${attempts}Q` : '–'}</b></div>`;
    }).join('');
    const sections = (data.section_performance || []).map(item => `<div class="analytics-ranking-row"><div><b>${escapeHTML(item.name)}</b><small>${item.correct}/${item.attempted} latest answers correct</small></div><strong>${item.accuracy_percent}%</strong><div class="analytics-track"><span style="width:${Math.max(0,Math.min(100,item.accuracy_percent))}%"></span></div></div>`).join('') || '<div class="empty-state"><strong>No section data yet</strong><p>Attempt practice questions or PYQs to see subject-level accuracy.</p></div>';
    const weak = (data.weak_topics || []).map(item => `<div class="analytics-weak-row"><span><b>${escapeHTML(item.topic_name)}</b><small>${item.attempted} questions attempted</small></span><strong class="${item.accuracy_percent < 60 ? 'is-low' : ''}">${item.accuracy_percent}%</strong></div>`).join('') || '<div class="empty-state"><strong>No weak topics identified</strong><p>Keep practising. A topic appears here after it has recorded attempts.</p></div>';
    const mocks = (data.mock_tests?.history || []).slice(0,6).map(item => `<div class="analytics-history-row"><span><b>${escapeHTML(item.test_id)}</b><small>${escapeHTML(item.created_at || '')} · ${item.attempted_count} attempted</small></span><strong>${Number(item.score || 0).toFixed(2)} / ${Number(item.maximum_marks || 100).toFixed(0)}</strong></div>`).join('') || '<div class="empty-state"><strong>No completed mocks yet</strong><p>Your score trend will appear after your first full mock.</p></div>';
    host.innerHTML = `
      <div class="page-heading"><div><span class="eyebrow">STAGE 12 · LEARN FROM YOUR DATA</span><h1>Preparation analytics</h1><p>Track recorded study, topic completion, question accuracy and mock-test outcomes for ${escapeHTML(state.profile.paper_code)}.</p></div><button class="btn btn-secondary" data-action="analytics-refresh">${icon('repeat',13)} Refresh report</button></div>
      <div class="notice"><span class="notice-icon">ⓘ</span><div><strong>Recorded activity only</strong><p>${escapeHTML(data.notice || 'The report does not estimate unrecorded offline work or predict a GATE rank.')}</p></div></div>
      <section class="metrics-grid analytics-metrics">${analyticsMetric('Syllabus completion',`${data.syllabus.completion_percent}%`,`${data.syllabus.completed_topics}/${data.syllabus.total_topics} topics complete`,'book')}${analyticsMetric('Question accuracy',`${data.practice.accuracy_percent}%`,`${data.practice.unique_questions_attempted} unique questions · latest attempts`,'target')}${analyticsMetric('Mock tests completed',data.mock_tests.completed, data.mock_tests.average_score === null ? 'No completed mock scores yet' : `Average ${data.mock_tests.average_score}/100`,'timer')}${analyticsMetric('Current activity streak',`${data.current_study_streak_days} days`,`${data.active_days_last_14} active days in last 14`,'calendar')}</section>
      <div class="analytics-grid"><section class="panel"><div class="panel-head"><div><h3>14-day study activity</h3><p>Completed planner minutes and practice volume by day.</p></div><span class="status-pill">Last 14 days</span></div><div class="panel-body"><div class="analytics-chart">${bars}</div><div class="analytics-chart-legend"><span><i></i> Study time</span><small>Labels show hours or question count when no study minutes were recorded.</small></div></div></section>
      <section class="panel"><div class="panel-head"><div><h3>Topics to revisit</h3><p>Lowest accuracy among topics with recorded attempts.</p></div></div><div class="panel-body analytics-weak-list">${weak}</div></section></div>
      <div class="analytics-grid"><section class="panel"><div class="panel-head"><div><h3>Subject performance</h3><p>Latest recorded practice and PYQ answers, grouped by syllabus section.</p></div></div><div class="panel-body analytics-ranking">${sections}</div></section><section class="panel"><div class="panel-head"><div><h3>Mock-test history</h3><p>Recent submitted full-length mock attempts.</p></div></div><div class="panel-body analytics-history">${mocks}</div></section></div>
      <div class="notice analytics-note"><span class="notice-icon">✦</span><div><strong>Use analytics to plan, not to predict.</strong><p>Accuracy is based on the latest answer per question. Mock scores are GATEPath mock results, not official GATE scores or rank predictions.</p><button class="text-link" data-action="go-view" data-view="planner">Review your study plan →</button></div></div>`;
    setIcons(host);
  } catch (error) {
    host.innerHTML = `<section class="panel content-placeholder"><div><h2>Analytics could not load</h2><p>${escapeHTML(error.message)}</p><button class="btn btn-primary" data-action="analytics-refresh">Try again</button></div></section>`;
  }
}

async function loadCommunityFeed() {
  const params = new URLSearchParams({ paper_code: state.profile.paper_code, scope: state.communityScope || 'paper', category: state.communityCategory || '', q: state.communityQuery || '', page: '1', limit: '30' });
  state.communityFeed = await api(`/community/feed?${params.toString()}`);
  state.communitySelectedPost = null;
  renderCommunityContent();
}

function communityPostCard(item) {
  const dateText = item.created_at ? new Date(`${item.created_at.replace(' ','T')}Z`).toLocaleString('en-IN',{dateStyle:'medium',timeStyle:'short'}) : '';
  return `<article class="community-post-card"><div class="community-post-meta"><span class="community-avatar">${escapeHTML((item.author_name || 'S').slice(0,1).toUpperCase())}</span><span><b>${escapeHTML(item.author_name)}</b><small>${escapeHTML(item.paper_code)} · ${escapeHTML(item.category)} · ${escapeHTML(dateText)}</small></span>${item.pinned ? '<span class="status-pill community-pinned">Pinned</span>' : ''}</div><button class="community-post-title" data-action="community-open-post" data-post-id="${item.id}">${escapeHTML(item.title)}</button><p class="community-post-excerpt">${escapeHTML(item.body.length > 260 ? `${item.body.slice(0,260)}…` : item.body)}</p><div class="community-post-actions"><button data-action="community-like" data-post-id="${item.id}" class="community-action ${item.liked_by_me ? 'is-liked' : ''}">${icon('check',13)} ${item.like_count} helpful</button><button data-action="community-open-post" data-post-id="${item.id}" class="community-action">${icon('users',13)} ${item.reply_count} replies</button><button data-action="community-report" data-target-type="post" data-target-id="${item.id}" class="community-action">Report</button>${item.is_owner ? `<button data-action="community-delete-post" data-post-id="${item.id}" class="community-action is-danger">Delete</button>` : ''}</div></article>`;
}

async function renderCommunity() {
  state.communitySelectedPost = null;
  const host = document.getElementById('page-content');
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Opening the GATEPath community...</span></div>';
  try {
    const params = new URLSearchParams({ paper_code: state.profile.paper_code, scope: state.communityScope || 'paper', category: state.communityCategory || '', q: state.communityQuery || '', page: '1', limit: '30' });
    state.communityFeed = await api(`/community/feed?${params.toString()}`);
    renderCommunityContent();
  } catch (error) { host.innerHTML = `<section class="panel content-placeholder"><div><h2>Community could not load</h2><p>${escapeHTML(error.message)}</p></div></section>`; }
}

async function openCommunityPost(postId) {
  try {
    state.communitySelectedPost = await api(`/community/posts/${postId}`);
    renderCommunityContent();
  } catch (error) { toast(error.message); }
}

function renderCommunityContent() {
  const host = document.getElementById('page-content');
  if (!host || state.view !== 'community' || !state.communityFeed) return;
  if (state.communitySelectedPost) {
    const { post, replies } = state.communitySelectedPost;
    const dateText = post.created_at ? new Date(`${post.created_at.replace(' ','T')}Z`).toLocaleString('en-IN',{dateStyle:'medium',timeStyle:'short'}) : '';
    host.innerHTML = `<div class="page-heading"><div><span class="eyebrow">STAGE 12 · COMMUNITY DISCUSSION</span><h1>${escapeHTML(post.title)}</h1><p>${escapeHTML(post.paper_code)} · ${escapeHTML(post.category)} · ${escapeHTML(post.author_name)} · ${escapeHTML(dateText)}</p></div><button class="btn btn-secondary" data-action="community-back">← Back to discussions</button></div><section class="panel community-detail-card"><div class="panel-body"><p class="community-detail-body">${escapeHTML(post.body)}</p><div class="community-post-actions"><button class="community-action ${post.liked_by_me ? 'is-liked' : ''}" data-action="community-like" data-post-id="${post.id}">${icon('check',13)} ${post.like_count} helpful</button><button class="community-action" data-action="community-report" data-target-type="post" data-target-id="${post.id}">Report discussion</button>${post.is_owner ? `<button class="community-action is-danger" data-action="community-delete-post" data-post-id="${post.id}">Delete discussion</button>` : ''}</div></div></section><section class="panel"><div class="panel-head"><div><h3>Replies</h3><p>${replies.length} responses · keep advice respectful and evidence-based.</p></div></div><div class="panel-body community-replies">${replies.length ? replies.map(reply => `<article class="community-reply"><div class="community-post-meta"><span class="community-avatar">${escapeHTML((reply.author_name || 'S').slice(0,1).toUpperCase())}</span><span><b>${escapeHTML(reply.author_name)}</b><small>${escapeHTML(reply.created_at)}</small></span></div><p>${escapeHTML(reply.body)}</p>${reply.is_owner || post.can_moderate ? `<button class="community-action is-danger" data-action="community-delete-reply" data-reply-id="${reply.id}">Remove reply</button>` : `<button class="community-action" data-action="community-report" data-target-type="reply" data-target-id="${reply.id}">Report</button>`}</article>`).join('') : '<div class="empty-state"><strong>No replies yet</strong><p>Share a useful explanation or ask a follow-up question.</p></div>'}</div></section><section class="panel"><div class="panel-head"><div><h3>Add a reply</h3><p>Do not share personal contact details or copyrighted material.</p></div></div><div class="panel-body"><form id="community-reply-form" class="community-form"><textarea name="body" rows="4" minlength="2" maxlength="2000" placeholder="Write a helpful reply..." required></textarea><div class="community-form-footer"><small>2–2,000 characters</small><button class="btn btn-primary" type="submit">Post reply ${icon('arrow',13)}</button></div></form></div></section>`;
    setIcons(host);
    document.getElementById('community-reply-form')?.addEventListener('submit', submitCommunityReply);
    return;
  }
  const items = state.communityFeed.items || [];
  host.innerHTML = `<div class="page-heading"><div><span class="eyebrow">STAGE 12 · STUDY TOGETHER</span><h1>GATEPath community</h1><p>Discuss concepts, ask doubts and share preparation strategies with other aspirants.</p></div><span class="status-pill">${state.profile.paper_code} community</span></div><div class="community-layout"><section class="panel community-compose-panel"><div class="panel-head"><div><h3>Start a discussion</h3><p>Keep questions specific so peers can help.</p></div></div><div class="panel-body"><form id="community-post-form" class="community-form"><div class="community-form-grid"><label>Paper<select name="paper_code">${paperOptions(state.profile.paper_code)}</select></label><label>Category<select name="category"><option>Doubt</option><option>Study tips</option><option>Resources</option><option>Exam strategy</option><option>General</option></select></label></div><label>Title<input name="title" minlength="8" maxlength="120" placeholder="e.g. Why does deadlock avoidance use safe states?" required></label><label>Details<textarea name="body" rows="3" minlength="20" maxlength="5000" placeholder="Include the concept, what you tried and where you got stuck..." required></textarea></label><div class="community-form-footer"><small>Be respectful · Avoid personal information · Cite external resources</small><button class="btn btn-primary" type="submit">Publish discussion ${icon('arrow',13)}</button></div></form></div></section><section class="community-feed-column"><div class="community-feed-toolbar"><div><h3>Discussions</h3><p>${state.communityFeed.total} discussions found</p></div><div class="community-filter-row"><select id="community-scope-filter"><option value="paper" ${state.communityScope !== 'all' && state.communityScope !== 'mine' ? 'selected' : ''}>My paper</option><option value="all" ${state.communityScope === 'all' ? 'selected' : ''}>All papers</option><option value="mine" ${state.communityScope === 'mine' ? 'selected' : ''}>My posts</option></select><select id="community-category-filter"><option value="">All categories</option>${['Doubt','Study tips','Resources','Exam strategy','General'].map(value => `<option ${state.communityCategory === value ? 'selected' : ''}>${value}</option>`).join('')}</select></div></div><label class="community-search">${icon('search',14)}<input id="community-search" type="search" value="${escapeHTML(state.communityQuery || '')}" placeholder="Search discussions and doubts"></label><div class="community-post-list">${items.length ? items.map(communityPostCard).join('') : '<div class="empty-state"><strong>No discussions match yet</strong><p>Start a discussion or change the filters.</p></div>'}</div></section></div><div class="notice community-guidelines"><span class="notice-icon">ⓘ</span><div><strong>Community guidelines</strong><p>Share original explanations, respect other learners, avoid spam, and report harmful or misleading content. Discussions may be hidden while moderators review reports.</p></div></div>`;
  setIcons(host);
  document.getElementById('community-post-form')?.addEventListener('submit', submitCommunityPost);
  document.getElementById('community-scope-filter')?.addEventListener('change', async event => { state.communityScope = event.target.value; await renderCommunity(); });
  document.getElementById('community-category-filter')?.addEventListener('change', async event => { state.communityCategory = event.target.value; await renderCommunity(); });
  let timer;
  document.getElementById('community-search')?.addEventListener('input', event => {
    clearTimeout(timer); state.communityQuery = event.target.value;
    const caret = event.target.selectionStart;
    timer = setTimeout(async () => { await renderCommunity(); const replacement=document.getElementById('community-search'); replacement?.focus(); if (replacement && caret !== null) replacement.setSelectionRange(caret,caret); }, 260);
  });
}

async function submitCommunityPost(event) {
  event.preventDefault(); const form = new FormData(event.currentTarget);
  try {
    const result = await api('/community/posts', { method:'POST', body:JSON.stringify({paper_code:form.get('paper_code'),category:form.get('category'),title:form.get('title'),body:form.get('body')}) });
    state.communityScope = 'paper'; state.communityCategory = ''; state.communityQuery = '';
    await openCommunityPost(result.id); toast('Your discussion has been published.');
  } catch (error) { toast(error.message); }
}

async function submitCommunityReply(event) {
  event.preventDefault(); if (!state.communitySelectedPost) return;
  const form = new FormData(event.currentTarget);
  try {
    await api(`/community/posts/${state.communitySelectedPost.post.id}/replies`, {method:'POST',body:JSON.stringify({body:form.get('body')})});
    await openCommunityPost(state.communitySelectedPost.post.id); toast('Reply posted.');
  } catch (error) { toast(error.message); }
}

function openCommunityReportForm(type, id) {
  openModal('Report community content', 'COMMUNITY SAFETY', `<form id="community-report-form"><input type="hidden" name="target_type" value="${escapeHTML(type)}"><input type="hidden" name="target_id" value="${Number(id)}"><label>Why are you reporting this?<textarea class="form-control" name="reason" rows="4" minlength="5" maxlength="500" placeholder="Explain the concern for moderators..." required></textarea></label><div class="modal-actions"><button class="btn btn-secondary" type="button" data-action="close-modal">Cancel</button><button class="btn btn-primary" type="submit">Submit report</button></div></form>`);
  document.getElementById('community-report-form')?.addEventListener('submit', async event => { event.preventDefault(); const form = new FormData(event.currentTarget); try { await api('/community/reports',{method:'POST',body:JSON.stringify({target_type:form.get('target_type'),target_id:Number(form.get('target_id')),reason:form.get('reason')})}); closeModal(); toast('Report sent to moderators.'); } catch (error) { toast(error.message); } });
}

async function renderAdmin() {
  const host = document.getElementById('page-content');
  if (state.user?.role !== 'admin') { host.innerHTML = '<section class="panel content-placeholder"><div><h2>Administrator access required</h2><p>This workspace is available only to authorised administrators.</p></div></section>'; return; }
  host.innerHTML = '<div class="loading-state"><div class="loader"></div><span>Loading administration workspace...</span></div>';
  try {
    const [overview, users, reports, catalog, queue] = await Promise.all([
      api('/admin/overview'), api('/admin/users?limit=30'), api('/admin/reports?status=pending&limit=30'),
      api('/admin/content/catalog'), api(`/admin/content/review-queue?paper_code=${encodeURIComponent(state.adminPaperCode || 'CS')}&content_type=${encodeURIComponent(state.adminContentType || 'all')}&limit=300`),
    ]);
    state.adminOverview=overview; state.adminUsers=users; state.adminReports=reports.items || []; state.adminCatalog=catalog.items || []; state.adminQueue=queue;
    renderAdminContent();
  } catch (error) { host.innerHTML=`<section class="panel content-placeholder"><div><h2>Admin workspace could not load</h2><p>${escapeHTML(error.message)}</p></div></section>`; }
}

function renderAdminContent() {
  const host=document.getElementById('page-content'); if (!host || state.view!=='admin' || !state.adminOverview) return;
  const o=state.adminOverview;
  const userRows=adminUserTableRows(state.adminUsers?.items || []);
  const reports=(state.adminReports || []).map(item=>`<article class="admin-report-card"><div><span class="status-pill">${escapeHTML(item.target_type)} · #${item.target_id}</span><h4>${escapeHTML(item.target_excerpt || 'Content unavailable')}</h4><p>${escapeHTML(item.reason)}</p><small>Reported by ${escapeHTML(item.reporter_name)} · ${escapeHTML(item.created_at)}</small></div><div class="admin-report-actions"><button class="btn btn-small btn-secondary" data-action="admin-report-action" data-report-id="${item.id}" data-resolution="dismissed" data-moderation="none">Dismiss</button><button class="btn btn-small btn-secondary" data-action="admin-report-action" data-report-id="${item.id}" data-resolution="resolved" data-moderation="hide">Hide</button><button class="btn btn-small btn-danger" data-action="admin-report-action" data-report-id="${item.id}" data-resolution="resolved" data-moderation="remove">Remove</button></div></article>`).join('');
  const queueItems=(state.adminQueue?.items || []).slice(0,30).map(item=>`<div class="admin-review-row"><div><b>${escapeHTML(item.title.length>110?`${item.title.slice(0,110)}…`:item.title)}</b><small>${escapeHTML(item.paper_code)} · ${escapeHTML(item.content_type)} · ${escapeHTML(item.content_id)} · ${escapeHTML(item.source_status)}</small></div><select data-admin-review-status data-paper-code="${escapeHTML(item.paper_code)}" data-content-type="${escapeHTML(item.content_type)}" data-content-id="${escapeHTML(item.content_id)}"><option value="pending_review" ${item.review_status==='pending_review'?'selected':''}>Pending review</option><option value="approved" ${item.review_status==='approved'?'selected':''}>Approved</option><option value="needs_changes" ${item.review_status==='needs_changes'?'selected':''}>Needs changes</option><option value="rejected" ${item.review_status==='rejected'?'selected':''}>Rejected</option></select></div>`).join('');
  const catalog=(state.adminCatalog||[]).map(item=>`<tr><td><b>${escapeHTML(item.paper_code)}</b><small>${escapeHTML(item.paper_name)}</small></td><td>${item.syllabus_topics}</td><td>${item.study_notes}</td><td>${item.practice_questions}</td><td>${item.pyq_records}</td></tr>`).join('');
  host.innerHTML=`<div class="page-heading"><div><span class="eyebrow">STAGE 12 · PLATFORM OPERATIONS</span><h1>Administration</h1><p>Monitor the learning platform, manage student access, moderate discussions and review learning content.</p></div><button class="btn btn-secondary" data-action="admin-refresh">${icon('repeat',13)} Refresh</button></div>
  <section class="metrics-grid admin-metrics">${analyticsMetric('Registered users',o.users,'All accounts','users')}${analyticsMetric('Active students',o.active_students,`${o.students} student accounts`,'graduation')}${analyticsMetric('Pending reports',o.pending_reports,'Community moderation queue','flag')}${analyticsMetric('Content approved',o.approved_content_items,`${o.pending_content_reviews} explicitly pending review`,'check')}</section>
  <div class="admin-grid"><section class="panel"><div class="panel-head"><div><h3>Student accounts</h3><p>Deactivate access to revoke active sessions.</p></div><span class="status-pill" id="admin-user-count">Showing ${state.adminUsers.items.length} of ${state.adminUsers.total}</span></div><div class="panel-body"><label class="community-search">${icon('search',14)}<input id="admin-user-search" type="search" value="${escapeHTML(state.adminUserQuery || '')}" placeholder="Search name or email"></label><div class="table-scroll"><table class="admin-table"><thead><tr><th>Student</th><th>Role</th><th>Status</th><th>Access</th></tr></thead><tbody id="admin-user-table-body">${userRows||'<tr><td colspan="4">No accounts found.</td></tr>'}</tbody></table></div></div></section>
  <section class="panel"><div class="panel-head"><div><h3>Community moderation</h3><p>Review reports and take a proportionate action.</p></div><span class="status-pill">${state.adminReports.length} pending</span></div><div class="panel-body admin-report-list">${reports||'<div class="empty-state"><strong>No pending reports</strong><p>The moderation queue is clear.</p></div>'}</div></section></div>
  <section class="panel admin-content-panel"><div class="panel-head"><div><h3>Content review queue</h3><p>Review editorial notes and question-bank records. Review status is not an automatic accuracy certification.</p></div><div class="admin-filter-group"><label class="admin-paper-select">Paper<select id="admin-paper-select">${paperOptions(state.adminPaperCode||'CS')}</select></label><label class="admin-paper-select">Type<select id="admin-content-type-select"><option value="all" ${state.adminContentType==='all'?'selected':''}>All content</option><option value="material" ${state.adminContentType==='material'?'selected':''}>Study notes</option><option value="practice_question" ${state.adminContentType==='practice_question'?'selected':''}>Practice questions</option><option value="pyq_answer" ${state.adminContentType==='pyq_answer'?'selected':''}>PYQ answer keys</option></select></label></div></div><div class="panel-body"><div class="admin-review-list">${queueItems||'<div class="empty-state"><strong>No imported content found</strong><p>This paper needs a verified topic and content import.</p></div>'}</div><small class="muted-copy">Showing ${Math.min(30,state.adminQueue?.items?.length||0)} of ${state.adminQueue?.total_available||0} available content records. Review status is saved per record.</small></div></section>
  <section class="panel admin-content-panel"><div class="panel-head"><div><h3>Paper content catalogue</h3><p>Coverage across all configured GATE papers.</p></div></div><div class="panel-body table-scroll"><table class="admin-table"><thead><tr><th>Paper</th><th>Syllabus topics</th><th>Notes</th><th>Practice</th><th>PYQ keys</th></tr></thead><tbody>${catalog}</tbody></table></div></section>`;
  setIcons(host);
  document.getElementById('admin-paper-select')?.addEventListener('change',async e=>{state.adminPaperCode=e.target.value;await renderAdmin();});
  document.getElementById('admin-content-type-select')?.addEventListener('change',async e=>{state.adminContentType=e.target.value;await renderAdmin();});
  let searchTimer; document.getElementById('admin-user-search')?.addEventListener('input',e=>{clearTimeout(searchTimer);state.adminUserQuery=e.target.value;searchTimer=setTimeout(()=>loadAdminUsers(state.adminUserQuery),250);});
  host.querySelectorAll('[data-admin-review-status]').forEach(select=>select.addEventListener('change',async e=>{const el=e.target;try{await api(`/admin/content/reviews/${encodeURIComponent(el.dataset.contentType)}/${encodeURIComponent(el.dataset.contentId)}?paper_code=${encodeURIComponent(el.dataset.paperCode)}`,{method:'PUT',body:JSON.stringify({status:el.value,note:''})});toast('Content review status saved.');}catch(error){toast(error.message);}}));
}

function adminUserTableRows(items) {
  return items.map(item=>`<tr><td><b>${escapeHTML(item.full_name)}</b><small>${escapeHTML(item.email)}</small></td><td>${escapeHTML(item.role)}</td><td><span class="status-pill ${item.is_active?'':'is-muted'}">${item.is_active?'Active':'Inactive'}</span></td><td>${item.role==='student'?`<button class="btn btn-small ${item.is_active?'btn-secondary':'btn-primary'}" data-action="admin-toggle-user" data-user-id="${item.id}" data-next-active="${item.is_active?'false':'true'}">${item.is_active?'Deactivate':'Reactivate'}</button>`:'Protected'}</td></tr>`).join('');
}

async function loadAdminUsers(query='') {
  try {
    state.adminUserQuery=query;
    state.adminUsers=await api(`/admin/users?limit=30&q=${encodeURIComponent(query)}`);
    const tbody=document.getElementById('admin-user-table-body');
    if (tbody) tbody.innerHTML=adminUserTableRows(state.adminUsers.items)||'<tr><td colspan="4">No accounts found.</td></tr>';
    const count=document.getElementById('admin-user-count');
    if (count) count.textContent=`Showing ${state.adminUsers.items.length} of ${state.adminUsers.total}`;
  } catch(error) { toast(error.message); }
}


function renderView() {
  const host = document.getElementById('page-content');
  if (state.view === 'overview') host.innerHTML = renderOverview();
  else if (state.view === 'syllabus') { renderSyllabus(); return; }
  else if (state.view === 'planner') { renderPlanner(); return; }
  else if (state.view === 'resources') { renderResources(); return; }
  else if (state.view === 'questions') { renderPyqBank(); return; }
  else if (state.view === 'practice') { renderPractice(); return; }
  else if (state.view === 'tests') { renderMockTests(); return; }
  else if (state.view === 'mindmaps') { renderMindmaps(); return; }
  else if (state.view === 'tutor') { renderTutor(); return; }
  else if (state.view === 'analytics') { renderAnalytics(); return; }
  else if (state.view === 'community') { renderCommunity(); return; }
  else if (state.view === 'admin') { renderAdmin(); return; }
  else if (state.view === 'material') { renderMaterialDetail(); return; }
  else host.innerHTML = renderPlaceholder(state.view);
  setIcons(host);
}

async function refreshOverview() {
  const [profileResult, dashResult, papersResult] = await Promise.all([
    api('/profile'), api('/dashboard'), api('/papers'),
  ]);
  state.profile = profileResult;
  state.dashboard = dashResult;
  state.papers = papersResult.items;
  state.tasks = dashResult.tasks;
  try {
    state.plannerOverview = await api(`/planner/overview?paper_code=${encodeURIComponent(profileResult.paper_code)}&selected_date=${encodeURIComponent(localDateKey())}`);
  } catch (_) { state.plannerOverview = null; }
}

function openModal(title, eyebrow, bodyHTML) {
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-eyebrow').textContent = eyebrow;
  document.getElementById('modal-body').innerHTML = bodyHTML;
  document.getElementById('modal-backdrop').hidden = false;
  setIcons(document.getElementById('modal-backdrop'));
  const first = document.querySelector('#modal-body input, #modal-body select');
  first?.focus();
}

function closeModal() {
  document.getElementById('modal-backdrop').hidden = true;
}

function openPreferencesModal() {
  openModal('Personalise your preparation', 'YOUR STUDY PROFILE', `
    <form id="preferences-form">
      <div class="form-field"><label for="preference-paper">GATE paper</label><select class="form-control" id="preference-paper" name="paper_code">${paperOptions(state.profile.paper_code)}</select></div>
      <div class="form-field"><label for="preference-target">Your preparation goal</label><select class="form-control" id="preference-target" name="target"><option ${state.profile.target === 'IIT admission' ? 'selected' : ''}>IIT admission</option><option ${state.profile.target === 'Top GATE score' ? 'selected' : ''}>Top GATE score</option><option ${state.profile.target === 'PSU opportunity' ? 'selected' : ''}>PSU opportunity</option><option ${state.profile.target === 'Strong subject mastery' ? 'selected' : ''}>Strong subject mastery</option></select></div>
      <div class="form-field"><label for="preference-hours">Daily study target</label><select class="form-control" id="preference-hours" name="daily_hours">${[1,2,3,4,5,6,7,8,9,10,12,14,16].map((h) => `<option value="${h}" ${Number(state.profile.daily_hours) === h ? 'selected' : ''}>${h} hours per day</option>`).join('')}</select></div>
      <div class="modal-actions"><button class="btn btn-secondary" type="button" data-action="close-modal">Cancel</button><button class="btn btn-primary" type="submit">Save preferences ${icon('check', 13)}</button></div>
    </form>
  `);
  document.getElementById('preferences-form').addEventListener('submit', handlePreferencesSubmit);
}

function openTaskModal() {
  openModal('Add a study task', "TODAY'S PLAN", `
    <form id="task-modal-form">
      <div class="form-field"><label for="task-title">What will you work on?</label><input class="form-control" id="task-title" name="title" placeholder="e.g. Revise binary search trees" minlength="2" maxlength="140" required /></div>
      <div class="form-field"><label for="task-subject">Subject or category</label><input class="form-control" id="task-subject" name="subject" placeholder="e.g. Data Structures" maxlength="80" /></div>
      <div class="form-field"><label for="task-duration">Study duration</label><select class="form-control" id="task-duration" name="duration_minutes"><option value="25">25 minutes</option><option value="45">45 minutes</option><option value="60" selected>60 minutes</option><option value="90">90 minutes</option><option value="120">2 hours</option></select></div>
      <div class="form-field"><label for="task-priority">Priority</label><select class="form-control" id="task-priority" name="priority"><option>Normal</option><option>High</option><option>Low</option></select></div>
      <div class="modal-actions"><button class="btn btn-secondary" type="button" data-action="close-modal">Cancel</button><button class="btn btn-primary" type="submit">Add to my plan ${icon('plus', 13)}</button></div>
    </form>
  `);
  document.getElementById('task-modal-form').addEventListener('submit', handleModalTaskSubmit);
}

async function handlePreferencesSubmit(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = {
    paper_code: String(form.get('paper_code')),
    target: String(form.get('target')),
    daily_hours: Number(form.get('daily_hours')),
  };
  try {
    state.profile = await api('/profile', { method: 'PUT', body: JSON.stringify(payload) });
    closeModal();
    await refreshOverview();
    renderView();
    toast('Your preparation preferences were saved.');
  } catch (error) { toast(error.message); }
}

async function createTaskFromForm(form) {
  const data = new FormData(form);
  const title = String(data.get('title') || '').trim();
  if (title.length < 2) return toast('Please enter a task name.');
  const payload = {
    title,
    subject: String(data.get('subject') || 'General').trim() || 'General',
    duration_minutes: Number(data.get('duration_minutes') || 30),
    priority: String(data.get('priority') || 'Normal'),
  };
  try {
    await api('/tasks', { method: 'POST', body: JSON.stringify(payload) });
    closeModal();
    if (state.view === 'planner') await renderPlanner();
    else { await refreshOverview(); renderView(); }
    toast('Study task added to your plan.');
  } catch (error) { toast(error.message); }
}

function handleModalTaskSubmit(event) { event.preventDefault(); createTaskFromForm(event.currentTarget); }
function handleInlineTaskSubmit(event) { event.preventDefault(); createTaskFromForm(event.currentTarget); }

async function toggleTask(taskId) {
  const task = state.tasks.find((item) => item.id === Number(taskId)) || (state.dashboard?.tasks || []).find((item) => item.id === Number(taskId));
  if (!task) return;
  try {
    await api(`/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify({ completed: !task.completed }) });
    await refreshOverview();
    renderView();
    toast(!task.completed ? 'Task completed. Nice work.' : 'Task moved back to your list.');
  } catch (error) { toast(error.message); }
}

async function changePaper(code) {
  if (!code || code === state.profile.paper_code) return;
  try {
    state.profile = await api('/profile', { method: 'PUT', body: JSON.stringify({ ...state.profile, paper_code: code }) });
    await refreshOverview();
    renderView();
    toast(`Workspace switched to ${code}.`);
  } catch (error) { toast(error.message); }
}

function showSearchResults(query) {
  document.querySelector('.search-results')?.remove();
  if (!query.trim()) return;
  const options = [
    ['Overview', 'overview', 'grid'], ['Syllabus explorer', 'syllabus', 'book'], ['Mind maps', 'mindmaps', 'nodes'],
    ['PYQ bank', 'questions', 'layers'], ['Practice', 'practice', 'target'], ['Mock tests', 'tests', 'timer'],
    ['Study planner', 'planner', 'calendar'], ['Revision centre', 'revision', 'repeat'], ['Analytics', 'analytics', 'chart'],
    ['AI tutor', 'tutor', 'sparkles'], ['Resources', 'resources', 'bookmark'], ['Community', 'community', 'users'],
  ];
  if (state.user?.role === 'admin') options.push(['Administration', 'admin', 'shield']);
  const matches = options.filter((item) => item[0].toLowerCase().includes(query.toLowerCase()));
  const container = document.createElement('div');
  container.className = 'search-results';
  container.innerHTML = matches.length ? matches.map((item) => `<button class="search-result" data-action="go-view" data-view="${item[1]}"><span>${icon(item[2], 14)}</span>${escapeHTML(item[0])}</button>`).join('') : `<div class="empty-state"><strong>No matching sections</strong><p>Try syllabus, planner, practice or resources.</p></div>`;
  document.querySelector('.topbar').appendChild(container);
}

function applyTheme(theme) {
  document.documentElement.classList.toggle('dark', theme === 'dark');
  const button = document.getElementById('theme-toggle');
  if (button) button.innerHTML = icon(theme === 'dark' ? 'sun' : 'moon', 16);
  localStorage.setItem('gatepath-theme', theme);
}

function handleClick(event) {
  const actionTarget = event.target.closest('[data-action]');
  const navTarget = event.target.closest('[data-view].nav-item');
  if (navTarget) { setNav(navTarget.dataset.view); return; }
  if (!actionTarget) return;
  const action = actionTarget.dataset.action;
  if (action === 'go-view') { document.querySelector('.search-results')?.remove(); setNav(actionTarget.dataset.view); }
  else if (action === 'logout') signOut();
  else if (action === 'open-profile') openPreferencesModal();
  else if (action === 'create-task') openTaskModal();
  else if (action === 'close-modal') closeModal();
  else if (action === 'toggle-task') toggleTask(actionTarget.dataset.id);
  else if (action === 'open-material') openMaterial(actionTarget.dataset.topicId);
  else if (action === 'back-materials') setNav('resources');
  else if (action === 'toggle-material-bookmark') updateMaterial({ bookmarked: !state.materialDetail?.progress?.bookmarked });
  else if (action === 'save-material-note') updateMaterial({ personal_note: document.getElementById('material-personal-note')?.value || '' });
  else if (action === 'print-material') window.print();
  else if (action === 'open-pyq-attempt') openPyqAttempt(actionTarget.dataset.questionId);
  else if (action === 'toggle-pyq-bookmark') togglePyqBookmark(actionTarget.dataset.questionId, actionTarget.dataset.bookmarked === 'true');
  else if (action === 'refresh-pyq') { closeModal(); renderPyqBank(); }
  else if (action === 'select-mindmap-topic') { state.mindmapSelected = actionTarget.dataset.topicId; renderMindmaps(); }
  else if (action === 'open-mindmap-prerequisite') changeMindmapSection(actionTarget.dataset.sectionCode, actionTarget.dataset.topicId);
  else if (action === 'mock-start') startMockTest(actionTarget.dataset.testId);
  else if (action === 'mock-go-question') navigateMockQuestion(Number(actionTarget.dataset.index));
  else if (action === 'mock-previous') navigateMockQuestion(state.mockCurrentIndex - 1);
  else if (action === 'mock-next' || action === 'mock-save-next') navigateMockQuestion(state.mockCurrentIndex + 1);
  else if (action === 'mock-mark-review') {
    const question = state.mockSession?.questions?.[state.mockCurrentIndex];
    if (question) saveMockCurrentResponse({ marked_for_review: !question.response?.marked_for_review }).then(saved => { if (saved) { renderMockSession(); toast(question.response.marked_for_review ? 'Question marked for review.' : 'Review flag removed.'); } });
  }
  else if (action === 'mock-clear-answer') saveMockCurrentResponse({ answer: '' }).then(saved => { if (saved) { renderMockSession(); toast('Response cleared.'); } });
  else if (action === 'mock-submit') { if (window.confirm('Submit this mock examination now? You cannot change responses after submission.')) submitMockTest(false); }
  else if (action === 'mock-return') { state.mockResult = null; state.mockSession = null; renderMockTests(); }
  else if (action === 'mock-open-result') openMockResult(actionTarget.dataset.sessionId);
  else if (action === 'new-tutor-chat') { state.tutorConversationId = null; state.tutorMessages = []; state.tutorSimilarResult = null; state.tutorImageDataUrl = null; state.tutorImageName = ''; renderTutorContent(); }
  else if (action === 'open-tutor-conversation') loadTutorConversation(actionTarget.dataset.conversationId).catch(error => toast(error.message));
  else if (action === 'tutor-clear-image') { state.tutorImageDataUrl = null; state.tutorImageName = ''; renderTutorContent(); }
  else if (action === 'tutor-starter') submitTutorMessage(null, actionTarget.dataset.message);
  else if (action === 'tutor-generate-similar') generateTutorSimilarQuestions();
  else if (action === 'dismiss-tutor-generated') { state.tutorSimilarResult = null; renderTutorContent(); }
  else if (action === 'analytics-refresh') renderAnalytics();
  else if (action === 'community-open-post') openCommunityPost(Number(actionTarget.dataset.postId));
  else if (action === 'community-back') { state.communitySelectedPost = null; renderCommunity(); }
  else if (action === 'community-like') {
    const postId=Number(actionTarget.dataset.postId);
    api(`/community/posts/${postId}/like`,{method:'PUT',body:'{}'}).then(()=>state.communitySelectedPost?openCommunityPost(postId):renderCommunity()).catch(error=>toast(error.message));
  }
  else if (action === 'community-report') openCommunityReportForm(actionTarget.dataset.targetType,Number(actionTarget.dataset.targetId));
  else if (action === 'community-delete-post') {
    const postId=Number(actionTarget.dataset.postId);
    if (window.confirm('Delete this discussion? It will be removed from the public feed.')) api(`/community/posts/${postId}`,{method:'DELETE'}).then(()=>{state.communitySelectedPost=null;renderCommunity();toast('Discussion removed.');}).catch(error=>toast(error.message));
  }
  else if (action === 'community-delete-reply') {
    const replyId=Number(actionTarget.dataset.replyId);
    if (window.confirm('Remove this reply?')) api(`/community/replies/${replyId}`,{method:'DELETE'}).then(()=>openCommunityPost(state.communitySelectedPost.post.id)).catch(error=>toast(error.message));
  }
  else if (action === 'admin-refresh') renderAdmin();
  else if (action === 'admin-toggle-user') {
    const userId=Number(actionTarget.dataset.userId), active=actionTarget.dataset.nextActive==='true';
    if (window.confirm(`${active?'Reactivate':'Deactivate'} this student account? ${active?'':'Their active sessions will be revoked.'}`)) api(`/admin/users/${userId}`,{method:'PATCH',body:JSON.stringify({is_active:active})}).then(()=>renderAdmin()).then(()=>toast(active?'Student account reactivated.':'Student account deactivated.')).catch(error=>toast(error.message));
  }
  else if (action === 'admin-report-action') {
    const reportId=Number(actionTarget.dataset.reportId);
    api(`/admin/reports/${reportId}`,{method:'PATCH',body:JSON.stringify({status:actionTarget.dataset.resolution,action:actionTarget.dataset.moderation,note:''})}).then(()=>renderAdmin()).then(()=>toast('Report reviewed.')).catch(error=>toast(error.message));
  }
}

function updateAccountUI() {
  if (!state.user) return;
  const first = state.user.full_name.trim().split(/\s+/)[0] || 'Student';
  const initials = state.user.full_name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join('').toUpperCase();
  const name = document.getElementById('account-name');
  const avatar = document.getElementById('account-avatar');
  const sidebarName = document.querySelector('.profile-mini b');
  const sidebarMeta = document.querySelector('.profile-mini small');
  if (name) name.textContent = first;
  if (avatar) avatar.textContent = initials || 'GP';
  if (sidebarName) sidebarName.textContent = state.user.full_name;
  if (sidebarMeta) sidebarMeta.textContent = state.user.email;
  const adminNav = document.getElementById('admin-nav-item');
  if (adminNav) adminNav.hidden = state.user.role !== 'admin';
}

async function signOut() {
  try {
    await api('/auth/logout', { method: 'POST', body: '{}' });
  } catch (_) { /* The server-side session may already have expired. */ }
  window.location.assign('/login');
}

async function boot() {
  setIcons();
  try {
    const session = await api('/auth/me');
    state.user = session.user;
    state.profile = session.profile;
    updateAccountUI();
    await refreshOverview();
    const requestedPaper = new URLSearchParams(window.location.search).get('paper')?.toUpperCase();
    if (requestedPaper && state.papers.some((paper) => paper.code === requestedPaper)) {
      if (requestedPaper !== state.profile.paper_code) {
        state.profile = await api('/profile', {
          method: 'PUT',
          body: JSON.stringify({ ...state.profile, paper_code: requestedPaper }),
        });
      }
      window.history.replaceState({}, '', '/app');
    }
    renderView();
  } catch (error) {
    if (error.message.toLowerCase().includes('sign in') || error.message.includes('(401)')) {
      const next = `${window.location.pathname}${window.location.search}`;
      window.location.replace(`/login?next=${encodeURIComponent(next)}`);
      return;
    }
    document.getElementById('page-content').innerHTML = `<section class="panel content-placeholder"><div><div class="placeholder-icon">${icon('file', 24)}</div><h2>Could not connect to the GATEPath API</h2><p>${escapeHTML(error.message)}. Start the backend using the instructions in README.md and reload this page.</p></div></section>`;
  }
  const theme = localStorage.getItem('gatepath-theme') || 'light';
  applyTheme(theme);

  document.addEventListener('click', handleClick);
  document.getElementById('theme-toggle').addEventListener('click', () => applyTheme(document.documentElement.classList.contains('dark') ? 'light' : 'dark'));
  document.getElementById('mobile-menu').addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'));
  document.addEventListener('change', async (event) => {
    if (event.target && event.target.id === 'paper-switcher') changePaper(event.target.value);
    if (event.target?.id === 'pyq-year-filter') { state.pyqYear = Number(event.target.value); state.pyqSession = 'all'; await loadPyqQuestionItems(); }
    if (event.target?.id === 'pyq-session-filter') { state.pyqSession = event.target.value; await loadPyqQuestionItems(); }
    if (event.target?.id === 'pyq-type-filter') { state.pyqType = event.target.value; await loadPyqQuestionItems(); }
    if (event.target?.id === 'pyq-section-filter') { state.pyqSection = event.target.value; await loadPyqQuestionItems(); }
    if (event.target?.id === 'pyq-bookmarked-filter') { state.pyqBookmarked = event.target.checked; await loadPyqQuestionItems(); }
    const topicId = event.target?.dataset?.topicStatusSelect;
    if (topicId) {
      try {
        await api(`/materials/${encodeURIComponent(topicId)}/progress?paper_code=${encodeURIComponent(state.profile.paper_code)}`, { method: 'PATCH', body: JSON.stringify({ status: event.target.value }) });
        await renderSyllabus();
        toast('Topic progress updated.');
      } catch (error) { toast(error.message); }
    }
    if (event.target?.id === 'practice-section-filter') {
      state.practiceFilters.section_code = event.target.value;
      state.practiceFilters.topic_id = 'all';
      state.practiceFilters.difficulty = document.getElementById('practice-difficulty-filter')?.value || 'all';
      state.practiceFilters.question_type = document.getElementById('practice-type-filter')?.value || 'all';
      state.practiceFilters.q = document.getElementById('practice-search')?.value || '';
      renderPractice();
    } else if (['practice-topic-filter','practice-difficulty-filter','practice-type-filter'].includes(event.target?.id)) {
      updatePracticeFiltersFromUI();
    }
  });
  document.addEventListener('click', (event) => {
    if (event.target.closest('#mindmap-zoom-in')) { state.mindmapZoom = Math.min(1.6, state.mindmapZoom + 0.1); applyMindmapZoom(); }
    if (event.target.closest('#mindmap-zoom-out')) { state.mindmapZoom = Math.max(0.6, state.mindmapZoom - 0.1); applyMindmapZoom(); }
    if (event.target.closest('#mindmap-export')) downloadMindmapSvg();
    if (event.target.closest('#mindmap-fullscreen')) { document.querySelector('.mindmap-panel')?.classList.toggle('is-fullscreen'); }
  });
  document.addEventListener('change', (event) => {
    if (event.target?.id === 'mindmap-section-select') changeMindmapSection(event.target.value);
  });
  document.getElementById('global-search').addEventListener('input', (event) => showSearchResults(event.target.value));
  document.addEventListener('input', (event) => {
    if (event.target?.id === 'pyq-search') { state.pyqQuery = event.target.value; loadPyqQuestionItems(); }
    if (event.target?.id === 'practice-search') {
      state.practiceFilters.q = event.target.value;
      if (state.practiceSearchHandle) window.clearTimeout(state.practiceSearchHandle);
      state.practiceSearchHandle = window.setTimeout(async () => {
        try {
          await loadPracticeQuestions();
          const grid = document.querySelector('.practice-question-grid');
          if (grid) grid.innerHTML = state.practiceItems.length ? state.practiceItems.map(practiceQuestionCard).join('') : '<div class="empty-state"><strong>No matching questions</strong><p>Try another search phrase.</p></div>';
          const meta = document.querySelector('.practice-results-head p');
          if (meta) meta.textContent = `${state.practiceItems.length} questions match your filters`;
        } catch (error) { toast(error.message); }
      }, 220);
    }
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.search-box') && !event.target.closest('.search-results')) document.querySelector('.search-results')?.remove();
  });
  document.addEventListener('keydown', (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); document.getElementById('global-search').focus(); }
    if (event.key === 'Escape') { closeModal(); document.querySelector('.search-results')?.remove(); document.getElementById('sidebar').classList.remove('open'); }
  });
  document.getElementById('modal-backdrop').addEventListener('click', (event) => { if (event.target.id === 'modal-backdrop') closeModal(); });
}

boot();
