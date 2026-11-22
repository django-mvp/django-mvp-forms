// Keeps a choice chosen inside a closed fold on show, and the count of the
// choices still folded true. Without it the fold still opens and every choice
// in it can be chosen and sent.
(function () {
  "use strict";

  // A page may hold this script once for each form on it. Only the first acts.
  if (window.mvpFormsChoiceFold) return;
  window.mvpFormsChoiceFold = true;

  const FOLD = "details[data-choice-fold]";
  const OPTION = "[data-choice-index]";

  function chosen(option) {
    return option.matches(":checked") || option.querySelector("input:checked") !== null;
  }

  // Put an option among the choices on show where the field's order puts it.
  function place(shown, option) {
    const index = Number(option.dataset.choiceIndex);
    const later = Array.from(shown.children).find(function (each) {
      return Number(each.dataset.choiceIndex) > index;
    });
    shown.insertBefore(option, later || null);
  }

  // The words for a count: the package's own, held in the summary, or the
  // number alone after the developer's.
  function words(summary, count) {
    const own = count === 1 ? summary.dataset.choiceOne : summary.dataset.choiceOther;
    return own ? own.replace("{n}", String(count)) : String(count);
  }

  // The toggle event does not bubble, so it is heard in the capture phase.
  document.addEventListener(
    "toggle",
    function (event) {
      const fold = event.target;
      if (!(fold instanceof Element) || !fold.matches(FOLD) || fold.open) return;
      const shown = fold.parentElement.querySelector(":scope > [data-choice-shown]");
      if (!shown) return;
      Array.from(fold.querySelectorAll(OPTION))
        .filter(chosen)
        .forEach(function (option) {
          place(shown, option);
        });
      const left = fold.querySelectorAll(OPTION).length;
      if (left === 0) {
        fold.remove();
        return;
      }
      const count = fold.querySelector("[data-choice-count]");
      if (count) count.textContent = words(fold.querySelector("summary"), left);
    },
    true
  );
})();
