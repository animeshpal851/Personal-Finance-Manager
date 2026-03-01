// ── Sidebar toggle ───────────────────────────────────────────
const sidebar = document.getElementById('sidebar');
const menuToggle = document.getElementById('menuToggle');
if (menuToggle) {
  menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

// ── Flash auto-dismiss ───────────────────────────────────────
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => el.remove(), 5000);
});

// ── Tabs ─────────────────────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.tab;
    const container = btn.closest('.tabs').parentElement;
    container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    container.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    const panel = container.querySelector(`[data-panel="${target}"]`);
    if (panel) panel.classList.add('active');
  });
});

// ── Modal helpers ────────────────────────────────────────────
function openModal(id) {
  document.getElementById(id).classList.add('show');
}
function closeModal(id) {
  document.getElementById(id).classList.remove('show');
}
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.classList.remove('show');
  });
});

// ── Transaction type selector ────────────────────────────────
const typeInput = document.getElementById('type-input');
const incomeBtn = document.getElementById('income-btn');
const expenseBtn = document.getElementById('expense-btn');
const incomeCats = document.getElementById('income-categories');
const expenseCats = document.getElementById('expense-categories');

function selectType(type) {
  if (!typeInput) return;
  typeInput.value = type;
  if (type === 'income') {
    incomeBtn?.classList.add('active');
    expenseBtn?.classList.remove('active');
    incomeCats && (incomeCats.style.display = 'block');
    expenseCats && (expenseCats.style.display = 'none');
  } else {
    expenseBtn?.classList.add('active');
    incomeBtn?.classList.remove('active');
    expenseCats && (expenseCats.style.display = 'block');
    incomeCats && (incomeCats.style.display = 'none');
  }
}

incomeBtn?.addEventListener('click', () => selectType('income'));
expenseBtn?.addEventListener('click', () => selectType('expense'));
if (typeInput) selectType('expense'); // default

// ── Chart.js global defaults ─────────────────────────────────
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#8a93b2';
  Chart.defaults.borderColor = '#2a2f42';
  Chart.defaults.font.family = "'DM Sans', sans-serif";
}

// ── Health score ring animation ──────────────────────────────
document.querySelectorAll('.health-ring-fill').forEach(path => {
  const dasharray = parseFloat(path.getAttribute('stroke-dasharray')) || 0;
  const target = parseFloat(path.dataset.target || 0);
  const offset = dasharray - (dasharray * target / 100);
  path.style.strokeDashoffset = dasharray;
  setTimeout(() => { path.style.strokeDashoffset = offset; }, 300);
});
