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

  // The first or last day a partial date could be, as one number.
  function limit(written, last) {
    const [year, month, day] = written.split("-").map(Number);
    return year * 10000 + (month || (last ? 12 : 1)) * 100 + (day || (last ? 31 : 1));
  }

  // Every option a select held when it was first met. Safari ignores `hidden`
  // on an option, so the options a part cannot take are taken out of the list
  // and put back from here.
  const LISTS = new WeakMap();

  // Put into a select only the options that can be chosen. One that is held is
  // kept when the form is first shown, and cleared after that.
  function offer(select, keep, allowed) {
    if (!LISTS.has(select)) LISTS.set(select, Array.from(select.options));
    const held = select.value;
    const wanted = LISTS.get(select).filter(function (option) {
      return (
        option.value === "" ||
        allowed(Number(option.value)) ||
        (keep && option.value === held)
      );
    });
    const shown = Array.from(select.options);
    const same =
      wanted.length === shown.length &&
      wanted.every(function (option, index) {
        return option === shown[index];
      });
    if (!same) select.replaceChildren.apply(select, wanted);
    select.value = wanted.some(function (option) {
      return option.value === held;
    })
      ? held
      : "";
  }

  // What a form was sent is shown as it was sent: a part that holds a value is
  // left alone until the person changes something.
  function sync(group, keep) {
    const year = part(group, "year");
    const month = part(group, "month");
    const day = part(group, "day");
    const earliest = group.dataset.partialDateMin ? limit(group.dataset.partialDateMin, false) : 0;
    const latest = group.dataset.partialDateMax ? limit(group.dataset.partialDateMax, true) : Infinity;
    const within = function (first, last) {
      return last >= earliest && first <= latest;
    };
    const years = Number(year.value) * 10000;
    const whole = /^\d{4}$/.test(year.value) && years > 0 && within(years + 101, years + 1231);
    if (month) {
      month.disabled = year.disabled || !whole;
      if (!whole && !keep) month.value = "";
      if (whole) {
        offer(month, keep, function (number) {
          return within(years + number * 100 + 1, years + number * 100 + 31);
        });
      }
      if (keep && month.value !== "") month.disabled = year.disabled;
    }
    if (day) {
      const chosen = month.value !== "";
      const months = years + Number(month.value) * 100;
      const length = chosen ? daysIn(Number(year.value), Number(month.value)) : 31;
      offer(day, keep, function (number) {
        return number <= length && (!chosen || within(months + number, months + number));
      });
      day.disabled = month.disabled || !chosen;
      if (keep && day.value !== "") day.disabled = year.disabled;
      else if (!chosen) day.value = "";
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
