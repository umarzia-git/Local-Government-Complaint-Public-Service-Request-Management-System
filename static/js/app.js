const state = {
  activePortal: "citizen",
  staffStatus: "All",
  staffDept: "All",
  query: "",
  categories: [],
  citizens: [],
  departments: [],
  complaints: [],
  dashboard: null,
};

const portalCopy = {
  citizen: {
    eyebrow: "Citizen Portal",
    title: "File and Track Requests",
  },
  staff: {
    eyebrow: "Staff Portal",
    title: "Resolve Assigned Complaints",
  },
  admin: {
    eyebrow: "Admin Portal",
    title: "Monitor City Performance",
  },
};

const formatNumber = new Intl.NumberFormat("en");
const dateFormatter = new Intl.DateTimeFormat("en", {
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

const qs = (selector) => document.querySelector(selector);
const qsa = (selector) => Array.from(document.querySelectorAll(selector));

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => {
    const map = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return map[char];
  });
}

function statusClass(status) {
  return String(status || "")
    .toLowerCase()
    .replace("in ", "")
    .replace(/\s+/g, "-");
}

function priorityClass(priority) {
  return String(priority || "normal").toLowerCase();
}

function toDate(value) {
  if (!value) return null;
  return new Date(String(value).replace(" ", "T"));
}

function formatDate(value) {
  const parsed = toDate(value);
  if (!parsed || Number.isNaN(parsed.getTime())) return "-";
  return dateFormatter.format(parsed);
}

function isBreached(row) {
  const deadline = toDate(row.sla_deadline);
  return deadline && deadline < new Date() && !["Resolved", "Closed"].includes(row.status);
}

function matchesSearch(row) {
  if (!state.query) return true;
  const needle = state.query.toLowerCase();
  return [
    row.token,
    row.citizen_name,
    row.category_name,
    row.dept_name,
    row.ward_no,
    row.status,
  ]
    .join(" ")
    .toLowerCase()
    .includes(needle);
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

function setSource(source, detail = "") {
  qs("#sourceLabel").textContent = source === "mysql" ? "MySQL Live" : "Demo Mode";
  qs("#sourceDetail").textContent =
    source === "mysql" ? detail || "Connected to lgc_system" : "Using built-in preview data";
}

function setPortal(portal) {
  state.activePortal = portal;
  qsa(".portal-nav button").forEach((button) => {
    button.classList.toggle("active", button.dataset.portalTarget === portal);
  });
  qsa(".portal").forEach((section) => {
    section.classList.toggle("active", section.dataset.portal === portal);
  });
  qs("#portalEyebrow").textContent = portalCopy[portal].eyebrow;
  qs("#portalTitle").textContent = portalCopy[portal].title;
}

function renderMetrics(stats) {
  qs("#totalComplaints").textContent = formatNumber.format(stats.total_complaints || 0);
  qs("#openComplaints").textContent = formatNumber.format(stats.open_complaints || 0);
  qs("#slaBreaches").textContent = formatNumber.format(stats.sla_breaches || 0);
  qs("#avgRating").textContent = stats.avg_rating ? Number(stats.avg_rating).toFixed(1) : "N/A";
}

function staffRows() {
  return state.complaints.filter((row) => {
    const deptMatch = state.staffDept === "All" || String(row.dept_id) === state.staffDept;
    const statusMatch = state.staffStatus === "All" || row.status === state.staffStatus;
    return deptMatch && statusMatch && matchesSearch(row);
  });
}

function renderStaffMetrics() {
  const departmentRows = state.complaints.filter((row) => {
    return state.staffDept === "All" || String(row.dept_id) === state.staffDept;
  });
  const assigned = departmentRows.filter((row) => !["Resolved", "Closed"].includes(row.status));
  const breaches = departmentRows.filter(isBreached);
  const resolved = departmentRows.filter((row) => ["Resolved", "Closed"].includes(row.status));

  qs("#staffAssigned").textContent = formatNumber.format(assigned.length);
  qs("#staffBreaches").textContent = formatNumber.format(breaches.length);
  qs("#staffResolved").textContent = formatNumber.format(resolved.length);
}

function renderComplaints(rows) {
  const body = qs("#complaintsBody");
  body.innerHTML = "";
  if (!rows.length) {
    body.innerHTML = `<tr><td colspan="7"><div class="empty-state">No complaints match this view.</div></td></tr>`;
    return;
  }

  const template = qs("#statusActionTemplate");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const breach = isBreached(row);
    const priority = row.priority
      ? `<span class="pill ${priorityClass(row.priority)}">${escapeHtml(row.priority)}</span>`
      : "";
    tr.innerHTML = `
      <td>
        <span class="token">${escapeHtml(row.token)}</span>
        <span class="subtle">${priority}</span>
      </td>
      <td>
        <strong>${escapeHtml(row.citizen_name)}</strong>
        <span class="subtle">${escapeHtml(row.citizen_phone || "")}</span>
      </td>
      <td>
        <strong>${escapeHtml(row.category_name)}</strong>
        <span class="subtle">${escapeHtml(row.dept_name)}</span>
      </td>
      <td>${escapeHtml(row.ward_no)}</td>
      <td><span class="pill ${statusClass(row.status)}">${escapeHtml(row.status)}</span></td>
      <td>
        ${formatDate(row.sla_deadline)}
        ${breach ? `<span class="subtle"><span class="pill breach">Breach</span></span>` : ""}
      </td>
      <td></td>
    `;

    const action = template.content.firstElementChild.cloneNode(true);
    const select = action.querySelector("select");
    const button = action.querySelector("button");
    select.value = row.status;
    button.addEventListener("click", async () => {
      button.disabled = true;
      button.textContent = "Saving";
      try {
        await fetchJson(`/api/complaints/${row.complaint_id}/status`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            status: select.value,
            note: `Updated from ${row.status} to ${select.value}`,
          }),
        });
        await loadAll();
      } catch (error) {
        window.alert(error.message);
      } finally {
        button.disabled = false;
        button.textContent = "Update";
      }
    });
    tr.lastElementChild.appendChild(action);
    body.appendChild(tr);
  });
}

