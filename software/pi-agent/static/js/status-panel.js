window.LiveSpoolStatusPanel = {
  valueOrDash(value) {
    if (value === null || value === undefined || value === "") {
      return "--";
    }

    return value;
  },

  statusClass(ok, warning) {
    if (ok) {
      return "good";
    }

    if (warning) {
      return "warn";
    }

    return "bad";
  },

  setText(id, value) {
    const element = document.getElementById(id);

    if (!element) {
      return;
    }

    element.textContent = value;
  },

  setClass(id, className) {
    const element = document.getElementById(id);

    if (!element) {
      return;
    }

    element.classList.remove("good", "warn", "bad");
    element.classList.add(className);
  },

  update(data) {
    const scale = data.scale || {};
    const nfc = data.nfc || {};

    this.setText("nfcFooter", nfc.connected ? ((nfc.tagPresent || data.tagPresent) ? "TAG" : "READY") : "OFFLINE");
    this.setClass("nfcFooter", this.statusClass(nfc.connected, false));

    this.setText("scaleFooter", scale.connected ? (scale.stable ? "READY" : "UNSTABLE") : "OFFLINE");
    this.setClass("scaleFooter", this.statusClass(scale.connected && scale.stable, scale.connected));

    this.setText("monitorStatus", data.monitorRunning ? "RUNNING" : "STOPPED");
    this.setClass("monitorStatus", this.statusClass(data.monitorRunning, false));
  }
};
