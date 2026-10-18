// Starts a Tom Select control on every select a Tom Select widget draws, on
// the page as it loads and on each select added to it afterwards, and destroys
// the control of each select that leaves the page. The widget writes its
// settings on the select as JSON in data-tom-select. The page loads Tom Select
// itself, and on a page without it this script does nothing and each select
// stays a stock select. Once a control has started, the select sends
// mvp-forms:tomselect, which carries the Tom Select instance.
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
  // The words a counted control shows, which the stylesheet reads from the box
  // that holds the chosen values.
  const WORDS = ["noneText", "countText"];

  function settings(select) {
    const written = JSON.parse(select.dataset.tomSelect);
    const given = { maxOptions: null }; // Offer every option, however many there are.
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
    WORDS.forEach(function (name) {
      if (name in select.dataset) control.control.dataset[name] = select.dataset[name];
    });
    select.dispatchEvent(
      new CustomEvent(EVENT, { bubbles: true, detail: { tomselect: control } }),
    );
  }

  // Tom Select keeps listeners on the document and the window for each control
  // until it is destroyed. A select moved within the page is back in it by the
  // time its records are read, so it keeps its control.
  function release(select) {
    if (select.tomselect && !select.isConnected) select.tomselect.destroy();
  }

  // The nodes Tom Select adds and removes as it draws a control hold no select
  // of ours, so each costs one match and one search of its own children.
  function each(node, act) {
    if (node.nodeType !== Node.ELEMENT_NODE) return;
    if (node.matches(SELECTOR)) act(node);
    node.querySelectorAll(SELECTOR).forEach(act);
  }

  function start() {
    if (typeof window.TomSelect !== "function") return;
    document.querySelectorAll(SELECTOR).forEach(apply);
    new MutationObserver(function (records) {
      records.forEach(function (record) {
        record.addedNodes.forEach(function (node) {
          each(node, apply);
        });
      });
      records.forEach(function (record) {
        record.removedNodes.forEach(function (node) {
          each(node, release);
        });
      });
    }).observe(document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === "complete") {
    start();
  } else {
    window.addEventListener("load", start);
  }
})();
