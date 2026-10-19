const form = document.getElementById("patientForm");
const rows = document.getElementById("patientRows");
const toast = document.getElementById("toast");
let toastTimer;

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.className = isError ? "show error" : "show";
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.className = ""; }, 3000);
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[ch]));
}

function statusClass(status) {
  if (status === "In Consultation") return "status-consult";
  if (status === "Completed") return "status-completed";
  return "status-waiting";
}

async function loadPatients() {
  try {
    const patients = await api("/api/patients");
    const waiting = patients.filter(p => p.status === "Waiting");
    const consulting = patients.filter(p => p.status === "In Consultation");
    const completed = patients.filter(p => p.status === "Completed");
    document.getElementById("waitingCount").textContent = waiting.length;
    document.getElementById("consultCount").textContent = consulting.length;
    document.getElementById("completedCount").textContent = completed.length;

    const next = waiting[0];
    document.getElementById("nextPatient").textContent = next ? `Token #${next.token} · ${next.name}` : "No patients waiting";
    document.getElementById("nextDetails").textContent = next ? `${next.department} · Age ${next.age}` : "Register a patient to begin.";
    document.getElementById("callNextButton").disabled = waiting.length === 0;

    if (!patients.length) {
      rows.innerHTML = '<tr><td colspan="5" class="empty-state">No patients yet. Register the first patient to start the queue.</td></tr>';
      return;
    }
    rows.innerHTML = patients.map(p => {
      let action = "—";
      if (p.status === "In Consultation") {
        action = `<button class="small-action" data-complete="${p.id}">Complete visit</button>`;
      } else if (p.status === "Waiting") {
        action = `<button class="small-action" data-remove="${p.id}">Cancel</button>`;
      }
      return `<tr>
        <td class="token">#${p.token}</td>
        <td><div class="patient-name">${escapeHtml(p.name)}</div><div class="patient-age">Age ${p.age}</div></td>
        <td>${escapeHtml(p.department)}</td>
        <td><span class="status ${statusClass(p.status)}">${escapeHtml(p.status)}</span></td>
        <td>${action}</td>
      </tr>`;
    }).join("");
  } catch (error) {
    showToast(error.message, true);
  }
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  const payload = {
    name: document.getElementById("name").value.trim(),
    age: document.getElementById("age").value,
    department: document.getElementById("department").value,
    reason: document.getElementById("reason").value.trim()
  };
  try {
    const result = await api("/api/patients", { method: "POST", body: JSON.stringify(payload) });
    form.reset();
    showToast(`Patient registered. Token number: ${result.token}`);
    await loadPatients();
  } catch (error) {
    showToast(error.message, true);
  }
});

document.getElementById("callNextButton").addEventListener("click", async () => {
  try {
    const result = await api("/api/next", { method: "POST", body: "{}" });
    showToast(`Calling token #${result.patient.token}: ${result.patient.name}`);
    await loadPatients();
  } catch (error) {
    showToast(error.message, true);
  }
});

document.getElementById("refreshButton").addEventListener("click", loadPatients);

rows.addEventListener("click", async event => {
  const completeId = event.target.dataset.complete;
  const removeId = event.target.dataset.remove;
  try {
    if (completeId) {
      const result = await api(`/api/patients/${completeId}/complete`, { method: "POST", body: "{}" });
      showToast(result.message);
      await loadPatients();
    } else if (removeId) {
      const result = await api(`/api/patients/${removeId}/remove`, { method: "POST", body: "{}" });
      showToast(result.message);
      await loadPatients();
    }
  } catch (error) {
    showToast(error.message, true);
  }
});

loadPatients();
