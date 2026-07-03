function valueOrDash(value) {
  return window.LiveSpoolStatusPanel.valueOrDash(value);
}

function setText(id, value) {
  window.LiveSpoolStatusPanel.setText(id, value);
}

function pickSpoolName(tag) {
  if (!tag) {
    return "No spool loaded";
  }

  return tag.name || tag.filamentName || tag.spoolName || tag.variant || tag.material || "Tagged spool";
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

  return "NFC tag detected";
}

function updateSpoolDetails(data) {
  const tag = data.spool || data.tag || null;
  const tagType = data.tagType || data.nfc?.tagType || null;

  setText("weight", valueOrDash(data.weightGrams));
  setText("spoolName", pickSpoolName(tag));
  setText("spoolSubtitle", subtitleForTag(data, tagType));
  const brand = pickField(tag, ["brand", "manufacturer", "vendor"]);
  setText("brandBadge", brand);
  setText("material", pickField(tag, ["material", "variant", "filamentType", "type"]));
  setText("color", pickField(tag, ["colorName", "color", "colorHex"]));
  setText("tagId", valueOrDash(data.tagId));
  setText("changed", data.tagChanged || data.weightChanged ? "Yes" : "No");

  setColorSwatch(tag);
}

async function refreshDashboard() {
  try {
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