function requestProgress(status) {
  const steps = ["Received", "In Progress", "Resolved", "Closed"];
  const activeIndex = Math.max(0, steps.indexOf(status));
  return steps
    .map((step, index) => {
      const className = index <= activeIndex ? "done" : "";
      return `<span class="${className}">${step}</span>`;
    })
    .join("");
}

function renderCitizenRequests() {
  const root = qs("#citizenRequests");
  const selectedCitizen = qs("#citizenTrackSelect").value;
  const rows = state.complaints
    .filter((row) => String(row.citizen_id) === selectedCitizen && matchesSearch(row))
    .sort((a, b) => toDate(b.filed_at) - toDate(a.filed_at));

  root.innerHTML = "";
  if (!rows.length) {
    root.innerHTML = `<div class="empty-state">No requests found for this citizen.</div>`;
    return;
  }

  rows.forEach((row) => {
    const card = document.createElement("article");
    card.className = "request-card";
    card.innerHTML = `
      <div class="request-top">
        <div>
          <strong>${escapeHtml(row.token)}</strong>
          <span class="subtle">${escapeHtml(row.category_name)} · ${escapeHtml(row.dept_name)}</span>
        </div>
        <span class="pill ${statusClass(row.status)}">${escapeHtml(row.status)}</span>
      </div>
      <p>${escapeHtml(row.description)}</p>
      <div class="request-meta">
        <span>${escapeHtml(row.ward_no)}</span>
        <span>Filed ${formatDate(row.filed_at)}</span>
        <span>Deadline ${formatDate(row.sla_deadline)}</span>
      </div>
      <div class="progress-rail">${requestProgress(row.status)}</div>
      ${row.feedback_pending ? `<span class="pill high">Feedback Pending</span>` : ""}
    `;
    root.appendChild(card);
  });
}

function renderDepartmentKpi(rows) {
  const root = qs("#departmentKpi");
  root.innerHTML = "";
  rows.forEach((row) => {
    const pct = Number(row.on_time_pct || 0);
    const item = document.createElement("article");
    item.className = "kpi-row";
    item.innerHTML = `
      <div class="kpi-top">
        <strong>${escapeHtml(row.dept_name)}</strong>
        <span class="pill">${pct.toFixed(0)}% on time</span>
      </div>
      <div class="bar" aria-hidden="true"><span style="width: ${Math.min(pct, 100)}%"></span></div>
      <span class="subtle">${row.total_resolved || 0} resolved · ${row.total_feedback || 0} ratings · ${row.avg_rating || "N/A"} avg</span>
    `;
    root.appendChild(item);
  });
}

function renderHeatmap(rows) {
  const root = qs("#wardHeatmap");
  root.innerHTML = "";
  rows.slice(0, 8).forEach((row) => {
    const risk = Number(row.risk_score || 0);
    const width = Math.min(Math.max(risk * 18, 8), 100);
    const item = document.createElement("article");
    item.className = "ward-tile";
    item.innerHTML = `
      <strong>${escapeHtml(row.ward_no)}</strong>
      <small>${row.open_complaints || 0} open · ${row.sla_breaches || 0} SLA breaches</small>
      <div class="risk-meter" aria-hidden="true"><span style="width: ${width}%"></span></div>
      <small>Risk ${risk.toFixed(2)} · Satisfaction ${Number(row.avg_satisfaction || 0).toFixed(1)}</small>
    `;
    root.appendChild(item);
  });
}

