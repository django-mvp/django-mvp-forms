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

  function block(options) {
    const { kind, ...rest } = options;
    if (kind === "range") return { mask: window.IMask.MaskedRange, ...rest };
    if (kind === "enum") return { mask: window.IMask.MaskedEnum, ...rest };
    return rest;
  }

  function build(options) {
    const { kind, ...rest } = options;
    if (kind === "regex") {
      return { mask: new RegExp(rest.mask, rest.flags || "") };
    }
    if (kind === "number") {
      return { mask: Number, ...rest };
    }
    if (kind === "dynamic") {
      return { mask: rest.mask.map(build) };
    }
    if (rest.definitions) {
      rest.definitions = Object.fromEntries(
        Object.entries(rest.definitions).map(([char, source]) => [
          char,
          new RegExp(source),
        ]),
      );
    }
    if (rest.blocks) {
      rest.blocks = Object.fromEntries(
        Object.entries(rest.blocks).map(([name, options]) => [
          name,
          block(options),
        ]),
      );
    }
    return rest;
  }

  function apply(input) {
    if (!window.IMask || masked.has(input)) return;
    const options = JSON.parse(input.dataset.imask);
    const plain = input.value;
    const mask = window.IMask(input, build(options));
    if (options.kind === "number" && plain) mask.unmaskedValue = plain;
    masked.set(input, mask);
    // A mask with a display character shows something other than its value, so
    // the form is given the value and not what is shown.
    if (mask.masked.displayChar && input.form) {
      input.form.addEventListener("formdata", function (event) {
        if (input.name && !input.disabled) event.formData.set(input.name, mask.value);
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
