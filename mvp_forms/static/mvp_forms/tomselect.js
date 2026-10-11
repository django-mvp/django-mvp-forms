// Starts a Tom Select control on every select a Tom Select widget draws, on
// the page as it loads and on each select added to it afterwards. The widget
// writes its settings on the select as JSON in data-tom-select. The page loads
// Tom Select itself, and on a page without it this script does nothing and
// each select stays a stock select. Once a control has started, the select
// sends mvp-forms:tomselect, which carries the Tom Select instance.
(function () {
  "use strict";

  // A page may hold this script once for each form on it. Only the first acts.
  if (window.mvpFormsTomselect) return;
  window.mvpFormsTomselect = true;

  const SELECTOR = "select[data-tom-select]";
  const EVENT = "mvp-forms:tomselect";
  // The only settings read from the attribute. Everything else is reached
  // through the control itself.
  const SETTINGS = ["placeholder", "maxItems", "plugins"];

  // Every option of the field is offered, however many there are.
  function settings(select) {
    const written = JSON.parse(select.dataset.tomSelect);
    const given = { maxOptions: null };
    SETTINGS.forEach(function (name) {
      if (name in written) given[name] = written[name];
    });
    return given;
  }

  function apply(select) {
    if (select.tomselect) return;
    let control;
    try {
      control = new window.TomSelect(select, settings(select));
    } catch (error) {
      // A select Tom Select refuses is left as it is, and no other select
      // loses its control for it.
      console.error(select, error);
      return;
    }
    // Help text and errors stay tied to the input that takes focus.
    const described = select.getAttribute("aria-describedby");
    if (described) control.control_input.setAttribute("aria-describedby", described);
    select.dispatchEvent(
      new CustomEvent(EVENT, { bubbles: true, detail: { tomselect: control } }),
    );
  }

  // The nodes Tom Select adds as it starts a control hold no select of ours,
  // so each costs one match and one search of its own children.
  function scan(node) {
    if (node.nodeType !== Node.ELEMENT_NODE) return;
    if (node.matches(SELECTOR)) apply(node);
    node.querySelectorAll(SELECTOR).forEach(apply);
  }

  function start() {
    if (typeof window.TomSelect !== "function") return;
    document.querySelectorAll(SELECTOR).forEach(apply);
    new MutationObserver(function (records) {
      records.forEach(function (record) {
        record.addedNodes.forEach(scan);
      });
    }).observe(document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === "complete") {
    start();
  } else {
    window.addEventListener("load", start);
  }
})();
