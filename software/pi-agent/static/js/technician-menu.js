(function () {
  const HOLD_MS = 2500;

  const menuItems = [
    { label: "Dashboard", href: "/dashboard" },
    { label: "Calibration", href: "/calibration-wizard" },
    { label: "Diagnostics", href: "/diagnostics" },
    { label: "Settings", href: "#", disabled: true },
    { label: "About", href: "#", disabled: true },
  ];

  let holdTimer = null;
  let progressTimer = null;
  let startedAt = 0;
  let activeTrigger = null;

  function buildMenu() {
    if (document.getElementById("technicianMenuOverlay")) return;

    const overlay = document.createElement("div");
    overlay.id = "technicianMenuOverlay";
    overlay.className = "tech-menu-overlay hidden";

    overlay.innerHTML = `
      <div class="tech-menu-card">
        <div class="tech-menu-header">
          <div>
            <div class="eyebrow">Hidden Access</div>
            <h2>Technician Menu</h2>
          </div>
          <button id="closeTechMenu" class="tech-menu-close" type="button">×</button>
        </div>

        <div class="tech-menu-list">
          ${menuItems.map((item) => `
            <a
              class="tech-menu-item ${item.disabled ? "disabled" : ""}"
              href="${item.href}"
              ${item.disabled ? "aria-disabled='true'" : ""}
            >
              <span>${item.label}</span>
              <strong>${item.disabled ? "Soon" : "Open"}</strong>
            </a>
          `).join("")}
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    document.getElementById("closeTechMenu").addEventListener("click", closeMenu);

    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) closeMenu();
    });

    overlay.querySelectorAll(".tech-menu-item.disabled").forEach((item) => {
      item.addEventListener("click", (event) => event.preventDefault());
    });
  }

  function openMenu() {
    const overlay = document.getElementById("technicianMenuOverlay");
    if (overlay) overlay.classList.remove("hidden");
  }

  function closeMenu() {
    const overlay = document.getElementById("technicianMenuOverlay");
    if (overlay) overlay.classList.add("hidden");
  }

  function resetProgress(trigger) {
    if (!trigger) return;
    trigger.style.setProperty("--hold-progress", "0%");
    trigger.classList.remove("tech-hold-active");
  }

  function clearHold() {
    clearTimeout(holdTimer);
    clearInterval(progressTimer);

    holdTimer = null;
    progressTimer = null;

    resetProgress(activeTrigger);
    activeTrigger = null;
  }

  function startHold(trigger, event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    clearHold();

    activeTrigger = trigger;
    startedAt = Date.now();

    trigger.classList.add("tech-hold-active");
    trigger.style.setProperty("--hold-progress", "0%");

    holdTimer = setTimeout(() => {
      const finishedTrigger = activeTrigger;
      clearHold();
      resetProgress(finishedTrigger);
      openMenu();
    }, HOLD_MS);

    progressTimer = setInterval(() => {
      if (!activeTrigger) return;

      const elapsed = Date.now() - startedAt;
      const percent = Math.min(100, (elapsed / HOLD_MS) * 100);
      activeTrigger.style.setProperty("--hold-progress", `${percent}%`);
    }, 40);
  }

  function attachTrigger() {
    const trigger = document.querySelector("[data-tech-menu-trigger]");

    if (!trigger) return;

    trigger.classList.add("tech-menu-trigger");
    trigger.title = "Press and hold for Technician Menu";
    trigger.style.touchAction = "none";

    trigger.addEventListener("pointerdown", (event) => startHold(trigger, event));
    trigger.addEventListener("pointerup", clearHold);
    trigger.addEventListener("pointercancel", clearHold);

    trigger.addEventListener("touchstart", (event) => startHold(trigger, event), { passive: false });
    trigger.addEventListener("touchend", clearHold);
    trigger.addEventListener("touchcancel", clearHold);

    trigger.addEventListener("mousedown", (event) => startHold(trigger, event));
    trigger.addEventListener("mouseup", clearHold);
  }

  buildMenu();
  attachTrigger();
})();
