// static/js/forecast.js (v12) - Enhanced Forecast Visualization

let ordersChart = null;
let revenueChart = null;
let ordersCompareChart = null;
let revenueCompareChart = null;
let deliveriesCompareChart = null;

const MAX_POINTS = 60;

const COLORS = {
  blue: { line: '#1d4ed8', area: 'rgba(29,78,216,0.14)', point: '#1d4ed8' },
  amber: { line: '#f59e0b', area: 'rgba(245,158,11,0.10)', point: '#f59e0b' },
  emerald: { solid: '#059669', hover: '#10b981' },
  emeraldGradTop: 'rgba(5,150,105,0.92)',
  emeraldGradBottom: 'rgba(5,150,105,0.38)',
  rose: { line: '#ef4444', area: 'rgba(239,68,68,0.10)', point: '#ef4444' },
  violet: { line: '#7c3aed', area: 'rgba(124,58,237,0.14)', point: '#7c3aed' },
  cyan: { line: '#06b6d4', area: 'rgba(6,182,212,0.10)', point: '#06b6d4' },
  slate: { axis: '#64748b', grid: 'rgba(0,0,0,0.05)' }
};

document.addEventListener('DOMContentLoaded', () => {
  const startDate = document.getElementById('startDate');
  const endDate = document.getElementById('endDate');
  const horizon = document.getElementById('horizonSelect');
  const refresh = document.getElementById('refreshForecasts');

  const today = new Date();
  const plus14 = new Date(today);
  plus14.setDate(today.getDate() + 14);
  if (startDate) startDate.value = toInputDate(today);
  if (endDate) endDate.value = toInputDate(plus14);

  refresh?.addEventListener('click', () => {
    const i = refresh.querySelector('i');
    if (i) {
      i.style.animation = 'spin .5s linear';
      setTimeout(() => (i.style.animation = ''), 500);
    }
    loadForecasts();
  });

  horizon?.addEventListener('change', e => {
    if (e.target.value !== 'custom') {
      const d = parseInt(e.target.value, 10);
      const s = new Date(), e2 = new Date();
      e2.setDate(s.getDate() + d);
      if (startDate) startDate.value = toInputDate(s);
      if (endDate) endDate.value = toInputDate(e2);
      loadForecasts();
    }
  });

  startDate?.addEventListener('change', () => {
    if (horizon) horizon.value = 'custom';
    loadForecasts();
  });
  endDate?.addEventListener('change', () => {
    if (horizon) horizon.value = 'custom';
    loadForecasts();
  });

  loadForecasts();
});

