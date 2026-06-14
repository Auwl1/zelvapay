// ===== ZELVAPAY MAIN JS =====

function toggleNav() {
  const links = document.querySelector('.nav-links');
  if (links) {
    links.style.display = links.style.display === 'flex' ? 'none' : 'flex';
    links.style.flexDirection = 'column';
    links.style.position = 'fixed';
    links.style.top = '70px';
    links.style.left = '0';
    links.style.right = '0';
    links.style.background = 'var(--bg2)';
    links.style.padding = '20px';
    links.style.borderBottom = '1px solid var(--border)';
    links.style.zIndex = '99';
  }
}

// Toast notification
function showToast(message, type = 'success') {
  let toast = document.querySelector('.toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  toast.className = `toast toast-${type}`;
  setTimeout(() => toast.classList.add('show'), 10);
  setTimeout(() => toast.classList.remove('show'), 3500);
}

// Copy to clipboard
function copyText(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    const old = btn.textContent;
    btn.textContent = 'Copied!';
    showToast('Copied to clipboard', 'success');
    setTimeout(() => btn.textContent = old, 2000);
  });
}

// Format currency
function formatNaira(amount) {
  return '₦' + Number(amount).toLocaleString('en-NG', { minimumFractionDigits: 2 });
}

// Simple tab switcher
function switchTab(tabEl, targetId) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
  tabEl.classList.add('active');
  const panel = document.getElementById(targetId);
  if (panel) panel.style.display = 'block';
}

// Select gift card
function selectGiftCard(el) {
  document.querySelectorAll('.gift-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  const name = el.querySelector('.gift-name')?.textContent;
  const input = document.getElementById('selected-giftcard');
  if (input) input.value = name;
}

// Select network
function selectNetwork(btn, network) {
  document.querySelectorAll('.network-btn').forEach(b => b.classList.remove('active-network'));
  btn.classList.add('active-network');
  const input = document.getElementById('network-input');
  if (input) input.value = network;
  loadPlans(network);
}

// Mock plan loader
function loadPlans(network) {
  const plans = {
    MTN: [
      { id: 'mtn_500mb', label: '500MB – 1 Day', price: 130 },
      { id: 'mtn_1gb',   label: '1GB – 7 Days',  price: 230 },
      { id: 'mtn_2gb',   label: '2GB – 30 Days', price: 460 },
      { id: 'mtn_5gb',   label: '5GB – 30 Days', price: 1100 },
      { id: 'mtn_10gb',  label: '10GB – 30 Days',price: 2000 },
    ],
    Airtel: [
      { id: 'airtl_1gb',  label: '1GB – 7 Days',  price: 250 },
      { id: 'airtl_2gb',  label: '2GB – 30 Days', price: 500 },
      { id: 'airtl_5gb',  label: '5GB – 30 Days', price: 1200 },
      { id: 'airtl_10gb', label: '10GB – 30 Days',price: 2200 },
    ],
    Glo: [
      { id: 'glo_1gb',  label: '1GB – 30 Days', price: 200 },
      { id: 'glo_3gb',  label: '3GB – 30 Days', price: 500 },
      { id: 'glo_5gb',  label: '5GB – 30 Days', price: 1000 },
    ],
    '9Mobile': [
      { id: '9mob_1gb', label: '1GB – 30 Days', price: 300 },
      { id: '9mob_2gb', label: '2GB – 30 Days', price: 550 },
      { id: '9mob_5gb', label: '5GB – 30 Days', price: 1200 },
    ],
  };

  const planSelect = document.getElementById('plan-select');
  if (!planSelect) return;
  planSelect.innerHTML = '<option value="">Select Plan</option>';
  (plans[network] || []).forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = `${p.label} — ₦${p.price}`;
    opt.dataset.price = p.price;
    planSelect.appendChild(opt);
  });
  planSelect.addEventListener('change', function () {
    const selected = this.options[this.selectedIndex];
    const priceEl = document.getElementById('plan-price');
    if (priceEl && selected.dataset.price) {
      priceEl.textContent = formatNaira(selected.dataset.price);
    }
  });
}

// Mask/unmask API key
function toggleKeyVisibility(keyId, btn) {
  const el = document.getElementById(keyId);
  if (!el) return;
  if (el.dataset.masked === 'true') {
    el.textContent = el.dataset.full;
    el.dataset.masked = 'false';
    btn.textContent = 'Hide';
  } else {
    el.dataset.full = el.textContent;
    el.textContent = el.textContent.substring(0, 12) + '••••••••••••••••••••••••••••';
    el.dataset.masked = 'true';
    btn.textContent = 'Show';
  }
}

// Mask all API keys on load
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.api-key-text').forEach(el => {
    if (el.textContent.length > 12) {
      el.dataset.full = el.textContent;
      el.dataset.masked = 'true';
      el.textContent = el.textContent.substring(0, 12) + '••••••••••••••••••••••••••••';
    }
  });
});

// Form submission simulation
function submitForm(e, msg) {
  e.preventDefault();
  const btn = e.target.querySelector('[type="submit"]') || e.target.querySelector('.btn-primary');
  if (btn) {
    const old = btn.textContent;
    btn.textContent = 'Processing...';
    btn.disabled = true;
    setTimeout(() => {
      btn.textContent = old;
      btn.disabled = false;
      showToast(msg || 'Transaction successful!', 'success');
    }, 1800);
  }
}

// Animate numbers on scroll
function animateCounters() {
  document.querySelectorAll('.stat-num').forEach(el => {
    const text = el.textContent;
    const num = parseFloat(text.replace(/[^0-9.]/g, ''));
    const suffix = text.replace(/[0-9.]/g, '');
    let start = 0;
    const step = num / 60;
    const timer = setInterval(() => {
      start += step;
      if (start >= num) { start = num; clearInterval(timer); }
      el.textContent = (num >= 1000 ? (start / 1000).toFixed(1) + 'K' : start.toFixed(0)) + suffix.replace(/\d/g, '');
    }, 16);
  });
}

const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) animateCounters(); });
}, { threshold: 0.5 });

const statsEl = document.querySelector('.hero-stats');
if (statsEl) observer.observe(statsEl);
