const EMPTY_THRESHOLD_GRAMS = 100;
const PLACED_THRESHOLD_GRAMS = 100;
const VERIFY_PASS_GRAMS = 5;
const SCALE_IS_MOCK = window.liveSpoolScaleIsMock === true;

const steps = [
  { title: "Welcome", icon: "⚖", text: "This wizard will calibrate the Live Spool scale using a known weight.", button: "Start", mode: "manual" },
  { title: "Remove spool", icon: "⬆", text: "Remove the spool and anything sitting on the scale platform.", button: "Platform empty", mode: "wait-empty", developer: true },
  { title: "Tare scale", icon: "◎", text: "The platform is empty. Save this as the zero point.", button: "Tare", mode: "tare" },
  { title: "Place weight", icon: "⬇", text: "Place your calibration weight on the center of the platform.", button: "Weight detected", mode: "wait-weight", developer: true },
  { title: "Select weight", icon: "✎", text: "Select the exact weight currently on the platform. Choosing the wrong value will create an incorrect calibration.", button: "Save calibration", mode: "known-weight", input: true },
  { title: "Verification", icon: "✓", text: "Confirm the measured weight matches the selected calibration weight.", button: "Looks good", mode: "verify", verification: true },
  { title: "Finished", icon: "★", text: "Calibration is complete. Scale is ready.", button: "Dashboard", mode: "finished", verification: true, finished: true }
];

let currentStep = 0;
let latestWeight = null;
let selectedKnownWeight = null;
let verificationSnapshot = null;

const stepPill = document.getElementById("stepPill");
const statusPill = document.getElementById("statusPill");
const progressFill = document.getElementById("progressFill");
const stepIcon = document.getElementById("stepIcon");
const stepTitle = document.getElementById("stepTitle");
const stepText = document.getElementById("stepText");
const liveWeight = document.getElementById("liveWeight");
const scaleState = document.getElementById("scaleState");
const knownWeightPanel = document.getElementById("knownWeightPanel");
const knownWeightInput = document.getElementById("knownWeightInput");
const customWeightPanel = document.getElementById("customWeightPanel");
const customToggleButton = document.getElementById("customToggleButton");
const selectedWeightLabel = document.getElementById("selectedWeightLabel");
const resultPanel = document.getElementById("resultPanel");
const backButton = document.getElementById("backButton");
const nextButton = document.getElementById("nextButton");
const developerPanel = document.getElementById("developerPanel");
const devButtons = document.querySelectorAll(".dev-button");
const keypadButtons = document.querySelectorAll(".keypad-button");
const presetButtons = document.querySelectorAll(".preset-button");
const verificationPanel = document.getElementById("verificationPanel");
const verifyExpected = document.getElementById("verifyExpected");
const verifyMeasured = document.getElementById("verifyMeasured");
const verifyDifference = document.getElementById("verifyDifference");
const verifyResult = document.getElementById("verifyResult");

function setStatus(message, isError = false) {
  statusPill.textContent = message;
  statusPill.classList.toggle("danger", isError);
  statusPill.classList.toggle("muted", !isError);
}

function showResult(message, isError = false) {
  resultPanel.textContent = message;
  resultPanel.classList.remove("hidden");
  resultPanel.classList.toggle("error", isError);
}

function hideResult() {
  resultPanel.textContent = "";
  resultPanel.classList.add("hidden");
  resultPanel.classList.remove("error");
}

function currentMode() {
  return steps[currentStep].mode;
}

function displayedWeight() {
  return Number(latestWeight?.weightGrams || 0);
}

function isPlatformEmpty() {
  return latestWeight && latestWeight.connected && latestWeight.stable && Math.abs(displayedWeight()) <= EMPTY_THRESHOLD_GRAMS;
}

function isWeightPlaced() {
  return latestWeight && latestWeight.connected && latestWeight.stable && displayedWeight() >= PLACED_THRESHOLD_GRAMS;
}

function updateSelectedWeight(value) {
  selectedKnownWeight = value ? Number(value) : null;
  selectedWeightLabel.textContent = selectedKnownWeight ? `${selectedKnownWeight} g selected` : "None selected";
  knownWeightInput.value = selectedKnownWeight ? String(selectedKnownWeight) : "";
}

function updateVerification() {
  if (!selectedKnownWeight || !latestWeight) return;

  const expected = selectedKnownWeight;
  const measured = displayedWeight();
  const difference = measured - expected;
  const pass = Math.abs(difference) <= VERIFY_PASS_GRAMS;

  verificationSnapshot = { expected, measured, difference, pass };

  verifyExpected.textContent = `${expected.toFixed(2)} g`;
  verifyMeasured.textContent = `${measured.toFixed(2)} g`;
  verifyDifference.textContent = `${difference.toFixed(2)} g`;
  verifyResult.textContent = pass ? "PASS" : "CHECK";
  verifyResult.classList.toggle("verify-pass", pass);
  verifyResult.classList.toggle("verify-warn", !pass);
}

