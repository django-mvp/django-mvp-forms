// Draws the line that says how many characters are left under every input and
// textarea a characters-left widget draws. The widget writes the number from
// which the line appears, the words for each count and the limit (maxlength)
// on the control. The script only reads them, and never changes the value.
(function () {
  "use strict";

  // A page may hold this script once for each form on it. Only the first acts.
  if (window.mvpFormsCharactersLeft) return;
  window.mvpFormsCharactersLeft = true;

  const SELECTOR = "input[data-characters-left-from], textarea[data-characters-left-from]";
  // How long after the last key the status region is written.
  const PAUSE = 1000;
  const timers = new WeakMap();
  let unnamed = 0;

  // What the control's words say. A control whose words cannot be read gets a
  // line with no text.
  function wordsOf(input) {
    try {
      return JSON.parse(input.dataset.charactersLeftWords);
    } catch (error) {
      return [];
    }
  }

  // The name each line records for the input it serves.
  function keyOf(input) {
    if (!input.id && !input.name && !input.dataset.charactersLeftKey) {
      unnamed += 1;
      input.dataset.charactersLeftKey = "unnamed-" + unnamed;
    }
    return input.id || input.name || input.dataset.charactersLeftKey;
  }

  // Where the line goes: after the input, or after the join or label around it,
  // whichever is outermost.
  function anchorOf(input) {
    let anchor = input;
    for (const around of [input.closest(".join"), input.closest("label")]) {
      if (around && around.contains(anchor)) anchor = around;
    }
    return anchor;
  }

  // The line an input serves. It is looked for among the lines that follow the
  // anchor, by the record each carries, and made when none is there.
  function lineOf(input) {
    const key = keyOf(input);
    const anchor = anchorOf(input);
    let last = anchor;
    for (
      let next = anchor.nextElementSibling;
      next && "charactersLeftLine" in next.dataset;
      next = next.nextElementSibling
    ) {
      if (next.dataset.charactersLeftLine === key) return next;
      last = next;
    }
    const line = document.createElement("div");
    line.dataset.charactersLeftLine = key;
    const shown = document.createElement("p");
    shown.className = "label text-base-content text-wrap";
    shown.setAttribute("aria-hidden", "true");
    shown.hidden = true;
    const status = document.createElement("p");
    status.className = "sr-only";
    status.setAttribute("role", "status");
    line.append(shown, status);
    last.after(line);
    return line;
  }

  function say(line, text) {
    const status = line.querySelector("[role=status]");
    if (status.textContent !== text) status.textContent = text;
  }

  function stopWaiting(line) {
    clearTimeout(timers.get(line));
    timers.delete(line);
  }

  // Brings the line of one input up to date. A person's typing also decides when
  // the status region is written.
  function refresh(input, typing) {
    const limit = input.maxLength;
    if (limit < 0) return;
    const left = limit - input.value.length;
    const line = lineOf(input);
    const shown = line.querySelector("[aria-hidden]");
    if (left > Number(input.dataset.charactersLeftFrom)) {
      shown.hidden = true;
      shown.textContent = "";
      stopWaiting(line);
      say(line, "");
      return;
    }
    const wasHidden = shown.hidden;
    const text =
      left < 0
        ? input.dataset.charactersLeftOver.replace("%(n)s", String(-left))
        : wordsOf(input)[left] || "";
    shown.textContent = text;
    shown.hidden = false;
    if (!typing) return;
    stopWaiting(line);
    if (wasHidden || left === 0) {
      say(line, text);
    } else {
      timers.set(
        line,
        setTimeout(() => say(line, shown.textContent), PAUSE),
      );
    }
  }

  function refreshWithin(node) {
    if (node.nodeType !== Node.ELEMENT_NODE) return;
    if (node.matches(SELECTOR)) refresh(node, false);
    node.querySelectorAll(SELECTOR).forEach((input) => refresh(input, false));
  }

  document.addEventListener(
    "input",
    (event) => {
      if (event.target.matches && event.target.matches(SELECTOR)) {
        refresh(event.target, true);
      }
    },
    true,
  );
  document.addEventListener(
    "focusin",
    (event) => {
      if (event.target.matches && event.target.matches(SELECTOR)) {
        refresh(event.target, false);
      }
    },
    true,
  );

  new MutationObserver((records) => {
    for (const record of records) record.addedNodes.forEach(refreshWithin);
  }).observe(document.documentElement, { childList: true, subtree: true });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => refreshWithin(document.body));
  } else {
    refreshWithin(document.body);
  }
})();
