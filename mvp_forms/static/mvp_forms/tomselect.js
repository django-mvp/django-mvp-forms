// Starts a Tom Select control on every select a Tom Select widget draws. The
// widget writes its settings on the select as JSON in data-tom-select. The
// page loads Tom Select itself, and on a page without it this script does
// nothing and each select stays a stock select.
(function () {
  "use strict";

  // A page may hold this script once for each form on it. Only the first acts.
  if (window.mvpFormsTomselect) return;
  window.mvpFormsTomselect = true;

  const SELECTOR = "select[data-tom-select]";
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
  }

  function start() {
    if (typeof window.TomSelect !== "function") return;
    document.querySelectorAll(SELECTOR).forEach(apply);
  }

  if (document.readyState === "complete") {
    start();
  } else {
    window.addEventListener("load", start);
  }
})();
