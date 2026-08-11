const state = {
  ramen: [],
  selected: null,
  remaining: 0,
  total: 0,
  timerId: null,
  running: false,
  activeType: "all"
};

const $ = (selector) => document.querySelector(selector);
const formatTime = (seconds) => {
  const s = Math.max(0, Math.ceil(seconds));
  const m = Math.floor(s / 60).toString().padStart(2, "0");
  const sec = (s % 60).toString().padStart(2, "0");
  return `${m}:${sec}`;
};

async function loadRamen() {
  try {
    const response = await fetch(`data/ramen.json?ts=${Date.now()}`);
    if (!response.ok) throw new Error("ramen.json load failed");
    const data = await response.json();

    state.ramen = data.ramen || [];
    render();
    $("#updatedAt").textContent =
      `데이터 업데이트: ${data.updatedAt || "알 수 없음"} · 총 ${state.ramen.length}개`;
  } catch (error) {
    console.error(error);
    $("#popularGrid").innerHTML =
      `<p class="empty">라면 데이터를 불러오지 못했습니다.</p>`;
  }
}

function selectRamen(ramen) {
  stopTimer();
  state.selected = ramen;
  state.total = Number(ramen.cookingTime) || 180;
  state.remaining = state.total;
  $("#timerName").textContent = ramen.name;
  $("#timerType").textContent = `${ramen.type || "라면"} · ${formatTime(state.total)}`;
  $("#timerDisplay").textContent = formatTime(state.remaining);
  $("#timerProgress").style.width = "0%";
  $("#startBtn").disabled = false;
  $("#pauseBtn").disabled = true;
  $("#resetBtn").disabled = false;
  document.querySelector(".timer-panel").scrollIntoView({ behavior: "smooth", block: "center" });
}

function startTimer() {
  if (!state.selected || state.running) return;
  if (state.remaining <= 0) state.remaining = state.total;

  state.running = true;
  $("#startBtn").disabled = true;
  $("#pauseBtn").disabled = false;

  state.timerId = setInterval(() => {
    state.remaining -= 0.1;
    if (state.remaining <= 0) {
      state.remaining = 0;
      finishTimer();
      return;
    }
    updateTimerUI();
  }, 100);
}

function pauseTimer() {
  if (!state.running) return;
  clearInterval(state.timerId);
  state.timerId = null;
  state.running = false;
  $("#startBtn").disabled = false;
  $("#pauseBtn").disabled = true;
}

function stopTimer() {
  clearInterval(state.timerId);
  state.timerId = null;
  state.running = false;
}

function resetTimer() {
  if (!state.selected) return;
  stopTimer();
  state.remaining = state.total;
  updateTimerUI();
  $("#startBtn").disabled = false;
  $("#pauseBtn").disabled = true;
}

function finishTimer() {
  stopTimer();
  updateTimerUI();
  $("#startBtn").disabled = false;
  $("#pauseBtn").disabled = true;
  document.title = "🍜 완성!";
  playBeep();
  setTimeout(() => {
    document.title = "라면 타이머 🍜";
    alert(`${state.selected.name} 완성! 🍜`);
  }, 50);
}

function playBeep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.value = 880;
    gain.gain.value = 0.08;
    osc.start();
    osc.stop(ctx.currentTime + 0.35);
  } catch (_) {}
}

function updateTimerUI() {
  $("#timerDisplay").textContent = formatTime(state.remaining);
  const progress = state.total ? ((state.total - state.remaining) / state.total) * 100 : 0;
  $("#timerProgress").style.width = `${Math.min(100, Math.max(0, progress))}%`;
}

function card(ramen) {
  const button = document.createElement("button");
  button.className = "ramen-card";
  button.innerHTML = `
    <div class="type">${escapeHtml(ramen.type || "라면")}</div>
    <h3>${escapeHtml(ramen.name)}</h3>
    <div class="time">${formatTime(ramen.cookingTime)}</div>
    <div class="brand">${escapeHtml(ramen.brand || "")}</div>
  `;
  button.addEventListener("click", () => selectRamen(ramen));
  return button;
}

function render() {
  const query = $("#searchInput").value.trim().toLowerCase();

  const filtered = state.ramen.filter((r) => {
    const matchesQuery =
      !query ||
      String(r.name).toLowerCase().includes(query) ||
      String(r.brand || "").toLowerCase().includes(query);
    const matchesType =
      state.activeType === "all" || r.type === state.activeType;
    return matchesQuery && matchesType;
  });

  const popular = state.ramen.filter(r => r.popular).slice(0, 8);

  $("#popularGrid").replaceChildren(...popular.map(card));
  $("#ramenGrid").replaceChildren(...filtered.map(card));
  $("#emptyState").classList.toggle("hidden", filtered.length !== 0);
  $("#countText").textContent = `${filtered.length}개`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

$("#startBtn").addEventListener("click", startTimer);
$("#pauseBtn").addEventListener("click", pauseTimer);
$("#resetBtn").addEventListener("click", resetTimer);
$("#searchInput").addEventListener("input", render);

document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    state.activeType = tab.dataset.type;
    render();
  });
});

loadRamen();