function toInputDate(d) {
  const y = d.getFullYear(), m = String(d.getMonth() + 1).padStart(2, '0'), da = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${da}`;
}

async function loadForecasts() {
  try {
    const s = document.getElementById('startDate')?.value;
    const e = document.getElementById('endDate')?.value;
    const qs = new URLSearchParams();
    if (s && e) {
      qs.append('start_date', s);
      qs.append('end_date', e);
    } else {
      const h = document.getElementById('horizonSelect')?.value || '14';
      if (h !== 'custom') qs.append('horizon', h);
    }

    showLoadingPlaceholders();
    const res = await fetch(`/api/forecast?${qs.toString()}`);
    const text = await res.text();
    let data = {};
    if (text) data = JSON.parse(text);
    if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);

    setKPI('kpiOrders', data.kpis?.totalOrders ?? 0);
    setKPI('kpiRevenue', data.kpis?.totalRevenue ?? 0, true);
    setKPI('kpiDeliveries', data.kpis?.totalDeliveries ?? 0);
    setKPI('kpiRisks', (data.inventoryWatch || []).length);

    drawOrdersChart(data.ordersForecast || {});
    drawRevenueChart(data.revenueForecast || {});
    renderOrdersCompare(data.ordersActuals, data.ordersForecast);
    renderRevenueCompare(data.revenueActuals, data.revenueForecast);
    renderDeliveriesCompare(data.deliveriesActuals, data.shipmentForecast);
    renderInventory(data.inventoryWatch || []);
    renderShipments(data.shipmentForecast || []);

    document.dispatchEvent(new CustomEvent("forecastDataLoaded", { detail: data }));
  } catch (err) {
    console.error('[forecast] load error:', err);
    showErrorPlaceholders();
  }
}

function setKPI(id, value, currency = false) {
  const el = document.getElementById(id);
  if (!el) return;
  const current = parseFloat(String(el.textContent).replace(/[₹,]/g, '')) || 0;
  const dur = 800, t0 = performance.now();
  const ease = t => 1 - Math.pow(1 - t, 4);
  function step(ts) {
    const p = Math.min((ts - t0) / dur, 1);
    const v = current + (value - current) * ease(p);
    el.textContent = currency
      ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(v || 0)
      : Math.round(v).toLocaleString('en-IN');
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function baseLineOptions() {
  return {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false }, ticks: { font: { size: 9 }, color: COLORS.slate.axis } },
      y: { beginAtZero: true, grid: { color: COLORS.slate.grid }, ticks: { font: { size: 9 }, color: COLORS.slate.axis } }
    }
  };
}

function baseBarOptions() {
  return {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: COLORS.slate.grid },
        ticks: {
          color: COLORS.slate.axis,
          callback: v => {
            if (v >= 100000) return '₹' + (v / 100000).toFixed(1) + 'L';
            if (v >= 1000) return '₹' + (v / 1000).toFixed(1) + 'K';
            return '₹' + v;
          }
        }
      }
    }
  };
}

// Chart Drawing Functions
function drawOrdersChart({ labels = [], values = [] }) {
  const c = document.getElementById('ordersForecastChart');
  if (!c) return;
  if (ordersChart) ordersChart.destroy();
  ordersChart = new Chart(c, {
    type: 'line',
    data: { labels, datasets: [{ data: values, borderColor: COLORS.blue.line, backgroundColor: COLORS.blue.area, fill: true, tension: 0.35, borderWidth: 2 }] },
    options: baseLineOptions()
  });
}

function drawRevenueChart({ labels = [], values = [] }) {
  const c = document.getElementById('revenueForecastChart');
  if (!c) return;
  if (revenueChart) revenueChart.destroy();
  revenueChart = new Chart(c, {
    type: 'bar',
    data: { labels, datasets: [{ data: values, backgroundColor: COLORS.emerald.solid, hoverBackgroundColor: COLORS.emerald.hover, borderRadius: 4 }] },
    options: baseBarOptions()
  });
}

// Comparison Charts
function renderOrdersCompare(actual = {}, predicted = {}) {
  const ctx = document.getElementById('ordersCompareChart');
  if (!ctx) return;
  if (ordersCompareChart) ordersCompareChart.destroy();
  ordersCompareChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: predicted.labels || actual.labels,
      datasets: [
        { label: 'Actual', data: actual.values, borderColor: COLORS.blue.line, fill: true, backgroundColor: COLORS.blue.area, tension: 0.35 },
        { label: 'Predicted', data: predicted.values, borderColor: COLORS.amber.line, fill: true, backgroundColor: COLORS.amber.area, borderDash: [6, 6], tension: 0.35 }
      ]
    },
    options: baseLineOptions()
  });
}

function renderRevenueCompare(actual = {}, predicted = {}) {
  const ctx = document.getElementById('revenueCompareChart');
  if (!ctx) return;
  if (revenueCompareChart) revenueCompareChart.destroy();
  revenueCompareChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: predicted.labels || actual.labels,
      datasets: [
        { label: 'Actual', data: actual.values, backgroundColor: COLORS.emerald.solid },
        { label: 'Predicted', type: 'line', data: predicted.values, borderColor: COLORS.rose.line, backgroundColor: COLORS.rose.area, fill: true, tension: 0.35, borderDash: [6, 6] }
      ]
    },
    options: baseBarOptions()
  });
}

function renderDeliveriesCompare(actual = {}, predicted = []) {
  const ctx = document.getElementById('deliveriesCompareChart');
  if (!ctx) return;
  if (deliveriesCompareChart) deliveriesCompareChart.destroy();
  const predVals = predicted.map(p => p.expected_deliveries || 0);
  const predLabels = predicted.map(p => p.date || '');
  deliveriesCompareChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: predLabels || actual.labels,
      datasets: [
        { label: 'Actual', data: actual.values, borderColor: COLORS.violet.line, backgroundColor: COLORS.violet.area, fill: true, tension: 0.35 },
        { label: 'Predicted', data: predVals, borderColor: COLORS.cyan.line, backgroundColor: COLORS.cyan.area, fill: true, tension: 0.35, borderDash: [6, 6] }
      ]
    },
    options: baseLineOptions()
  });
}

function renderInventory(items) {
  const tb = document.getElementById('inventoryWatchBody');
  if (!tb) return;
  tb.innerHTML = items.length
    ? items.map(it => `<tr>
      <td>${it.product}</td><td>${it.stock}</td><td>${it.daily_rate}</td><td>${it.days_left}</td>
      <td><span class="status-badge">${it.status || 'OK'}</span></td></tr>`).join('')
    : `<tr><td colspan="5" class="empty-state">No risks detected</td></tr>`;
}

function renderShipments(items) {
  const tb = document.getElementById('shipmentForecastBody');
  if (!tb) return;
  tb.innerHTML = items.map(r => `<tr><td>${r.date}</td><td>${r.expected_deliveries}</td><td>${r.on_time_pct}%</td></tr>`).join('');
}

function showLoadingPlaceholders() {
  document.querySelectorAll('.loading').forEach(el => el.textContent = 'Loading...');
}

function showErrorPlaceholders() {
  document.querySelectorAll('.value').forEach(el => el.textContent = "—");
}
