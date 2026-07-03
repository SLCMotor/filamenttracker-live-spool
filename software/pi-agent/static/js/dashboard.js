function valueOrDash(value) {
  return window.LiveSpoolStatusPanel.valueOrDash(value);
}

function setText(id, value) {
  window.LiveSpoolStatusPanel.setText(id, value);
}

function dashboardWeight(value) {
  if (value === null || value === undefined || value === "") {
    return "--";
  }

  const grams = Number(value);
  if (!Number.isFinite(grams)) {
    return "--";
  }

  const rounded = Math.abs(grams) < 1 ? 0 : Math.round(grams);
  return `${rounded}`;
}

function signedDashboardWeight(value) {
  const grams = Number(value);
  if (!Number.isFinite(grams)) {
    return "--";
  }

  const rounded = Math.abs(grams) < 1 ? 0 : Math.round(grams);
  if (rounded > 0) {
    return `+${rounded}g`;
  }
  return `${rounded}g`;
}

function pickSpoolName(tag) {
  if (!tag) {
    return "No spool loaded";
  }

  return tag.name || tag.filamentName || tag.spoolName || tag.variant || tag.material || "Tagged spool";
}

function spoolTitleForData(data, tag, tagType) {
  if (tag) {
    return pickSpoolName(tag);
  }

  if (data.tagPresent && !tagType) {
    return "No spool data";
  }

  return "No spool loaded";
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

  if (!swatch) {
    return;
  }

  if (!tag || !tag.colorHex) {
    swatch.style.background = "linear-gradient(135deg, #29364d, #111827)";
    swatch.title = "No filament color";
    return;
  }

  swatch.style.background = tag.colorHex;
  swatch.title = tag.colorName || tag.colorHex;
}

function writeTitleForState(state) {
  switch (state) {
    case "ready":
      return "Ready to Write";
    case "writing":
      return "Writing...";
    case "verifying":
      return "Verifying...";
    case "succeeded":
      return "Write Successful";
    case "timed_out":
      return "Write Timed Out";
    case "canceled":
      return "Write Canceled";
    case "failed":
      return "Write Failed";
    default:
      return "NFC Writer";
  }
}

function writeMessageForState(status) {
  if (!status) {
    return "Place NFC tag on reader";
  }

  if (status.state === "ready") {
    return "Place NFC tag on reader";
  }

  return status.message || "Place NFC tag on reader";
}

function writePayloadLabel(status) {
  const payload = status?.payload || {};
  const display = status?.display || {};
  const parts = [
    payload.brand,
    payload.material,
    payload.colorName,
    display.locationName
  ].filter((value) => value !== null && value !== undefined && value !== "");

  return parts.length ? parts.join(" · ") : "FilamentTracker spool";
}

function updateNfcWriteOverlay(status) {
  const overlay = document.getElementById("nfcWriteOverlay");
  if (!overlay) {
    return;
  }

  const state = status?.state || "idle";
  if (state === "idle" || state === "not_found") {
    overlay.classList.add("hidden");
    return;
  }

  overlay.className = `nfc-write-overlay ${state}`;
  setText("nfcWriteTitle", writeTitleForState(state));
  setText("nfcWriteMessage", writeMessageForState(status));
  setText("nfcWriteTag", status.tagId || "Waiting");
  setText("nfcWritePayload", writePayloadLabel(status));
}

async function refreshNfcWriteStatus() {
  try {
    const response = await fetch("/nfc/write/current", { cache: "no-store" });
    const status = await response.json();
    updateNfcWriteOverlay(status);
  } catch (error) {
    updateNfcWriteOverlay({ state: "idle" });
  }
}

function subtitleForTag(data, tagType) {
  if (!data.tagPresent) {
    return "Waiting for NFC tag...";
  }

  if (tagType === "bambu_lab_rfid") {
    return "Bambu Lab RFID detected";
  }

  if (tagType === "filamenttracker") {
    return "FilamentTracker tag detected";
  }

  if (!data.data && !data.tag && !data.spool) {
    return "Blank NFC tag detected";
  }

  return "Unknown NFC tag";
}

function updateSpoolDetails(data) {
  const tag = data.spool || data.tag || null;
  const tagType = data.tagType || data.nfc?.tagType || null;
  const hasTagWeight = data.tagWeightGrams !== null && data.tagWeightGrams !== undefined;

  setText("weight", dashboardWeight(data.weightGrams));
  setText("spoolName", spoolTitleForData(data, tag, tagType));
  setText("spoolSubtitle", subtitleForTag(data, tagType));
  const brand = pickField(tag, ["brand", "manufacturer", "vendor"]);
  setText("brandBadge", brand);
  setText("material", pickField(tag, ["material", "variant", "filamentType", "type"]));
  setText("color", pickField(tag, ["colorName", "color", "colorHex"]));
  setText("tagId", valueOrDash(data.tagId));
  setText("changedLabel", hasTagWeight ? "Weight Diff" : "Changed");
  setText(
    "changed",
    hasTagWeight
      ? (data.tagWeightChanged ? `Yes ${signedDashboardWeight(data.weightDeltaGrams)}` : "No")
      : (data.tagChanged || data.weightChanged ? "Yes" : "No")
  );

  setColorSwatch(tag);
}

async function refreshDashboard() {
  try {
    await refreshNfcWriteStatus();

    const response = await fetch("/spool/current", { cache: "no-store" });
    const data = await response.json();

    updateSpoolDetails(data);
    window.LiveSpoolGauge.draw(data);
    window.LiveSpoolStatusPanel.update(data);

    setText("lastUpdated", new Date().toLocaleTimeString());
  } catch (error) {
    setText("lastUpdated", "Dashboard error");
  }
}

refreshDashboard();
setInterval(refreshDashboard, 1000);
