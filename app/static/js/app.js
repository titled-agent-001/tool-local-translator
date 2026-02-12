document.addEventListener("DOMContentLoaded", () => {
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    // ── Load languages ──
    fetch("/api/languages")
        .then(r => r.json())
        .then(data => {
            const srcSel = $("#source-lang");
            const tgtSel = $("#target-lang");
            for (const [code, name] of Object.entries(data.source_languages)) {
                srcSel.add(new Option(name, code));
            }
            for (const [code, name] of Object.entries(data.target_languages)) {
                tgtSel.add(new Option(name, code));
            }
            srcSel.value = "auto";
            tgtSel.value = "zh-TW";
        });

    // ── Tabs ──
    $$(".tab").forEach(tab => {
        tab.addEventListener("click", () => {
            $$(".tab").forEach(t => t.classList.remove("active"));
            $$(".mode-panel").forEach(p => p.classList.remove("active"));
            tab.classList.add("active");
            $(`#panel-${tab.dataset.mode}`).classList.add("active");
        });
    });

    // ── Swap Languages ──
    $("#swap-langs").addEventListener("click", () => {
        const src = $("#source-lang");
        const tgt = $("#target-lang");
        if (src.value === "auto") return;
        const tmp = src.value;
        src.value = tgt.value;
        tgt.value = tmp;
    });

    // ── Status helpers ──
    function showStatus(msg) {
        $("#status-text").textContent = msg;
        $("#status-bar").style.display = "flex";
    }
    function hideStatus() {
        $("#status-bar").style.display = "none";
    }

    // ── Text Translation ──
    $("#translate-text-btn").addEventListener("click", async () => {
        const text = $("#source-text").value.trim();
        if (!text) return;
        showStatus("Translating text…");
        try {
            const res = await fetch("/api/translate/text", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text,
                    source_lang: $("#source-lang").value,
                    target_lang: $("#target-lang").value,
                }),
            });
            const data = await res.json();
            if (data.error) throw new Error(data.error);
            $("#result-text").value = data.translated_text;
        } catch (e) {
            alert("Translation failed: " + e.message);
        } finally {
            hideStatus();
        }
    });

    // ── File upload helpers ──
    function setupUpload(dropId, inputId, nameId, btnId, accept) {
        const zone = $(dropId);
        const input = $(inputId);
        const nameEl = $(nameId);
        const btn = $(btnId);

        zone.addEventListener("click", () => input.click());
        zone.querySelector("a").addEventListener("click", (e) => { e.preventDefault(); input.click(); });

        ["dragenter", "dragover"].forEach(evt => {
            zone.addEventListener(evt, e => { e.preventDefault(); zone.classList.add("dragover"); });
        });
        ["dragleave", "drop"].forEach(evt => {
            zone.addEventListener(evt, e => { e.preventDefault(); zone.classList.remove("dragover"); });
        });
        zone.addEventListener("drop", e => {
            const files = e.dataTransfer.files;
            if (files.length) { input.files = files; input.dispatchEvent(new Event("change")); }
        });

        input.addEventListener("change", () => {
            if (input.files.length) {
                nameEl.textContent = `Selected: ${input.files[0].name}`;
                btn.disabled = false;
            }
        });

        return input;
    }

    setupUpload("#image-drop-zone", "#image-file", "#image-file-name", "#translate-image-btn");
    setupUpload("#pdf-drop-zone", "#pdf-file", "#pdf-file-name", "#translate-pdf-btn");

    // ── Image Translation ──
    $("#translate-image-btn").addEventListener("click", async () => {
        const file = $("#image-file").files[0];
        if (!file) return;
        showStatus("Translating image (OCR + translation)… This may take a moment.");
        const fd = new FormData();
        fd.append("file", file);
        fd.append("source_lang", $("#source-lang").value);
        fd.append("target_lang", $("#target-lang").value);
        try {
            const res = await fetch("/api/translate/file", { method: "POST", body: fd });
            const data = await res.json();
            if (data.error) throw new Error(data.error);
            $("#image-result-img").src = data.download_url;
            $("#image-download").href = data.download_url;
            $("#image-result").style.display = "block";
        } catch (e) {
            alert("Image translation failed: " + e.message);
        } finally {
            hideStatus();
        }
    });

    // ── PDF Translation ──
    $("#translate-pdf-btn").addEventListener("click", async () => {
        const file = $("#pdf-file").files[0];
        if (!file) return;
        showStatus("Translating PDF… This may take a while for large files.");
        const fd = new FormData();
        fd.append("file", file);
        fd.append("source_lang", $("#source-lang").value);
        fd.append("target_lang", $("#target-lang").value);
        try {
            const res = await fetch("/api/translate/file", { method: "POST", body: fd });
            const data = await res.json();
            if (data.error) throw new Error(data.error);
            $("#pdf-download").href = data.download_url;
            $("#pdf-result").style.display = "block";
        } catch (e) {
            alert("PDF translation failed: " + e.message);
        } finally {
            hideStatus();
        }
    });
});
