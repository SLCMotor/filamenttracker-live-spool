const techMenuItems = [
  { label: "Dashboard", href: "/dashboard", detail: "Live view" },
  { label: "Diagnostics", href: "/diagnostics", detail: "System tools" },
  { label: "Calibration", href: "/calibration-wizard", detail: "Scale wizard" },
  { label: "Settings", href: "/settings", detail: "Device setup" },
];

let techMenuPressTimer = null;
let techMenuProgressTimer = null;
let techMenuPressStartedAt = 0;
const techMenuHoldMs = 900;

function closeTechMenu() {
  const overlay = document.querySelector(".tech-menu-overlay");
  if (overlay) overlay.remove();
}

function openTechMenu() {
  closeTechMenu();

  const overlay = document.createElement("div");
  overlay.className = "tech-menu-overlay";

  const card = document.createElement("div");
  card.className = "tech-menu-card";

  card.innerHTML = `
    <div class="tech-menu-header">
      <h2>Technician Menu</h2>
      <button class="tech-menu-close" type="button">×</button>
    </div>
    <div class="tech-menu-list"></div>
  `;

  const list = card.querySelector(".tech-menu-list");

  techMenuItems.forEach((item) => {
    const link = document.createElement("a");
    link.className = "tech-menu-item";
    link.href = item.href;
    link.innerHTML = `
      <span>${item.label}</span>
      <strong>${item.detail}</strong>
    `;
    list.appendChild(link);
  });

  overlay.appendChild(card);
  document.body.appendChild(overlay);

  card.querySelector(".tech-menu-close").addEventListener("click", closeTechMenu);

  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) closeTechMenu();
  });
}

function setHoldProgress(trigger, percent) {
  trigger.style.setProperty("--hold-progress", `${percent}%`);
}

function clearTechMenuTimer(trigger) {
  if (techMenuPressTimer) {
    clearTimeout(techMenuPressTimer);
    techMenuPressTimer = null;
  }

  if (techMenuProgressTimer) {
    clearInterval(techMenuProgressTimer);
    techMenuProgressTimer = null;
  }

  if (trigger) setHoldProgress(trigger, 0);
}

document.addEventListener("DOMContentLoaded", () => {
  const trigger = document.querySelector("[data-tech-menu-trigger]");
  if (!trigger) return;

  trigger.classList.add("tech-menu-trigger");

  trigger.addEventListener("pointerdown", () => {
    clearTechMenuTimer(trigger);

    techMenuPressStartedAt = Date.now();
    setHoldProgress(trigger, 0);

    techMenuProgressTimer = setInterval(() => {
      const elapsed = Date.now() - techMenuPressStartedAt;
      const percent = Math.min(100, Math.round((elapsed / techMenuHoldMs) * 100));
      setHoldProgress(trigger, percent);
    }, 30);

    techMenuPressTimer = setTimeout(() => {
      clearTechMenuTimer(trigger);
      openTechMenu();
    }, techMenuHoldMs);
  });

  trigger.addEventListener("pointerup", () => clearTechMenuTimer(trigger));
  trigger.addEventListener("pointerleave", () => clearTechMenuTimer(trigger));
  trigger.addEventListener("pointercancel", () => clearTechMenuTimer(trigger));
});
