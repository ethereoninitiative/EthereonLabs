
(function () {
  "use strict";

  var STORAGE_KEY = "lumina.harbor.first_loop.r1";
  var state = loadState();

  function now() {
    return new Date().toISOString();
  }

  function id(prefix) {
    return prefix + "-" + Math.random().toString(36).slice(2, 9) + "-" + Date.now().toString(36);
  }

  function byId(value) {
    return document.getElementById(value);
  }

  function all(selector) {
    return Array.prototype.slice.call(document.querySelectorAll(selector));
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function emptyState() {
    return {
      schema_version: "lumina-harbor-local-first-r1",
      created_at: now(),
      updated_at: now(),
      humans: [],
      intelligences: [],
      projects: [],
      current_project_id: null,
      last_return_at: null
    };
  }

  function loadState() {
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : emptyState();
    } catch (error) {
      return emptyState();
    }
  }

  function persist() {
    state.updated_at = now();
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      return true;
    } catch (error) {
      setStatus("Local storage unavailable");
      toast("The browser could not persist this local record.");
      return false;
    }
  }

  function setStatus(label) {
    var target = document.querySelector("[data-local-status]");
    if (target) target.textContent = label;
  }

  function toast(message) {
    var current = byId("toast");
    if (current) current.remove();
    var notice = document.createElement("div");
    notice.id = "toast";
    notice.className = "toast";
    notice.setAttribute("role", "status");
    notice.textContent = message;
    document.body.appendChild(notice);
    window.setTimeout(function () {
      if (notice.parentNode) notice.remove();
    }, 3400);
  }

  function showScreen(screenId) {
    all(".screen").forEach(function (screen) {
      screen.classList.toggle("hidden", screen.id !== screenId);
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function setStep(step) {
    all("[data-step]").forEach(function (item) {
      var number = Number(item.getAttribute("data-step"));
      item.classList.toggle("active", number === step);
      item.classList.toggle("done", number < step);
    });
  }

  function setSetupMode(mode) {
    var title = byId("setup-title");
    var copy = byId("setup-copy");
    var humanForm = byId("human-form");
    var intelligenceForm = byId("intelligence-form");
    var projectForm = byId("project-form");

    humanForm.classList.add("hidden");
    intelligenceForm.classList.add("hidden");
    projectForm.classList.add("hidden");

    if (mode === "human") {
      title.textContent = state.humans.length ? "Add a human navigator" : "Begin human orientation";
      copy.textContent = state.humans.length
        ? "A second human can join this local crew. This creates a participant record only; it does not invite or authenticate anyone."
        : "Lumina begins with the human because intention, consent, and authority must have a visible source.";
      humanForm.classList.remove("hidden");
      setStep(1);
    } else if (mode === "intelligence") {
      title.textContent = "Establish an intelligence passport";
      copy.textContent = "Record the intelligence you intend to bring into this harbor. Provider and model are descriptive labels here—not credentials, authentication, or a live connection.";
      intelligenceForm.classList.remove("hidden");
      setStep(2);
    } else {
      title.textContent = "Plant the first project";
      copy.textContent = "A habitat becomes meaningful when there is something shared to return to. Give the voyage a working name and a first intention.";
      projectForm.classList.remove("hidden");
      setStep(3);
    }
    showScreen("setup-screen");
  }

  function startFirstLoop() {
    setSetupMode("human");
    byId("human-name").focus();
  }

  function continueToIntelligence() {
    setSetupMode("intelligence");
    byId("intelligence-name").focus();
  }

  function continueToProject() {
    setSetupMode("project");
    byId("project-title").focus();
  }

  function humanName() {
    var first = state.humans[0];
    return first ? first.name : "Navigator";
  }

  function renderDashboard() {
    var primary = byId("primary-human");
    var returnMessage = byId("return-message");
    var crew = byId("crew-list");
    var projects = byId("project-list");
    var projectCount = byId("project-count");
    var intelligenceCount = byId("intelligence-count");
    var humanCount = byId("human-count");
    var lastReturn = byId("last-return");
    var project = state.projects.find(function (item) { return item.id === state.current_project_id; });

    primary.textContent = humanName();
    returnMessage.textContent = project
      ? "Welcome back, " + humanName() + ". " + project.title + " is waiting at the point where you left it."
      : "Welcome back, " + humanName() + ". The harbor is ready for its first shared project.";
    projectCount.textContent = String(state.projects.length);
    intelligenceCount.textContent = String(state.intelligences.length);
    humanCount.textContent = String(state.humans.length);
    lastReturn.textContent = state.last_return_at
      ? "Last local return: " + new Date(state.last_return_at).toLocaleString()
      : "This is the first local return.";

    if (!state.humans.length && !state.intelligences.length) {
      crew.innerHTML = '<p class="empty">No crew records yet.</p>';
    } else {
      var humanItems = state.humans.map(function (item) {
        return '<div class="list-item"><strong>' + escapeHtml(item.name) + '</strong><span>Human navigator · ' + escapeHtml(item.role) + '</span></div>';
      });
      var intelligenceItems = state.intelligences.map(function (item) {
        return '<div class="list-item"><strong>' + escapeHtml(item.name) + '</strong><span>Intelligence passport draft · ' + escapeHtml(item.provider) + " / " + escapeHtml(item.model) + '</span></div>';
      });
      crew.innerHTML = humanItems.concat(intelligenceItems).join("");
    }

    if (!state.projects.length) {
      projects.innerHTML = '<p class="empty">No project has been planted yet.</p>';
    } else {
      projects.innerHTML = state.projects.map(function (item) {
        var active = item.id === state.current_project_id ? " · current" : "";
        return '<div class="list-item"><strong>' + escapeHtml(item.title) + '</strong><span>' + escapeHtml(item.purpose) + " · " + escapeHtml(item.status) + active + '</span></div>';
      }).join("");
    }

    showScreen("harbor-screen");
  }

  function enterHarbor() {
    state.last_return_at = now();
    persist();
    renderDashboard();
    setStatus("Local harbor active");
  }

  function exportState() {
    var payload = JSON.stringify(state, null, 2);
    var blob = new Blob([payload], { type: "application/json" });
    var link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "lumina-harbor-local-record-r1.json";
    link.click();
    URL.revokeObjectURL(link.href);
    toast("Exported the local Harbor record.");
  }

  function resetHarbor() {
    if (!window.confirm("Erase this browser's local Harbor record? This cannot affect GitHub, a provider, or any remote account.")) return;
    window.localStorage.removeItem(STORAGE_KEY);
    state = emptyState();
    setStatus("Local prototype");
    showScreen("welcome-screen");
    toast("Local Harbor record erased.");
  }

  function onHumanSubmit(event) {
    event.preventDefault();
    var name = byId("human-name").value.trim();
    var role = byId("human-role").value.trim() || "navigator";
    if (!name) return;
    state.humans.push({
      id: id("human"),
      type: "human",
      name: name,
      role: role,
      created_at: now()
    });
    persist();
    byId("human-form").reset();
    if (state.projects.length || state.intelligences.length) {
      enterHarbor();
    } else {
      continueToIntelligence();
    }
  }

  function onIntelligenceSubmit(event) {
    event.preventDefault();
    var name = byId("intelligence-name").value.trim();
    var provider = byId("intelligence-provider").value.trim();
    var model = byId("intelligence-model").value.trim();
    var relationship = byId("intelligence-relationship").value.trim() || "crew intelligence";
    if (!name || !provider || !model) return;
    state.intelligences.push({
      id: id("intelligence"),
      type: "intelligence",
      name: name,
      provider: provider,
      model: model,
      relationship: relationship,
      status: "draft-passport",
      authority_granted: false,
      created_at: now()
    });
    persist();
    byId("intelligence-form").reset();
    if (state.projects.length) {
      enterHarbor();
    } else {
      continueToProject();
    }
  }

  function onProjectSubmit(event) {
    event.preventDefault();
    var title = byId("project-title").value.trim();
    var purpose = byId("project-purpose").value.trim();
    if (!title || !purpose) return;
    var project = {
      id: id("project"),
      type: "project",
      title: title,
      purpose: purpose,
      status: "active-local",
      human_ids: state.humans.map(function (item) { return item.id; }),
      intelligence_ids: state.intelligences.map(function (item) { return item.id; }),
      created_at: now()
    };
    state.projects.push(project);
    state.current_project_id = project.id;
    persist();
    byId("project-form").reset();
    enterHarbor();
    toast("First local project planted.");
  }

  document.addEventListener("click", function (event) {
    var action = event.target.closest("[data-action]");
    if (!action) return;
    var name = action.getAttribute("data-action");
    if (name === "begin") startFirstLoop();
    if (name === "return") enterHarbor();
    if (name === "add-human") setSetupMode("human");
    if (name === "add-intelligence") setSetupMode("intelligence");
    if (name === "new-project") setSetupMode("project");
    if (name === "export") exportState();
    if (name === "reset") resetHarbor();
    if (name === "welcome") showScreen("welcome-screen");
  });

  byId("human-form").addEventListener("submit", onHumanSubmit);
  byId("intelligence-form").addEventListener("submit", onIntelligenceSubmit);
  byId("project-form").addEventListener("submit", onProjectSubmit);

  if (state.humans.length || state.intelligences.length || state.projects.length) {
    byId("return-button").classList.remove("hidden");
  }

  setStatus(state.humans.length || state.intelligences.length ? "Local record found" : "Local prototype");
}());
