// Shows the image an image input holds: the stored one, or a newly chosen file
// before the form is sent. Choosing a file and removing the stored image are
// kept apart, because Django refuses a form that asks for both.
(function () {
  "use strict";

  // A page may hold this script once for each form on it. Only the first acts.
  if (window.mvpFormsImageInput) return;
  window.mvpFormsImageInput = true;

  const SELECTOR = "[data-image-input]";
  const PREVIEWS = new WeakMap();

  function parts(group) {
    const find = function (name) {
      return group.querySelector("[data-image-input-" + name + "]");
    };
    return {
      file: group.querySelector('input[type="file"]'),
      frame: find("frame"),
      preview: find("preview"),
      empty: find("empty"),
      emptyText: find("empty-text"),
      remove: find("remove"),
      status: find("status"),
      actions: find("actions"),
      revert: find("revert"),
      open: find("open"),
      hint: find("hint"),
    };
  }

  // Where the thumbnail opens the picker, its name says whether it adds an
  // image or changes the one shown, and so does the band shown over it.
  function name(p, showing) {
    if (!p.open) return;
    p.open.setAttribute("aria-label", showing ? p.open.dataset.change : p.open.dataset.add);
    if (p.hint) p.hint.hidden = !showing;
  }

  function showImage(p, url) {
    p.preview.src = url;
    p.preview.hidden = false;
    p.empty.hidden = true;
    name(p, true);
  }

  function showEmpty(p, message) {
    p.preview.hidden = true;
    p.preview.removeAttribute("src");
    p.empty.hidden = false;
    p.emptyText.textContent = message;
    name(p, false);
  }

  // The status line says what is waiting on the form being saved. Reverting is
  // offered while a chosen file waits; the remove checkbox is its own undo.
  function say(p, message, revert) {
    p.status.hidden = !message;
    p.status.textContent = message || "";
    p.revert.hidden = !revert;
    p.actions.hidden = !p.remove && !revert;
  }

  function release(group) {
    const url = PREVIEWS.get(group);
    if (url) URL.revokeObjectURL(url);
    PREVIEWS.delete(group);
  }

  // Draw the group from what it holds now.
  function draw(group) {
    const p = parts(group);
    const stored = group.dataset.imageInputStored;
    const file = p.file.files && p.file.files[0];
    release(group);
    p.frame.classList.toggle("opacity-50", Boolean(p.remove && p.remove.checked));
    if (file) {
      if (file.type.indexOf("image/") === 0) {
        const url = URL.createObjectURL(file);
        PREVIEWS.set(group, url);
        showImage(p, url);
        say(p, p.status.dataset.pending, true);
      } else {
        showEmpty(p, p.emptyText.dataset.unreadable);
        say(p, p.status.dataset.unreadable, true);
      }
      return;
    }
    if (stored) {
      if (p.preview.getAttribute("src") !== stored) showImage(p, stored);
    } else {
      showEmpty(p, p.emptyText.dataset.empty);
    }
    if (p.remove && p.remove.checked) {
      say(p, p.status.dataset.pending, false);
    } else {
      say(p, "", false);
    }
  }

  document.addEventListener("change", function (event) {
    const group = event.target.closest(SELECTOR);
    if (!group) return;
    const p = parts(group);
    if (event.target === p.file && p.file.files.length && p.remove) {
      p.remove.checked = false;
    }
    if (event.target === p.remove && p.remove.checked) {
      p.file.value = "";
    }
    draw(group);
  });

  document.addEventListener("click", function (event) {
    const open = event.target.closest("[data-image-input-open]");
    if (open) {
      parts(open.closest(SELECTOR)).file.click();
      return;
    }
    const revert = event.target.closest("[data-image-input-revert]");
    if (!revert) return;
    const group = revert.closest(SELECTOR);
    const p = parts(group);
    p.file.value = "";
    if (p.remove) p.remove.checked = false;
    draw(group);
    (p.open || p.file).focus();
  });

  // A stored image whose file is gone is drawn as missing, not as a broken
  // picture. The error event does not bubble, so it is heard while it is
  // captured.
  document.addEventListener(
    "error",
    function (event) {
      const preview = event.target;
      if (!(preview instanceof HTMLImageElement)) return;
      if (!preview.matches("[data-image-input-preview]")) return;
      const group = preview.closest(SELECTOR);
      const p = parts(group);
      if (PREVIEWS.get(group)) {
        showEmpty(p, p.emptyText.dataset.unreadable);
        say(p, p.status.dataset.unreadable, true);
      } else {
        showEmpty(p, p.emptyText.dataset.missing);
      }
    },
    true,
  );

  // A form sent back with an error, or restored by the browser's back button,
  // can hold a file already.
  // Where the thumbnail is the picker, the file input is taken out of sight
  // and out of the tab order only once this script runs, so a page without it
  // still has an input to use.
  function start() {
    document.querySelectorAll(SELECTOR).forEach(function (group) {
      const p = parts(group);
      if (p.open) {
        p.open.hidden = false;
        p.file.parentElement.classList.add("sr-only");
        p.file.tabIndex = -1;
      }
      draw(group);
      // A stored image that failed before this script was listening.
      if (p.preview.getAttribute("src") && p.preview.complete && !p.preview.naturalWidth) {
        showEmpty(p, p.emptyText.dataset.missing);
      }
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
