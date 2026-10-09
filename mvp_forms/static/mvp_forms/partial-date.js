// Keeps the three parts of a partial date in step: no month before a whole
// year, no day before a month, and only the days the month has in that year.
(function () {
  "use strict";

  // A page may hold this script once for each form on it. Only the first acts.
  if (window.mvpFormsPartialDate) return;
  window.mvpFormsPartialDate = true;

  const SELECTOR = "[data-partial-date]";

  function daysIn(year, month) {
    if (month === 2) {
      return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0 ? 29 : 28;
    }
    return [4, 6, 9, 11].includes(month) ? 30 : 31;
  }

  function part(group, name) {
    return group.querySelector('[data-partial-date-part="' + name + '"]');
  }

  // What a form was sent is shown as it was sent: a part that holds a value is
  // left alone until the person changes something.
  function sync(group, keep) {
    const year = part(group, "year");
    const month = part(group, "month");
    const day = part(group, "day");
    const whole = /^\d{4}$/.test(year.value) && Number(year.value) > 0;
    if (month) {
      month.disabled = year.disabled || !whole;
      if (!whole && !keep) month.value = "";
      if (keep && month.value !== "") month.disabled = year.disabled;
    }
    if (day) {
      const chosen = month.value !== "";
      day.disabled = month.disabled || !chosen;
      const length = chosen ? daysIn(Number(year.value), Number(month.value)) : 31;
      Array.from(day.options).forEach(function (option) {
        const beyond = option.value !== "" && Number(option.value) > length;
        const held = keep && option.selected;
        option.hidden = beyond && !held;
        option.disabled = beyond && !held;
      });
      if (keep && day.value !== "") day.disabled = year.disabled;
      else if (!chosen || Number(day.value) > length) day.value = "";
    }
  }

  function scan(root) {
    if (root.matches && root.matches(SELECTOR)) sync(root, true);
    if (root.querySelectorAll) {
      root.querySelectorAll(SELECTOR).forEach(function (group) {
        sync(group, true);
      });
    }
  }

  function changed(event) {
    const group = event.target.closest && event.target.closest(SELECTOR);
    if (group) sync(group);
  }

  function start() {
    scan(document);
    document.addEventListener("input", changed);
    document.addEventListener("change", changed);
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