function renderChronicIssues(rows) {
  const root = qs("#chronicIssues");
  root.innerHTML = "";
  if (!rows.length) {
    root.innerHTML = `<div class="empty-state">No recurring issues are active.</div>`;
    return;
  }
  rows.forEach((row) => {
    const item = document.createElement("article");
    item.className = "issue-row";
    item.innerHTML = `
      <div class="issue-top">
        <strong>${escapeHtml(row.category_name)}</strong>
        <span class="pill ${row.is_resolved ? "resolved" : "critical"}">${row.is_resolved ? "Resolved" : "Active"}</span>
      </div>
      <span class="subtle">${escapeHtml(row.ward_no)} · ${row.complaint_count} related complaints · ${formatDate(row.detected_at)}</span>
      ${row.resolution_note ? `<span class="subtle">${escapeHtml(row.resolution_note)}</span>` : ""}
    `;
    root.appendChild(item);
  });
}

function populateSelects() {
  const citizenOptions = state.citizens
    .map((citizen) => `<option value="${citizen.citizen_id}" data-ward="${escapeHtml(citizen.ward_no)}">${escapeHtml(citizen.full_name)} · ${escapeHtml(citizen.ward_no)}</option>`)
    .join("");
  qs("#citizenSelect").innerHTML = citizenOptions;
  qs("#citizenTrackSelect").innerHTML = citizenOptions;

  qs("#categorySelect").innerHTML = state.categories
    .map((category) => `<option value="${category.category_id}">${escapeHtml(category.category_name)} · ${escapeHtml(category.dept_name)}</option>`)
    .join("");

  qs("#staffDeptSelect").innerHTML = [
    `<option value="All">All departments</option>`,
    ...state.departments.map((department) => `<option value="${department.dept_id}">${escapeHtml(department.dept_name)}</option>`),
  ].join("");

  const firstCitizen = state.citizens[0];
  if (firstCitizen) qs("#wardInput").value = firstCitizen.ward_no;
}

async function loadLookups() {
  const [categories, citizens, departments] = await Promise.all([
    fetchJson("/api/categories"),
    fetchJson("/api/citizens"),
    fetchJson("/api/departments"),
  ]);
  state.categories = categories.categories;
  state.citizens = citizens.citizens;
  state.departments = departments.departments;
  populateSelects();
}

function renderAll() {
  if (!state.dashboard) return;
  renderMetrics(state.dashboard.stats);
  renderStaffMetrics();
  renderComplaints(staffRows());
  renderCitizenRequests();
  renderDepartmentKpi(state.dashboard.department_kpi);
  renderHeatmap(state.dashboard.ward_heatmap);
  renderChronicIssues(state.dashboard.chronic_issues);
}

async function loadAll() {
  const query = new URLSearchParams();
  if (state.query) query.set("q", state.query);
  const [dashboard, complaints] = await Promise.all([
    fetchJson("/api/dashboard"),
    fetchJson(`/api/complaints?${query.toString()}`),
  ]);

  state.dashboard = dashboard;
  state.complaints = complaints.complaints;
  setSource(dashboard.source);
  renderAll();
}

function bindEvents() {
  qs("#refreshButton").addEventListener("click", loadAll);
  qs("#searchInput").addEventListener("input", (event) => {
    state.query = event.target.value.trim();
    window.clearTimeout(window.searchTimer);
    window.searchTimer = window.setTimeout(loadAll, 220);
  });

  qsa(".portal-nav button").forEach((button) => {
    button.addEventListener("click", () => {
      setPortal(button.dataset.portalTarget);
      renderAll();
    });
  });

  qsa(".segmented button").forEach((button) => {
    button.addEventListener("click", () => {
      qsa(".segmented button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      state.staffStatus = button.dataset.status;
      renderAll();
    });
  });

  qs("#staffDeptSelect").addEventListener("change", (event) => {
    state.staffDept = event.target.value;
    renderAll();
  });

  qs("#citizenTrackSelect").addEventListener("change", renderCitizenRequests);

  qs("#citizenSelect").addEventListener("change", (event) => {
    const ward = event.target.selectedOptions[0]?.dataset.ward;
    if (ward) qs("#wardInput").value = ward;
    qs("#citizenTrackSelect").value = event.target.value;
    renderCitizenRequests();
  });

  qs("#intake").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const message = qs("#formMessage");
    const submit = form.querySelector("button[type='submit']");
    const payload = Object.fromEntries(new FormData(form).entries());
    message.textContent = "";
    message.classList.remove("error");
    submit.disabled = true;
    submit.textContent = "Submitting";
    try {
      const created = await fetchJson("/api/complaints", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      message.textContent = `${created.token} submitted successfully.`;
      form.querySelector("textarea").value = "";
      qs("#citizenTrackSelect").value = payload.citizen_id;
      await loadAll();
    } catch (error) {
      message.textContent = error.message;
      message.classList.add("error");
    } finally {
      submit.disabled = false;
      submit.textContent = "Submit Request";
    }
  });
}

async function boot() {
  bindEvents();
  try {
    const health = await fetchJson("/api/health");
    setSource(health.source, health.detail);
    await loadLookups();
    await loadAll();
  } catch (error) {
    qs("#sourceLabel").textContent = "Backend Offline";
    qs("#sourceDetail").textContent = error.message;
  }
}

boot();
