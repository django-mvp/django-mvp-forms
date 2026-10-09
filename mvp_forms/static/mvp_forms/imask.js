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
    if (kind === "dynamic") return { mask: rest.mask.map(build) };
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

  // The entry the form should hold for a masked input, or undefined to leave
  // the browser's own. The browser's stands whenever the mask is out of step
  // with the input, as it is after a reset or a value a script assigned.
  function entry(input, mask) {
    if (input.value !== mask.displayValue) return undefined;
    // A placeholder nothing was typed into is not a value.
    if (mask.masked.rawInputValue === "") return "";
    // A display character hides what was typed, and a pattern inside a list of
    // masks hides its display character from the outer mask.
    return mask.value === input.value ? undefined : mask.value;
  }

  function apply(input) {
    if (!window.IMask || masked.has(input)) return;
    let mask;
    try {
      mask = window.IMask(input, build(JSON.parse(input.dataset.imask)));
    } catch (error) {
      // Options IMask refuses cost this input its mask and no other input.
      console.error(input, error);
      return;
    }
    masked.set(input, mask);
    const form = input.form;
    if (form) {
      form.addEventListener("formdata", function (event) {
        if (input.form !== form || !input.name || input.matches(":disabled")) return;
        const value = entry(input, mask);
        if (value !== undefined) event.formData.set(input.name, value);
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
