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

  function daysIn(year, month) {
    if (month === 2) {
      return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0 ? 29 : 28;
    }
    return [4, 6, 9, 11].includes(month) ? 30 : 31;
  }

  // A number range whose first digit, when it can only be the whole part, is
  // given its leading zero: 4 as a month is 04.
  function paddedRange(first) {
    return class extends window.IMask.MaskedRange {
      _appendCharRaw(character, flags) {
        if (this.value === "" && character >= first && character <= "9") {
          return super
            ._appendCharRaw("0", flags)
            .aggregate(super._appendCharRaw(character, flags));
        }
        return super._appendCharRaw(character, flags);
      }
    };
  }

  // The first and last day a partial date could be, each as one number. The
  // first of a missing part is 1 and the last is 12 or 31.
  function limit(written, last) {
    const [year, month, day] = written.split("-").map(Number);
    return year * 10000 + (month || (last ? 12 : 1)) * 100 + (day || (last ? 31 : 1));
  }

  // The lowest and highest number a part cut off after some digits could still
  // become, given how many digits it has when whole.
  function reach(typed, digits, lowest, highest) {
    if (!typed) return [lowest, highest];
    const room = Math.pow(10, digits - typed.length);
    const from = Number(typed) * room;
    return [Math.max(from, lowest), Math.min(from + room - 1, highest)];
  }

  // A year, then a month and a day a person may leave off. A digit is refused
  // when no month, no day of the month typed, or no date the field accepts
  // could follow from it.
  function partialDate(resolution, min, max) {
    const Range = window.IMask.MaskedRange;
    const earliest = min ? limit(min, false) : 0;
    const latest = max ? limit(max, true) : Infinity;
    return {
      mask: { year: "Y", month: "Y-M", day: "Y-M-D" }[resolution || "day"],
      blocks: {
        Y: { mask: Range, from: 1, to: 9999, maxLength: 4 },
        M: { mask: paddedRange("2"), from: 1, to: 12, maxLength: 2 },
        D: { mask: paddedRange("4"), from: 1, to: 31, maxLength: 2 },
      },
      validate: function (value) {
        const [year, month, day] = value.split("-");
        const years = reach(year, 4, 1, 9999);
        const months = reach(month, 2, 1, 12);
        const length = month && month.length === 2 ? daysIn(Number(year), Number(month)) : 31;
        const days = reach(day, 2, 1, length);
        if (months[0] > months[1] || days[0] > days[1]) return false;
        const first = years[0] * 10000 + months[0] * 100 + days[0];
        const last = years[1] * 10000 + months[1] * 100 + days[1];
        return last >= earliest && first <= latest;
      },
    };
  }

  function build(written) {
    const { kind, definitions, blocks, flags, ...rest } = written;
    if (kind === "partial-date") return partialDate(rest.resolution, rest.min, rest.max);
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
