(function () {
  "use strict";

  var DEFAULT_ENDPOINT = "http://127.0.0.1:8766/api/bridge";
  var bridgeState = {
    status: "disconnected",
    endpoint: DEFAULT_ENDPOINT,
    data: null,
    error: null,
    fetched_at: null
  };

  function byId(value) {
    return document.getElementById(value);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function valueAt(object, path, fallback) {
    var current = object;
    path.split(".").forEach(function (part) {
      if (current && typeof current === "object") current = current[part];
      else current = undefined;
    });
    return current == null || current === "" ? (fallback || "not reported") : current;
  }

  function localEndpoint(raw) {
    var url;
    try {
      url = new URL(raw || DEFAULT_ENDPOINT);
    } catch (error) {
      throw new Error("Bridge endpoint is not a valid URL.");
    }
    var localHosts = ["localhost", "127.0.0.1", "::1", "[::1]"];
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      throw new Error("Bridge endpoint must use HTTP or HTTPS.");
    }
    if (localHosts.indexOf(url.hostname) === -1) {
      throw new Error("For safety, Harbor only connects to a local Bridge host.");
    }
    if (url.username || url.password || url.search || url.hash) {
      throw new Error("Bridge endpoint may not contain credentials or query state.");
    }
    if (url.pathname !== "/api/bridge") {
      throw new Error("Bridge endpoint must end with /api/bridge.");
    }
    return url;
  }

  function showHarbor() {
    var returnButton = document.querySelector('[data-action="return"]');
    if (returnButton) returnButton.click();
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
    }, 4200);
  }

  function item(label, value, className) {
    return '<div class="list-item"><strong>' + escapeHtml(label) + '</strong><span class="' + (className || "") + '">' + escapeHtml(value) + '</span></div>';
  }

  function render() {
    var status = byId("bridge-status");
    var summary = byId("bridge-summary");
    var witness = byId("bridge-witness");
    if (!status || !summary || !witness) return;

    status.textContent = bridgeState.status === "connected" ? "connected" : bridgeState.status;
    status.className = "pill " + (bridgeState.status === "connected" ? "pill-good" : "pill-muted");

    if (bridgeState.status === "connecting") {
      summary.textContent = "Requesting one read-only observation from the local Bridge.";
      witness.innerHTML = '<p class="empty">Reading local runtime truth…</p>';
      return;
    }

    if (bridgeState.status !== "connected" || !bridgeState.data) {
      summary.textContent = bridgeState.error || "No local Bridge is connected. Harbor remains fully usable in browser-local mode.";
      witness.innerHTML = [
        item("Endpoint", bridgeState.endpoint),
        item("Request", "GET /api/bridge only"),
        item("Authority", "observation only; no mutation")
      ].join("");
      return;
    }

    var data = bridgeState.data;
    var alignment = data.runtime_truth_alignment || {};
    var authority = data.authority || {};
    var committed = authority.committed || {};
    var governance = committed.governance_chain || {};
    var canon = committed.canon_lineage || {};
    var fields = [
      ["Project", valueAt(data, "workspace.project.name", valueAt(data, "workspace.project.slug"))],
      ["Harbor session", valueAt(data, "workspace.harbor_session.title", valueAt(data, "workspace.harbor_session.session_id"))],
      ["Current mode", valueAt(data, "runtime_witness.current_mode")],
      ["Runtime status", valueAt(data, "runtime_witness.status")],
      ["Latest action", valueAt(data, "runtime_witness.requested_action")],
      ["Truth alignment", alignment.aligned ? "aligned" : "not aligned / inspect"],
      ["Governance", valueAt(governance, "status")],
      ["Canon head", valueAt(canon, "current_head")],
      ["Observed at", bridgeState.fetched_at]
    ];
    witness.innerHTML = fields.map(function (entry) {
      var cls = entry[0] === "Truth alignment" && entry[1] === "aligned" ? "good" : "";
      return item(entry[0], entry[1], cls);
    }).join("");
    summary.textContent = "Connected to the local read-only Bridge. This is an observation of Lumina state, not a new authority source.";
  }

  async function connect() {
    var input = byId("bridge-endpoint");
    var endpoint;
    try {
      endpoint = localEndpoint(input ? input.value.trim() : DEFAULT_ENDPOINT);
    } catch (error) {
      bridgeState.status = "rejected";
      bridgeState.error = error.message;
      render();
      toast(error.message);
      return;
    }

    showHarbor();
    bridgeState.status = "connecting";
    bridgeState.endpoint = endpoint.href;
    bridgeState.error = null;
    bridgeState.data = null;
    render();
    setStatus("Reading local Bridge");

    var controller = new AbortController();
    var timeout = window.setTimeout(function () { controller.abort(); }, 6000);
    try {
      var response = await fetch(endpoint.href, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store",
        credentials: "omit",
        signal: controller.signal
      });
      if (!response.ok) throw new Error("Bridge returned HTTP " + response.status + ".");
      var data = await response.json();
      bridgeState.status = "connected";
      bridgeState.data = data;
      bridgeState.fetched_at = new Date().toISOString();
      setStatus("Local Bridge connected");
      toast("Local Lumina observation received.");
    } catch (error) {
      bridgeState.status = "disconnected";
      bridgeState.error = error.name === "AbortError"
        ? "The local Bridge did not answer within six seconds."
        : "Local Bridge unavailable. Start Lumina Bridge, then try again.";
      setStatus("Local prototype");
      toast(bridgeState.error);
    } finally {
      window.clearTimeout(timeout);
      render();
    }
  }

  document.addEventListener("click", function (event) {
    var action = event.target.closest("[data-action]");
    if (!action) return;
    var name = action.getAttribute("data-action");
    if (name === "connect-bridge" || name === "refresh-bridge") connect();
  });

  var input = byId("bridge-endpoint");
  if (input) input.value = DEFAULT_ENDPOINT;
  render();
}());
