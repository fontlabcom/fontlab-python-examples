---
this_file: CHANGELOG.md
---

# Changelog

## Unreleased

- Read both launcher catalogs explicitly as UTF-8 in FontLab's ASCII-default
  embedded Python; preserve all Unicode metadata and source/resource bytes.
- Close/delete the Designer QFile when QUiLoader construction fails, with
  regression checks for constructor cleanup and ASCII-default Unicode lookup.

- Implement four original numbered examples as direct PythonQt ports: QLabel,
  QVBoxLayout, Signals and Slots and Qt Designer; preserve required UI bytes.
- Add import-safe named host launcher, retained native handles, JSON snapshots,
  scoped `OwnedWidget` cleanup and an ordinary Remopy example.
- Record individual MIT review, source IDs/hashes and pending native acceptance
  in a separate manifest without altering the complete static catalog.

- Catalog both complete pinned collections: 1,569 original files, 465 Python
  files, every resource and both case-distinct matplotlib source names.
- Add deterministic stdlib inventory tools, static source/API/resource analysis,
  conservative license evidence, planned port mappings and categorized navigation.
- Verify receipt/source mismatch failures and complete catalog coverage with
  19 tests; retain pending implementation, license review and native acceptance.

- Verified the first four source-loaded ports in actual FontLab, including alert dismissal/repeat, Designer results and observed owned-object teardown; preserved complete remaining collection scope.
