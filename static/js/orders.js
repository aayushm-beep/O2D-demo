let currentPage = 1;
let pageSize = 25;
let totalOrders = 0;
let allOrders = [];

let ALL_COLUMNS = [];
let selectedColumns = [];

// -------- helpers --------
const toTitle = (k) => String(k).replace(/_/g, " ").replace(/\s+/g, " ").trim().replace(/\b\w/g, c => c.toUpperCase());
const isMoneyKey = (k) => /amount|price|cost|fee|duty|tax|total|credit|balance|profit|commission|wholesale|retail|subtotal|vat|rate/i.test(k);
const isDateKey  = (k) => /(date|_at|datetime|time)$/i.test(k);
const isStatusKey = (k) => /status$/i.test(k);
const isPriorityKey = (k) => /priority_level/i.test(k);
const fmtINR = (v) => "₹" + Number(v || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtDate = (v) => { const t = Date.parse(v); return Number.isFinite(t) ? new Date(t).toLocaleDateString("en-IN") : (v ?? "N/A"); };
const esc = (s) => String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;");

// -------- init --------
document.addEventListener("DOMContentLoaded", () => {
  setupSearch();
  wireColumnSelectorButtons();
  loadOrders();
});

function setupSearch() {
  const input = document.getElementById("searchInput");
  if (!input) return;
  let t;
  input.addEventListener("input", () => {
    clearTimeout(t);
    t = setTimeout(() => applyFilters(), 300);
  });
}

function applyFilters(){ currentPage = 1; loadOrders(); }
window.applyFilters = applyFilters;
function clearFilters(){
  ["searchInput","statusFilter","priorityFilter","dateFrom","dateTo"].forEach(id=>{ const el=document.getElementById(id); if(el) el.value=""; });
  applyFilters();
}
window.clearFilters = clearFilters;

// -------- API --------
async function loadOrders() {
  const params = new URLSearchParams({
    page: currentPage,
    page_size: pageSize,
    search: document.getElementById("searchInput")?.value || "",
    status: document.getElementById("statusFilter")?.value || "",
    priority: document.getElementById("priorityFilter")?.value || "",
    date_from: document.getElementById("dateFrom")?.value || "",
    date_to: document.getElementById("dateTo")?.value || "",
  });
  const res = await fetch("/api/orders/data?" + params.toString());
  const data = await res.json();

  allOrders = data.orders || [];
  totalOrders = data.total || 0;

  if (!ALL_COLUMNS.length && allOrders.length) {
    // union of keys across results
    const set = new Set();
    allOrders.forEach(o => Object.keys(o || {}).forEach(k => set.add(k)));
    const keys = Array.from(set).sort((a,b) => (a==="order_id"?-1:b==="order_id"?1:a.localeCompare(b)));
    ALL_COLUMNS = keys.map(k => ({ key: k, label: toTitle(k) }));

    // IMPORTANT: select **all columns** by default
    selectedColumns = ALL_COLUMNS.map(c => c.key);

    renderColumnSelector();
  }

  renderTable();
  renderPagination();
}

function refreshOrders(){ loadOrders(); showToast("Orders refreshed","success"); }
window.refreshOrders = refreshOrders;

// -------- Column selector --------
function renderColumnSelector(){
  const box = document.getElementById("columnCheckboxes");
  if(!box) return;
  const colsPerCol = Math.ceil(ALL_COLUMNS.length / 2);
  const left = ALL_COLUMNS.slice(0, colsPerCol);
  const right = ALL_COLUMNS.slice(colsPerCol);
  const group = (list) => list.map(c => `
    <label class="column-checkbox-label" style="display:flex;align-items:center;gap:.5rem;padding:.2rem 0;">
      <input type="checkbox" value="${esc(c.key)}" ${selectedColumns.includes(c.key)?"checked":""} />
      <span>${esc(c.label)}</span>
    </label>`).join("");
  box.innerHTML = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">${`<div>${group(left)}</div><div>${group(right)}</div>`}</div>`;
  box.querySelectorAll("input[type='checkbox']").forEach(cb=>{
    cb.addEventListener("change", (e)=>{
      const k = e.target.value;
      const i = selectedColumns.indexOf(k);
      if (e.target.checked && i===-1) selectedColumns.push(k);
      if (!e.target.checked && i>-1) selectedColumns.splice(i,1);
      updateSelectedCount();
    });
  });
  updateSelectedCount();
}

function updateSelectedCount(){
  const el = document.getElementById("selectedCount");
  if (el) el.textContent = `Selected ${selectedColumns.length} / ${ALL_COLUMNS.length}`;
}

function wireColumnSelectorButtons(){
  window.toggleColumnSelector = function(){
    const d = document.getElementById("columnSelector");
    if(!d) return;
    d.style.display = d.style.display === "none" ? "block" : "none";
  };
  window.selectAllColumns = function(){
    selectedColumns = ALL_COLUMNS.map(c=>c.key);
    document.querySelectorAll("#columnCheckboxes input[type='checkbox']").forEach(cb=>cb.checked=true);
    updateSelectedCount();
  };
  window.deselectAllColumns = function(){
    selectedColumns = [];
    document.querySelectorAll("#columnCheckboxes input[type='checkbox']").forEach(cb=>cb.checked=false);
    updateSelectedCount();
  };
  window.applyColumnSelection = function(){
    renderTable();
    toggleColumnSelector();
    showToast("Column selection applied","success");
  };
}

// -------- Rendering --------
function renderTable(){
  const thead = document.getElementById("ordersTableHead");
  const tbody = document.getElementById("ordersTableBody");
  if (!thead || !tbody) return;

  const visible = ALL_COLUMNS.filter(c => selectedColumns.includes(c.key));

  // header
  const htr = document.createElement("tr");
  visible.forEach(c=>{
    const th = document.createElement("th");
    th.textContent = c.label;
    htr.appendChild(th);
  });
  const thAct = document.createElement("th");
  thAct.textContent = "Actions";
  thAct.style.textAlign = "center";
  htr.appendChild(thAct);
  thead.innerHTML = "";
  thead.appendChild(htr);

  // body
  tbody.innerHTML = "";
  if (!allOrders.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = visible.length + 1;
    td.className = "text-center";
    td.innerHTML = `<p style="padding:1rem;color:#6b7280;">No orders found</p>`;
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  allOrders.forEach(order=>{
    const tr = document.createElement("tr");
    visible.forEach(col=>{
      const k = col.key;
      const v = order[k];
      const td = document.createElement("td");

      if (isStatusKey(k)) {
        td.innerHTML = `<span class="status-badge status-${String(v||"pending").toLowerCase()}">${esc(v||"N/A")}</span>`;
      } else if (isPriorityKey(k)) {
        td.innerHTML = `<span class="priority-badge priority-${String(v||"medium").toLowerCase()}">${esc(v||"N/A")}</span>`;
      } else if (isMoneyKey(k)) {
        td.textContent = fmtINR(v);
      } else if (isDateKey(k)) {
        td.textContent = fmtDate(v);
      } else if (typeof v === "boolean") {
        td.textContent = v ? "Yes" : "No";
      } else if (v === null || typeof v === "undefined" || v === "") {
        td.textContent = "N/A";
      } else {
        td.textContent = String(v);
      }
      tr.appendChild(td);
    });

    const act = document.createElement("td");
    act.style.textAlign = "center";
    act.innerHTML = `<button class="btn btn-sm btn-primary" onclick="viewOrder('${esc(order.order_id)}')" title="View"><i class="fas fa-eye"></i></button>`;
    tr.appendChild(act);

    tbody.appendChild(tr);
  });
}

function renderPagination(){
  const totalPages = Math.max(1, Math.ceil(totalOrders / pageSize));
  const info = document.getElementById("paginationInfo");
  const wrap = document.getElementById("pageNumbers");
  if (!info || !wrap) return;

  const start = totalOrders ? (currentPage-1)*pageSize + 1 : 0;
  const end = Math.min(currentPage*pageSize, totalOrders);
  info.textContent = `Showing ${start}-${end} of ${totalOrders} orders`;

  wrap.innerHTML = "";
  const maxPages = 5;
  let sp = Math.max(1, currentPage - Math.floor(maxPages/2));
  let ep = Math.min(totalPages, sp + maxPages - 1);
  if (ep - sp < maxPages - 1) sp = Math.max(1, ep - maxPages + 1);
  for (let i=sp; i<=ep; i++){
    const b = document.createElement("button");
    b.textContent = i;
    b.className = i === currentPage ? "active" : "";
    b.onclick = ()=>{ currentPage = i; loadOrders(); };
    wrap.appendChild(b);
  }
  const prev = document.getElementById("prevBtn");
  const next = document.getElementById("nextBtn");
  if (prev) prev.disabled = currentPage === 1;
  if (next) next.disabled = currentPage === totalPages;
}

function changePageSize(){
  const s = document.getElementById("pageSizeSelect");
  pageSize = parseInt(s.value, 10) || 25;
  currentPage = 1;
  loadOrders();
}
window.changePageSize = changePageSize;
function previousPage(){ if(currentPage>1){ currentPage--; loadOrders(); } }
function nextPage(){ const totalPages = Math.ceil(totalOrders/pageSize); if(currentPage<totalPages){ currentPage++; loadOrders(); } }
window.previousPage = previousPage;
window.nextPage = nextPage;

// modal (kept simple)
function viewOrder(orderId){
  const order = allOrders.find(o => String(o.order_id) === String(orderId));
  if (!order) return;
  const modal = document.getElementById("orderModal");
  const body = document.getElementById("orderDetailsContent");
  const rows = Object.keys(order).sort().map(k => `
    <div class="detail-row">
      <div class="detail-label">${esc(toTitle(k))}</div>
      <div class="detail-value">${esc(order[k] ?? "N/A")}</div>
    </div>
  `).join("");
  body.innerHTML = `<div class="detail-section"><h3><i class="fas fa-info-circle"></i> All Fields</h3><div class="detail-grid">${rows}</div></div>`;
  modal.style.display = "block";
}
window.viewOrder = viewOrder;
function closeOrderModal(){ const m = document.getElementById("orderModal"); if(m) m.style.display="none"; }
window.closeOrderModal = closeOrderModal;
window.onclick = function(ev){ const m=document.getElementById("orderModal"); if(ev.target===m) closeOrderModal(); };

// export + toast
function exportOrders(){
  const params = new URLSearchParams({
    search: document.getElementById("searchInput")?.value || "",
    status: document.getElementById("statusFilter")?.value || "",
    priority: document.getElementById("priorityFilter")?.value || ""
  });
  window.location.href = "/api/export/csv?" + params.toString();
  showToast("Export started","success");
}
window.exportOrders = exportOrders;

function showToast(msg, type){ if (typeof window.showToast==="function") window.showToast(msg,type); else console.log(type||"info", msg); }
