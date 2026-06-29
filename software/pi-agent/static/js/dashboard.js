function valueOrDash(value) {
  if (value === null || value === undefined || value === "") {
    return "--";
  }

  return value;
}

function statusClass(ok, warning) {
  if (ok) {
    return "good";
  }

  if (warning) {
    return "warn";
  }

  return "bad";
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function setClass(id, className) {
  const element = document.getElementById(id);
  element.classList.remove("good", "warn", "bad");
  element.classList.add(className);
}

function pickSpoolName(tag) {
  if (!tag) {
    return "No spool loaded";
  }

  return tag.name || tag.filamentName || tag.spoolName || tag.material || "Tagged spool";
}

function pickField(tag, keys) {
  if (!tag) {
    return "--";
  }

  for (const key of keys) {
    if (tag[key] !== null && tag[key] !== undefined && tag[key] !== "") {
      return tag[key];
    }
  }

  return "--";
}

function setColorSwatch(tag) {
  const swatch = document.getElementById("colorSwatch");

  if (!tag || !tag.colorHex) {
    swatch.style.background = "linear-gradient(135deg, #29364d, #111827)";
    swatch.title = "No filament color";
    return;
  }

  swatch.style.background = tag.colorHex;
  swatch.title = tag.colorName || tag.colorHex;
}

async function refreshDashboard() {
  try {
    const response = await fetch("/spool/current", { cache: "no-store" });
    const data = await response.json();

    const scale = data.scale || {};
    const nfc = data.nfc || {};
    const tag = data.tag || data.spool || null;

    setText("weight", valueOrDash(data.weightGrams));
    setText("spoolName", pickSpoolName(tag));
    setText(
      "spoolSubtitle",
      data.tagPresent ? "FilamentTracker tag detected" : "Waiting for NFC tag..."
    );
    setText("material", pickField(tag, ["material", "filamentType", "type"]));
    setText("brand", pickField(tag, ["brand", "manufacturer", "vendor"]));
    setText("color", pickField(tag, ["colorName", "color", "colorHex"]));
    setText("tagId", valueOrDash(data.tagId));
    setText("changed", data.tagChanged || data.weightChanged ? "Yes" : "No");

    setColorSwatch(tag);

    setText("scaleStatus", scale.connected ? "Scale: READY" : "Scale: OFFLINE");
    setClass("scaleStatus", statusClass(scale.connected, false));

    setText("stableStatus", scale.stable ? "Stable: YES" : "Stable: NO");
    setClass("stableStatus", statusClass(scale.stable, true));

    setText("monitorStatus", data.monitorRunning ? "Monitor: RUNNING" : "Monitor: STOPPED");
    setClass("monitorStatus", statusClass(data.monitorRunning, false));

    setText("nfcFooter", nfc.connected ? (data.tagPresent ? "TAG" : "READY") : "OFFLINE");
    setClass("nfcFooter", statusClass(nfc.connected, false));

    setText("scaleFooter", scale.connected ? "READY" : "OFFLINE");
    setClass("scaleFooter", statusClass(scale.connected, false));

    setText("loadedFooter", data.loaded ? "YES" : "NO");
    setClass("loadedFooter", statusClass(data.loaded, true));

    setText("lastUpdated", new Date().toLocaleTimeString());
  } catch (error) {
    setText("lastUpdated", "Dashboard error");
    setText("scaleStatus", "Scale: --");
    setText("stableStatus", "Stable: --");
    setText("monitorStatus", "Monitor: --");
  }
}

refreshDashboard();
setInterval(refreshDashboard, 1000);
