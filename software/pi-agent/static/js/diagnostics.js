function setText(id, value) {
  window.LiveSpoolStatusPanel.setText(id, value);
}

function valueOrDash(value) {
  return window.LiveSpoolStatusPanel.valueOrDash(value);
}

function displayWeight(value) {
  const grams = Number(value);
  if (!Number.isFinite(grams)) {
    return "--";
  }

  const rounded = Math.abs(grams) < 1 ? 0 : Math.round(grams);
  return `${rounded}`;
}

function pickSpoolName(spool) {
  if (!spool) {
    return "No spool loaded";
  }

  return spool.name || spool.filamentName || spool.spoolName || spool.material || "Tagged spool";
}

async function refreshDiagnostics() {
  try {
    const response = await fetch("/spool/current", { cache: "no-store" });
    const data = await response.json();
    const spool = data.spool || data.tag || null;

    setText("weight", displayWeight(data.weightGrams));
    setText("tagId", valueOrDash(data.tagId));
    setText("spoolName", pickSpoolName(spool));
    setText("error", data.error || "None");
    setText("lastUpdated", new Date().toLocaleTimeString());

    window.LiveSpoolStatusPanel.update(data);
  } catch (error) {
    setText("lastUpdated", "Diagnostics error");
    setText("error", "Unable to refresh diagnostics");
  }
}

refreshDiagnostics();
setInterval(refreshDiagnostics, 1000);

document.addEventListener("DOMContentLoaded", () => {
  const footerCards = document.querySelectorAll(".footer-card");

  if (footerCards.length > 0) {
    footerCards[0].addEventListener("click", () => {
      window.location.href = "/dashboard";
    });
  }
});
