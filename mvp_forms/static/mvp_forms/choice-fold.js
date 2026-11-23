// Folds the choices a chip or card widget marks behind its "More options"
// button. On load the marked choices that are not chosen are hidden and the
// button is shown. A click shows them in place, removes the button and moves
// the focus to the first choice shown. Without the script every choice is on
// show and the button stays hidden. Content added later, by a formset row or by
// htmx, is folded as it arrives.
(function () {
  "use strict";

  // A page may hold this script once for each form on it. Only the first acts.
  if (window.mvpFormsChoiceFold) return;
  window.mvpFormsChoiceFold = true;

  const MORE = "button[data-choice-more]";
  const FOLDED = "[data-choice-folded]";

  function inputOf(option) {
    return option.matches("input") ? option : option.querySelector("input");
  }

  function setHidden(option, hidden) {
    option.hidden = hidden;
    option.style.display = hidden ? "none" : "";
  }

  // Hide the marked choices next to a button that are not chosen and show the
  // button. A chosen choice is never folded. Running it again changes nothing.
  function fold(button) {
    const row = button.parentElement;
    const folded = Array.from(row.querySelectorAll(":scope > " + FOLDED));
    folded.forEach(function (option) {
      if (inputOf(option).checked) {
        option.removeAttribute("data-choice-folded");
      } else {
        setHidden(option, true);
      }
    });
    if (row.querySelector(":scope > " + FOLDED)) {
      button.hidden = false;
    } else {
      button.remove();
    }
  }

  function foldWithin(node) {
    if (node.nodeType !== Node.ELEMENT_NODE) return;
    if (node.matches(MORE)) fold(node);
    node.querySelectorAll(MORE).forEach(fold);
  }

  document.addEventListener("click", function (event) {
    const button = event.target.closest && event.target.closest(MORE);
    if (!button) return;
    const row = button.parentElement;
    const shown = Array.from(row.querySelectorAll(":scope > " + FOLDED));
    shown.forEach(function (option) {
      setHidden(option, false);
      option.removeAttribute("data-choice-folded");
    });
    button.remove();
    if (shown.length) inputOf(shown[0]).focus();
  });

  new MutationObserver(function (records) {
    records.forEach(function (record) {
      record.addedNodes.forEach(foldWithin);
    });
  }).observe(document.documentElement, { childList: true, subtree: true });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      foldWithin(document.body);
    });
  } else {
    foldWithin(document.body);
  }
})();
