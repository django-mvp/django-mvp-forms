# Tom Select 2.7.0

A copy of [Tom Select](https://tom-select.js.org/) 2.7.0, which the `TomSelect` and
`TomSelectMultiple` widgets name in their media. It is distributed under the Apache License,
Version 2.0, in `LICENSE` beside this file.

Both files come from the `tom-select` package on npm, version 2.7.0:

| File here | File in the npm package | SHA-256 of the npm file |
|---|---|---|
| `tom-select.complete.min.js` | `dist/js/tom-select.complete.min.js` | `5c1315fe8e62c7b9342cbf82c4d5454b83ab97d507a2e9803dbaef72433438bc` |
| `tom-select.min.css` | `dist/css/tom-select.min.css` | `ff5c963f8d96eff3c50b0eb456cc3bc1a545ff618a5bad77202fed22c8b2c030` |

Two changes are made to them, and no other:

- The script is placed inside `if (typeof window.TomSelect !== "function") { … }`, so it runs
  only on a page that has no Tom Select yet.
- The `sourceMappingURL` comment is removed from both, because the source maps are not
  distributed.

The complete build is the one that registers every plugin the widgets can name:
`clear_button`, `remove_button`, `checkbox_options` and `dropdown_input`.
