function wrapSwapWave(el) {
  if (el.dataset.waveWrapped === "1") return;
  el.dataset.waveWrapped = "1";

  const text = el.textContent;          // ✅ you missed this
  const chars = [...text];

  el.style.setProperty("--count", chars.length);

  el.textContent = "";

  chars.forEach((ch, i) => {
    const letter = document.createElement("span");
    letter.className = "wave-letter";
    letter.style.setProperty("--i", i);

    const safeCh = ch === " " ? "\u00A0" : ch;

    const sizer = document.createElement("span");
    sizer.className = "wave-sizer";
    sizer.textContent = safeCh;

    const top = document.createElement("span");
    top.className = "wave-top";
    top.textContent = safeCh;

    const bottom = document.createElement("span");
    bottom.className = "wave-bottom";
    bottom.textContent = safeCh;

    letter.appendChild(sizer);
    letter.appendChild(top);
    letter.appendChild(bottom);
    el.appendChild(letter);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".wave-swap").forEach(wrapSwapWave);
});
