(() => {
  const card = document.getElementById('auth-card');
  const pathname = window.location.pathname;
  const params = new URLSearchParams(window.location.search);
  const resetToken = params.get('token') || '';
  const safeNext = (() => {
    const value = params.get('next') || '/app';
    if (!value.startsWith('/') || value.startsWith('//') || value.includes('\\')) return '/app';
    return value;
  })();
  let papers = [];
  let requestedPaperCode = 'CS';

  const escapeHTML = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const nextQuery = `?next=${encodeURIComponent(safeNext)}`;
  const showMessage = (message, success = false) => {
    const node = document.getElementById('auth-message');
    if (!node) return;
    node.textContent = message;
    node.className = `auth-message visible${success ? ' success' : ''}`;
  };
  const setBusy = (button, busy, label) => {
    button.disabled = busy;
    button.textContent = busy ? 'Please wait…' : label;
  };
  const passwordField = (id, label = 'Password', hint = '', autocomplete = 'new-password') => `
    <div class="field"><label for="${id}">${label}</label><div class="password-wrap"><input id="${id}" name="${id}" type="password" autocomplete="${autocomplete}" required minlength="10" maxlength="128" placeholder="Enter your password"/><button type="button" class="toggle-password" data-toggle-password="${id}">Show</button></div>${hint ? `<small class="field-help">${hint}</small>` : ''}</div>`;

  function renderLogin() {
    card.innerHTML = `
      <div class="auth-heading"><span class="kicker">WELCOME BACK</span><h2>Sign in to your workspace.</h2><p>Pick up where you left off and keep your preparation moving.</p></div>
      <form class="auth-form" id="login-form">
        <div class="field"><label for="email">Email address</label><input id="email" name="email" type="email" autocomplete="email" maxlength="254" required placeholder="you@example.com"/></div>
        ${passwordField('password', 'Password', '', 'current-password')}
        <div class="form-options"><span>Secure, private student workspace</span><a href="/forgot-password">Forgot password?</a></div>
        <button class="primary-btn" type="submit">Sign in to GATEPath <span>→</span></button>
      </form>
      <div id="auth-message" class="auth-message" role="alert"></div>
      <p class="auth-switch">New to GATEPath? <a href="/register${nextQuery}">Create your account</a></p>
      <p class="auth-footnote">Your study plans and progress are private to your account.</p>`;
    document.getElementById('login-form').addEventListener('submit', submitLogin);
  }

  function renderRegister() {
    const nextUrl = new URL(safeNext, window.location.origin);
    const requestedPaper = (nextUrl.searchParams.get('paper') || params.get('paper') || 'CS').toUpperCase();
    requestedPaperCode = requestedPaper;
    const paperOptions = papers.map((paper) => `<option value="${escapeHTML(paper.code)}" ${paper.code === requestedPaper ? 'selected' : ''}>${escapeHTML(paper.code)} — ${escapeHTML(paper.name)}</option>`).join('');
    card.innerHTML = `
      <div class="auth-heading"><span class="kicker">START YOUR JOURNEY</span><h2>Create your GATEPath account.</h2><p>Your own preparation space, with your paper and daily study goal.</p></div>
      <form class="auth-form" id="register-form">
        <div class="field"><label for="full_name">Full name</label><input id="full_name" name="full_name" autocomplete="name" maxlength="100" minlength="2" required placeholder="Your name"/></div>
        <div class="field"><label for="email">Email address</label><input id="email" name="email" type="email" autocomplete="email" maxlength="254" required placeholder="you@example.com"/></div>
        ${passwordField('password', 'Create password', 'At least 10 characters, including uppercase, lowercase and a number.')}
        <div class="field-row"><div class="field"><label for="paper_code">GATE paper</label><select id="paper_code" name="paper_code">${paperOptions || '<option value="CS">CS — Computer Science</option>'}</select></div><div class="field"><label for="daily_hours">Daily study goal</label><select id="daily_hours" name="daily_hours">${[2,3,4,5,6,7,8,9,10,12,14,16].map((n) => `<option value="${n}" ${n === 5 ? 'selected' : ''}>${n} hours</option>`).join('')}</select></div></div>
        <div class="field"><label for="target">Your preparation goal</label><select id="target" name="target"><option>IIT admission</option><option>Top GATE score</option><option>PSU opportunity</option><option>Strong subject mastery</option></select></div>
        <button class="primary-btn" type="submit">Create my account <span>→</span></button>
      </form>
      <div id="auth-message" class="auth-message" role="alert"></div>
      <p class="auth-switch">Already have an account? <a href="/login${nextQuery}">Sign in</a></p>
      <p class="auth-footnote">You can change your selected paper and study goal later in your profile.</p>`;
    document.getElementById('register-form').addEventListener('submit', submitRegister);
  }

  function renderForgot() {
    card.innerHTML = `
      <div class="auth-heading"><span class="kicker">ACCOUNT RECOVERY</span><h2>Reset your password.</h2><p>Enter the email address associated with your GATEPath account.</p></div>
      <form class="auth-form" id="forgot-form"><div class="field"><label for="email">Email address</label><input id="email" name="email" type="email" autocomplete="email" maxlength="254" required placeholder="you@example.com"/></div><button class="primary-btn" type="submit">Send reset instructions <span>→</span></button></form>
      <div id="auth-message" class="auth-message" role="alert"></div>
      <p class="auth-switch"><a href="/login${nextQuery}">← Back to sign in</a></p>
      <p class="auth-footnote">Password recovery requires the platform administrator to configure email delivery.</p>`;
    document.getElementById('forgot-form').addEventListener('submit', submitForgot);
  }

  function renderReset() {
    if (!resetToken) {
      card.innerHTML = `<div class="auth-heading"><span class="kicker">ACCOUNT RECOVERY</span><h2>Reset link missing.</h2><p>Open the complete password reset link from your email, or request a new one.</p></div><p class="auth-switch"><a href="/forgot-password">Request another reset link</a></p>`;
      return;
    }
    card.innerHTML = `
      <div class="auth-heading"><span class="kicker">CHOOSE A NEW PASSWORD</span><h2>Secure your account.</h2><p>Choose a new password you have not used for this account.</p></div>
      <form class="auth-form" id="reset-form">${passwordField('new_password', 'New password', 'At least 10 characters, including uppercase, lowercase and a number.')}<button class="primary-btn" type="submit">Update password <span>→</span></button></form>
      <div id="auth-message" class="auth-message" role="alert"></div>
      <p class="auth-switch"><a href="/login">Back to sign in</a></p>`;
    document.getElementById('reset-form').addEventListener('submit', submitReset);
  }

  async function post(path, payload) {
    const response = await fetch(`/api${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, credentials: 'same-origin', body: JSON.stringify(payload) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = Array.isArray(data.detail) ? data.detail.map((item) => item.msg).join('. ') : data.detail;
      throw new Error(detail || `Request failed (${response.status})`);
    }
    return data;
  }

  async function submitLogin(event) {
    event.preventDefault();
    const button = event.currentTarget.querySelector('button[type="submit"]');
    setBusy(button, true, 'Sign in to GATEPath →');
    try {
      const form = new FormData(event.currentTarget);
      await post('/auth/login', { email: form.get('email'), password: form.get('password') });
      window.location.assign(safeNext);
    } catch (error) {
      showMessage(error.message);
      setBusy(button, false, 'Sign in to GATEPath →');
    }
  }

  async function submitRegister(event) {
    event.preventDefault();
    const button = event.currentTarget.querySelector('button[type="submit"]');
    setBusy(button, true, 'Create my account →');
    try {
      const form = new FormData(event.currentTarget);
      await post('/auth/register', {
        full_name: form.get('full_name'), email: form.get('email'), password: form.get('password'),
        paper_code: form.get('paper_code'), target: form.get('target'), daily_hours: Number(form.get('daily_hours')),
      });
      window.location.assign(safeNext);
    } catch (error) {
      showMessage(error.message);
      setBusy(button, false, 'Create my account →');
    }
  }

  async function submitForgot(event) {
    event.preventDefault();
    const button = event.currentTarget.querySelector('button[type="submit"]');
    setBusy(button, true, 'Send reset instructions →');
    try {
      const form = new FormData(event.currentTarget);
      const data = await post('/auth/request-password-reset', { email: form.get('email') });
      showMessage(data.message, true);
    } catch (error) {
      showMessage(error.message);
    } finally {
      setBusy(button, false, 'Send reset instructions →');
    }
  }

  async function submitReset(event) {
    event.preventDefault();
    const button = event.currentTarget.querySelector('button[type="submit"]');
    setBusy(button, true, 'Update password →');
    try {
      const form = new FormData(event.currentTarget);
      const data = await post('/auth/reset-password', { token: resetToken, new_password: form.get('new_password') });
      showMessage(data.message, true);
      window.setTimeout(() => window.location.assign('/login'), 1100);
    } catch (error) {
      showMessage(error.message);
      setBusy(button, false, 'Update password →');
    }
  }

  card.addEventListener('click', (event) => {
    const toggle = event.target.closest('[data-toggle-password]');
    if (!toggle) return;
    const input = document.getElementById(toggle.dataset.togglePassword);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    toggle.textContent = input.type === 'password' ? 'Show' : 'Hide';
  });

  async function init() {
    if (pathname === '/register') renderRegister();
    else if (pathname === '/forgot-password') renderForgot();
    else if (pathname === '/reset-password') renderReset();
    else renderLogin();
    if (pathname === '/register') {
      try {
        const response = await fetch('/api/papers', { credentials: 'same-origin' });
        const data = await response.json();
        if (response.ok && Array.isArray(data.items)) {
          papers = data.items;
          const select = document.getElementById('paper_code');
          if (select) {
            select.innerHTML = papers.map((paper) => `<option value="${escapeHTML(paper.code)}">${escapeHTML(paper.code)} — ${escapeHTML(paper.name)}</option>`).join('');
            select.value = papers.some((paper) => paper.code === requestedPaperCode) ? requestedPaperCode : 'CS';
          }
        }
      } catch (_) { /* The CS fallback keeps account creation available if the catalogue is temporarily offline. */ }
    }
  }

  init();
})();