function updateStepGate() {
  const mode = currentMode();

  if (mode === "wait-empty") {
    if (isPlatformEmpty()) {
      nextButton.disabled = false;
      setStatus("Platform empty");
      showResult("Platform is empty and stable.");
    } else {
      nextButton.disabled = true;
      setStatus("Waiting");
      showResult("Waiting for empty stable platform...");
    }
  }

  if (mode === "wait-weight") {
    if (isWeightPlaced()) {
      nextButton.disabled = false;
      setStatus("Weight detected");
      showResult("Calibration weight detected.");
    } else {
      nextButton.disabled = true;
      setStatus("Waiting");
      showResult("Waiting for a stable calibration weight...");
    }
  }

  if (mode === "known-weight") {
    nextButton.disabled = !selectedKnownWeight;
    setStatus(selectedKnownWeight ? "Ready" : "Select weight");
  }

  if (mode === "verify" || mode === "finished") {
    updateVerification();
  }
}

function renderStep() {
  const step = steps[currentStep];

  stepPill.textContent = `Step ${currentStep + 1} of ${steps.length}`;
  progressFill.style.width = `${((currentStep + 1) / steps.length) * 100}%`;
  stepIcon.textContent = step.icon;
  stepTitle.textContent = step.title;
  stepText.textContent = step.text;
  nextButton.textContent = step.button;

  backButton.disabled = false;
  backButton.textContent = "Back";
  backButton.classList.remove("secondary");
  backButton.classList.add("primary");
  nextButton.disabled = false;

  knownWeightPanel.classList.toggle("hidden", !step.input);
  verificationPanel.classList.toggle("hidden", !step.verification);
  developerPanel.classList.toggle("hidden", !(SCALE_IS_MOCK && step.developer));

  if (!step.input) customWeightPanel.classList.add("hidden");

  hideResult();
  setStatus("Ready");
  updateStepGate();
}

async function getJson(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch (error) {}
    throw new Error(message);
  }

  return response.json();
}

async function refreshStatus() {
  try {
    latestWeight = await getJson("/weight");

    liveWeight.textContent = `${displayedWeight().toFixed(2)} g`;
    scaleState.textContent = latestWeight.connected
      ? (latestWeight.stable ? "Stable" : "Moving")
      : "Disconnected";

    updateStepGate();
  } catch (error) {
    scaleState.textContent = "Error";
    setStatus("Status error", true);
  }
}

async function handleNext() {
  const step = steps[currentStep];

  try {
    nextButton.disabled = true;

    if (step.mode === "tare") {
      setStatus("Taring...");
      const result = await getJson("/calibration/tare", { method: "POST" });
      showResult(result.message || "Scale tared.");
      await refreshStatus();
    }

    if (step.mode === "known-weight") {
      if (!selectedKnownWeight || selectedKnownWeight <= 0) {
        showResult("Select a known weight first.", true);
        setStatus("Select weight", true);
        return;
      }

      setStatus("Saving...");
      const result = await getJson("/calibration/known-weight", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ knownWeightGrams: selectedKnownWeight })
      });

      showResult(result.message || "Calibration saved.");
      await refreshStatus();
      updateVerification();
    }

    if (step.finished) {
      window.location.href = "/dashboard";
      return;
    }

    if (currentStep < steps.length - 1) {
      currentStep += 1;
      renderStep();
      await refreshStatus();
    }
  } catch (error) {
    showResult(error.message, true);
    setStatus("Action failed", true);
  } finally {
    if (!["wait-empty", "wait-weight"].includes(currentMode())) {
      nextButton.disabled = false;
    }
    updateStepGate();
  }
}

async function setMockWeight(targetDisplayedGrams) {
  try {
    setStatus(`Mock scale ${targetDisplayedGrams} g`);

    await getJson("/mock/weight", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ weightGrams: targetDisplayedGrams })
    });

    await refreshStatus();
  } catch (error) {
    showResult(error.message, true);
    setStatus("Mock failed", true);
  }
}

function handleBack() {
  if (currentStep === 0) {
    window.location.href = "/dashboard";
    return;
  }

  currentStep -= 1;
  renderStep();
}

backButton.addEventListener("click", handleBack);
nextButton.addEventListener("click", handleNext);

devButtons.forEach((button) => {
  button.addEventListener("click", () => setMockWeight(Number(button.dataset.weight)));
});

presetButtons.forEach((button) => {
  button.addEventListener("click", () => {
    updateSelectedWeight(Number(button.dataset.value));
    customWeightPanel.classList.add("hidden");
    updateStepGate();
  });
});

customToggleButton.addEventListener("click", () => {
  customWeightPanel.classList.toggle("hidden");
});

keypadButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const key = button.dataset.key;

    if (key === "clear") {
      updateSelectedWeight(null);
      return;
    }

    if (key === "backspace") {
      knownWeightInput.value = knownWeightInput.value.slice(0, -1);
      updateSelectedWeight(knownWeightInput.value);
      return;
    }

    knownWeightInput.value = `${knownWeightInput.value}${key}`;
    updateSelectedWeight(knownWeightInput.value);
  });
});

updateSelectedWeight(null);
renderStep();
refreshStatus();
setInterval(refreshStatus, 1000);
