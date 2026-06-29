window.LiveSpoolGauge = {
  previousFillPercent: 0,

  clamp(value, min, max) {
    return Math.max(min, Math.min(value, max));
  },

  hexToRgb(hex) {
    if (!hex || typeof hex !== "string") return { r: 0, g: 216, b: 255 };

    const clean = hex.replace("#", "").trim();
    if (clean.length !== 6) return { r: 0, g: 216, b: 255 };

    return {
      r: parseInt(clean.slice(0, 2), 16),
      g: parseInt(clean.slice(2, 4), 16),
      b: parseInt(clean.slice(4, 6), 16)
    };
  },

  rgba(hex, alpha) {
    const rgb = this.hexToRgb(hex);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
  },

  ring(ctx, cx, cy, outer, inner, fillStyle) {
    ctx.fillStyle = fillStyle;
    ctx.beginPath();
    ctx.arc(cx, cy, outer, 0, Math.PI * 2);
    ctx.arc(cx, cy, inner, 0, Math.PI * 2, true);
    ctx.fill();
  },

  drawSpool(ctx, cx, cy, color, fillPercent) {
    const outer = 116;
    const backOuter = 104;
    const filamentOuter = 91;
    const filamentInner = 38;
    const frontInner = 34;
    const hub = 31;

    ctx.save();

    ctx.shadowColor = "rgba(0, 216, 255, 0.24)";
    ctx.shadowBlur = 34;

    const backGrad = ctx.createRadialGradient(cx - 42, cy - 48, 8, cx, cy, outer);
    backGrad.addColorStop(0, "#5a6677");
    backGrad.addColorStop(0.28, "#202a38");
    backGrad.addColorStop(0.72, "#090e17");
    backGrad.addColorStop(1, "#02050a");

    ctx.fillStyle = backGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, outer, 0, Math.PI * 2);
    ctx.fill();

    ctx.shadowBlur = 0;

    ctx.strokeStyle = "rgba(255, 255, 255, 0.24)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(cx, cy, outer - 3, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = "rgba(0, 216, 255, 0.13)";
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(cx, cy, backOuter - 4, 0, Math.PI * 2);
    ctx.stroke();

    const filamentRadius = this.clamp(
      filamentInner + (filamentOuter - filamentInner) * fillPercent,
      filamentInner + 6,
      filamentOuter
    );

    const filamentGrad = ctx.createRadialGradient(cx - 28, cy - 32, filamentInner, cx, cy, filamentOuter);
    filamentGrad.addColorStop(0, this.rgba(color, 0.38));
    filamentGrad.addColorStop(0.42, this.rgba(color, 0.95));
    filamentGrad.addColorStop(0.78, this.rgba(color, 0.72));
    filamentGrad.addColorStop(1, "rgba(0, 0, 0, 0.4)");

    this.ring(ctx, cx, cy, filamentRadius, filamentInner, filamentGrad);

    for (let r = filamentInner + 4; r < filamentRadius; r += 4.2) {
      ctx.strokeStyle = "rgba(255,255,255,0.22)";
      ctx.lineWidth = 1.1;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      ctx.strokeStyle = "rgba(0,0,0,0.24)";
      ctx.lineWidth = 0.8;
      ctx.beginPath();
      ctx.arc(cx, cy, r + 1.7, 0, Math.PI * 2);
      ctx.stroke();
    }

    for (let i = 0; i < 8; i++) {
      const angle = (Math.PI * 2 * i) / 8;
      const width = 0.16;

      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(angle);

      const spokeGrad = ctx.createLinearGradient(frontInner, -9, outer - 20, 9);
      spokeGrad.addColorStop(0, "#303847");
      spokeGrad.addColorStop(0.5, "#111823");
      spokeGrad.addColorStop(1, "#384354");

      ctx.fillStyle = spokeGrad;
      ctx.strokeStyle = "rgba(255,255,255,0.16)";
      ctx.lineWidth = 1.5;

      ctx.beginPath();
      ctx.moveTo(frontInner + 8, -7);
      ctx.lineTo(outer - 25, -13);
      ctx.lineTo(outer - 18, 13);
      ctx.lineTo(frontInner + 8, 7);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      ctx.restore();

      ctx.strokeStyle = "rgba(0,0,0,0.5)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(cx, cy, outer - 21, angle - width, angle + width);
      ctx.stroke();
    }

    const frontGrad = ctx.createRadialGradient(cx - 35, cy - 40, 10, cx, cy, outer);
    frontGrad.addColorStop(0, "rgba(100,112,130,0.42)");
    frontGrad.addColorStop(0.38, "rgba(26,34,46,0.5)");
    frontGrad.addColorStop(0.78, "rgba(5,9,15,0.78)");
    frontGrad.addColorStop(1, "rgba(0,0,0,0.92)");

    this.ring(ctx, cx, cy, outer, outer - 18, frontGrad);

    ctx.strokeStyle = "rgba(255,255,255,0.22)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, outer - 8, 0, Math.PI * 2);
    ctx.stroke();

    const hubGrad = ctx.createRadialGradient(cx - 12, cy - 12, 4, cx, cy, hub);
    hubGrad.addColorStop(0, "#586579");
    hubGrad.addColorStop(0.45, "#151d2a");
    hubGrad.addColorStop(1, "#02050a");

    ctx.fillStyle = hubGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, hub, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = "rgba(255,255,255,0.24)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, hub, 0, Math.PI * 2);
    ctx.stroke();

    ctx.fillStyle = "#000";
    ctx.beginPath();
    ctx.arc(cx, cy, 14, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = "rgba(0,216,255,0.28)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, 17, 0, Math.PI * 2);
    ctx.stroke();

    ctx.fillStyle = "rgba(0,0,0,0.78)";
    for (let i = 0; i < 8; i++) {
      const angle = (Math.PI * 2 * i) / 8;
      ctx.beginPath();
      ctx.arc(cx + Math.cos(angle) * 24, cy + Math.sin(angle) * 24, 5, 0, Math.PI * 2);
      ctx.fill();
    }

    const shine = ctx.createLinearGradient(cx - outer, cy - outer, cx + outer, cy + outer);
    shine.addColorStop(0, "rgba(255,255,255,0.24)");
    shine.addColorStop(0.16, "rgba(255,255,255,0.07)");
    shine.addColorStop(0.34, "rgba(255,255,255,0)");
    shine.addColorStop(1, "rgba(255,255,255,0)");

    ctx.fillStyle = shine;
    ctx.beginPath();
    ctx.arc(cx, cy, outer - 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  },

  draw(data) {
    const canvas = document.getElementById("spoolGauge");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const weight = Number(data.weightGrams || 0);
    const tag = data.tag || data.spool || null;
    const color = tag && tag.colorHex ? tag.colorHex : "#00d8ff";

    const maxPreviewWeight = 1200;
    const targetFill = this.clamp(weight / maxPreviewWeight, 0.04, 1);

    this.previousFillPercent += (targetFill - this.previousFillPercent) * 0.16;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    this.drawSpool(ctx, canvas.width / 2, 132, color, this.previousFillPercent);
  }
};
