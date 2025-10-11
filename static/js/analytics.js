// /static/js/analytics.js

let charts = {
  revenue: null,
  categories: null,
  region: null,
  hourly: null,
  status: null
};

document.addEventListener("DOMContentLoaded", () => {
  const select = document.getElementById("dateRangeSelect");
  if (select) {
    select.addEventListener("change", () => loadAnalytics());
  }
  // chart type toggle buttons
  document.querySelectorAll(".chart-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const type = e.target.textContent.trim().toLowerCase(); // 'line' or 'bar'
      changeChartType("revenue", type);
    });
  });

  loadAnalytics();
});

async function loadAnalytics() {
  try {
    const days = document.getElementById("dateRangeSelect")?.value || "30";
    const res = await fetch(`/api/analytics?days=${encodeURIComponent(days)}`);
    const data = await res.json();

    renderKPIs(data.kpis);
    renderRevenueChart(data.series.revenueTrend);
    renderCategoriesChart(data.series.categories);
    renderRegionChart(data.series.region);
    renderHourlyChart(data.series.hourly);
    renderStatusChart(data.series.status);
    renderTopTables(data.topProducts, data.topCustomers);
  } catch (err) {
    console.error("Analytics load failed:", err);
  }
}

function renderKPIs(kpis) {
  const INR = (v) => "₹" + Number(v || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  setText("totalRevenue", INR(kpis.totalRevenue));
  setText("totalOrders", Number(kpis.totalOrders || 0).toLocaleString("en-IN"));
  const aov = kpis.totalOrders ? kpis.avgOrderValue : 0;
  setText("avgOrderValue", INR(aov));
  setText("conversionRate", (Number(kpis.conversionRate || 0)).toFixed(1) + "%");
}

function setText(id, v) {
  const el = document.getElementById(id);
  if (el) el.textContent = v;
}

// ---- Charts ----

function destroyIfExists(key) {
  if (charts[key]) {
    charts[key].destroy();
    charts[key] = null;
  }
}

function renderRevenueChart(rows) {
  const ctx = document.getElementById("revenueChart").getContext("2d");
  const labels = rows.map(r => r.date);
  const data = rows.map(r => Number(r.revenue || 0));
  destroyIfExists("revenue");
  charts.revenue = new Chart(ctx, {
    type: "line",
    data: { labels, datasets: [{ label: "Revenue", data }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: {
        y: { ticks: { callback: v => "₹" + Number(v).toLocaleString("en-IN") } }
      }
    }
  });
  setActiveChartBtn("line");
}

function renderCategoriesChart(rows) {
  const ctx = document.getElementById("categoriesChart").getContext("2d");
  destroyIfExists("categories");
  charts.categories = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: rows.map(r => r.category),
      datasets: [{ label: "Revenue", data: rows.map(r => Number(r.revenue || 0)) }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

function renderRegionChart(rows) {
  const ctx = document.getElementById("regionChart").getContext("2d");
  destroyIfExists("region");
  charts.region = new Chart(ctx, {
    type: "bar",
    data: {
      labels: rows.map(r => r.region),
      datasets: [{ label: "Revenue", data: rows.map(r => Number(r.revenue || 0)) }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      indexAxis: "y",
      scales: { x: { ticks: { callback: v => "₹" + Number(v).toLocaleString("en-IN") } } }
    }
  });
}

function renderHourlyChart(rows) {
  const ctx = document.getElementById("hourlyChart").getContext("2d");
  const canonical = Array.from({ length: 24 }, (_, h) => {
    const row = rows.find(r => Number(r.hour) === h);
    return { hour: h, orders: row ? Number(row.orders || 0) : 0 };
  });
  destroyIfExists("hourly");
  charts.hourly = new Chart(ctx, {
    type: "line",
    data: {
      labels: canonical.map(r => r.hour),
      datasets: [{ label: "Orders", data: canonical.map(r => r.orders) }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

function renderStatusChart(rows) {
  const ctx = document.getElementById("statusChart").getContext("2d");
  destroyIfExists("status");
  charts.status = new Chart(ctx, {
    type: "bar",
    data: {
      labels: rows.map(r => r.status),
      datasets: [{ label: "Orders", data: rows.map(r => Number(r.count || 0)) }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

function changeChartType(key, type) {
  if (key !== "revenue" || !charts.revenue) return;
  const conf = charts.revenue.config;
  const data = conf.data;
  charts.revenue.destroy();
  charts.revenue = new Chart(document.getElementById("revenueChart").getContext("2d"), {
    type: type === "bar" ? "bar" : "line",
    data,
    options: conf.options
  });
  setActiveChartBtn(type);
}

function setActiveChartBtn(type) {
  document.querySelectorAll(".chart-btn").forEach(btn => {
    const is = btn.textContent.trim().toLowerCase() === type;
    btn.classList.toggle("active", is);
  });
}

// ---- Tables ----
function renderTopTables(products, customers) {
  const pBody = document.getElementById("topProductsBody");
  const cBody = document.getElementById("topCustomersBody");

  if (pBody) {
    if (!products?.length) {
      pBody.innerHTML = `<tr><td colspan="4" class="text-center">No data</td></tr>`;
    } else {
      pBody.innerHTML = products.map(p => `
        <tr>
          <td>${escapeHtml(p.product)}</td>
          <td>${Number(p.sales || 0).toLocaleString("en-IN")}</td>
          <td>₹${Number(p.revenue || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
          <td>${p.growth == null ? "-" : (Number(p.growth).toFixed(1) + "%")}</td>
        </tr>
      `).join("");
    }
  }

  if (cBody) {
    if (!customers?.length) {
      cBody.innerHTML = `<tr><td colspan="4" class="text-center">No data</td></tr>`;
    } else {
      cBody.innerHTML = customers.map(c => `
        <tr>
          <td>${escapeHtml(c.customer)}</td>
          <td>${Number(c.orders || 0).toLocaleString("en-IN")}</td>
          <td>₹${Number(c.revenue || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
          <td>₹${Number(c.ltv || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
        </tr>
      `).join("");
    }
  }
}

function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Export button
window.exportReport = function() {
  const days = document.getElementById("dateRangeSelect")?.value || "30";
  window.location.href = `/api/analytics/export?days=${encodeURIComponent(days)}`;
};
