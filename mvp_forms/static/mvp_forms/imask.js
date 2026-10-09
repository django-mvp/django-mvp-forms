// Applies IMask to every input a mask widget draws. The widget writes its
// options on the input as JSON in data-imask. The page loads IMask itself, and
// on a page without it this script does nothing.
(function () {
  "use strict";

  // A page may hold this script once for each form on it. Only the first acts.
  if (window.mvpFormsImask) return;
  window.mvpFormsImask = true;

  const SELECTOR = "input[data-imask]";
  const EVENT = "mvp-forms:imask";
  const masked = new WeakMap();

  // A definition is an expression written as text, or an object holding the
  // expression and a placeholder character. A built-in definition has no
  // expression written, and IMask holds it.
  function definition(character, written) {
    const { mask, ...rest } = typeof written === "string" ? { mask: written } : written;
    const builtIn = window.IMask.MaskedPattern.InputDefinition.DEFAULT_DEFINITIONS;
    return { ...rest, mask: mask === undefined ? builtIn[character] : new RegExp(mask) };
  }

  function block(written) {
    const { kind, ...rest } = written;
    if (kind === "range") return { mask: window.IMask.MaskedRange, ...rest };
    if (kind === "enum") return { mask: window.IMask.MaskedEnum, ...rest };
    return rest;
  }

  function build(written) {
    const { kind, definitions, blocks, flags, ...rest } = written;
    if (kind === "regex") return { mask: new RegExp(rest.mask, flags) };
    if (kind === "number") return { mask: Number, ...rest };
    if (definitions) {
      rest.definitions = Object.fromEntries(
        Object.entries(definitions).map(([character, value]) => [
          character,
          definition(character, value),
        ]),
      );
    }
    if (blocks) {
      rest.blocks = Object.fromEntries(
        Object.entries(blocks).map(([name, value]) => [name, block(value)]),
      );
    }
    return rest;
  }

  function apply(input) {
    if (!window.IMask || masked.has(input)) return;
    const mask = window.IMask(input, build(JSON.parse(input.dataset.imask)));
    masked.set(input, mask);
    // What the input shows is not always what the form should receive: a
    // display character hides the digits typed, and a pattern inside a list of
    // masks hides its display character from the outer mask.
    const form = input.form;
    if (form) {
      form.addEventListener("formdata", function (event) {
        if (input.form === form && input.name && !input.disabled) {
          event.formData.set(input.name, mask.value);
        }
      });
    }
    input.dispatchEvent(
      new CustomEvent(EVENT, { bubbles: true, detail: { mask: mask } }),
    );
  }

  function scan(root) {
    if (root.matches && root.matches(SELECTOR)) apply(root);
    if (root.querySelectorAll) root.querySelectorAll(SELECTOR).forEach(apply);
  }

  function start() {
    scan(document);
    new MutationObserver(function (records) {
      records.forEach(function (record) {
        record.addedNodes.forEach(scan);
      });
    }).observe(document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
