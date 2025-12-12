console.log('Browser client loaded.');

function copyText(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;

    // Check if it's a textarea or a code block
    let textToCopy = "";
    if (el.tagName.toLowerCase() === 'textarea' || el.tagName.toLowerCase() === 'input') {
        textToCopy = el.value;
    } else {
        textToCopy = el.innerText || el.textContent;
    }

    navigator.clipboard.writeText(textToCopy).then(() => {
        console.log(`Copied text from ${elementId}`);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

function copyCode() {
    copyText('code-output');
}

function autoResize(el) {
    el.style.height = 'auto'; // Reset height
    el.style.height = el.scrollHeight + 'px'; // Set to scroll height
}

function displayCode(code, language = "plaintext") {
    const el = document.getElementById("code-output");
    if (!el) return;

    // Remove old class
    el.className = "";
    el.classList.add("language-" + language);
    el.textContent = code;

    // Apply highlight.js
    hljs.highlightElement(el);
}

async function generateCode() {
    const descInput = document.getElementById("description-input");
    const desc = descInput ? descInput.value.trim() : "";

    if (!desc) {
        displayCode("Please enter a description first.", "plaintext");
        return;
    }

    displayCode("Generating code...", "plaintext");

    try {
        const res = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: desc })
        });
        const json = await res.json();

        const langSelect = document.getElementById("language-select");
        const lang = langSelect ? langSelect.value : "python";

        displayCode(json.code, lang);

    } catch (err) {
        displayCode("Error generating code: " + err, "plaintext");
    }
}

async function runGeneratedCode() {
    const codeEl = document.getElementById("code-output");
    const lang = document.getElementById("language-select").value || "python";
    const runBtn = document.getElementById("run-btn");
    const outCode = document.getElementById("runtime-out-code");

    if (!codeEl) return;
    const code = codeEl.textContent || codeEl.innerText || "";

    runBtn.disabled = true;
    runBtn.textContent = "Running...";

    try {
        const res = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code, language: lang })
        });
        const json = await res.json();

        // Format stdout/stderr
        const stdout = json.stdout || "";
        const stderr = json.stderr || "";

        let display = "";
        if (stdout) display += "STDOUT:\n" + stdout + "\n";
        if (stderr) display += (stderr ? "\nSTDERR:\n" + stderr : "");
        if (!display) display = "No output.";

        // Show output in a code block (plaintext)
        outCode.className = ""; // reset classes
        outCode.classList.add("language-plaintext");
        outCode.textContent = display;
        hljs.highlightElement(outCode);

    } catch (err) {
        outCode.textContent = "Error connecting to runner: " + err;
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = "Run";
    }
}

function init() {
    const micBtn = document.getElementById('mic-btn');
    const descriptionInput = document.getElementById('description-input');

    // Auto-resize listeners
    if (descriptionInput) {
        descriptionInput.addEventListener('input', () => autoResize(descriptionInput));
    }

    if (micBtn) {
        micBtn.addEventListener('click', () => {
            console.log('Mic button clicked. Voice connection logic is deferred.');

            micBtn.classList.toggle('listening');

            if (micBtn.classList.contains('listening')) {
                setTimeout(() => {
                    descriptionInput.value += " [Listening...]";
                    autoResize(descriptionInput);
                }, 500);
            } else {
                descriptionInput.value = descriptionInput.value.replace(" [Listening...]", "");
                autoResize(descriptionInput);
            }
        });
    }

    // Initial resize
    if (descriptionInput) autoResize(descriptionInput);

    // Wire Run button
    const runBtn = document.getElementById("run-btn");
    if (runBtn) runBtn.addEventListener("click", runGeneratedCode);

    // When language selection changes, update code highlighting class for display
    const langSelect = document.getElementById("language-select");
    const codeOutput = document.getElementById("code-output");
    if (langSelect && codeOutput) {
        langSelect.addEventListener("change", () => {
            const lang = langSelect.value === "java" ? "java" : "python";
            codeOutput.className = ""; // reset
            codeOutput.classList.add("language-" + lang);
            hljs.highlightElement(codeOutput);
        });
    }
}

window.addEventListener('DOMContentLoaded', init);
window.copyText = copyText;
window.copyCode = copyCode;
window.copyCode = copyCode;
window.generateCode = generateCode;
