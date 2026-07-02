(function () {
  const root = document.querySelector("[data-system-monitor]");
  if (!root) return;

  const els = {
    api: document.getElementById("monitorApi"),
    apiDot: document.getElementById("monitorApiDot"),
    scale: document.getElementById("monitorScale"),
    weight: document.getElementById("monitorWeight"),
    nfc: document.getElementById("monitorNfc"),
    spool: document.getElementById("monitorSpool"),
  };

  function setClass(el, className) {
    el.classList.remove("good", "warn", "bad");
    el.classList.add(className);
  }

  async function refreshMonitor() {
    try {
      const response = await fetch("/status", { cache: "no-store" });
      if (!response.ok) throw new Error("Status request failed");

      const data = await response.json();

      const scale = data.scale || {};
      const nfc = data.nfc || {};
      const spool = data.spool || data.currentSpool || null;

      els.api.textContent = "Online";
      setClass(els.api, "good");
      setClass(els.apiDot, "good");

      els.scale.textContent = scale.connected
        ? (scale.stable ? "Ready" : "Unstable")
        : "Offline";
      setClass(
        els.scale,
        scale.connected
          ? (scale.stable ? "good" : "warn")
          : "bad"
      );

      els.weight.textContent =
        `${Number(scale.weightGrams || 0).toFixed(1)} g`;

      els.nfc.textContent = nfc.connected
        ? (nfc.tagPresent ? "Tag Present" : "Ready")
        : "Offline";
      setClass(els.nfc, nfc.connected ? "good" : "bad");

      els.spool.textContent =
        spool?.name ||
        spool?.filamentName ||
        spool?.tagId ||
        nfc.tagId ||
        "None";

    } catch (err) {
      els.api.textContent = "Offline";
      setClass(els.api, "bad");
      setClass(els.apiDot, "bad");
    }
  }

  refreshMonitor();
  setInterval(refreshMonitor, 1000);
})();
