---
this_file: src_docs/md/echopy-native-examples.md
---

# Echopy native signatures and owned helpers

Two runnable examples show how to read what Echopy declares for FontLab's
native classes, and how to add a helper of your own without replacing anything
FontLab ships. Both live in `examples/echopy/` and run inside FontLab 9 with
`fontlab_echopy` installed.

## Read a signature, or say there is none

FontLab's native classes are builtin types. `inspect.signature` raises
`ValueError` for their constructors, so the example catches that and prints the
conservative `(*args, **kwargs)` form. Look in the shipped `.pyi` declarations
for the real parameters. The example never guesses.

```python
import inspect

UNAVAILABLE = "(*args, **kwargs)  # no runtime signature; see the shipped .pyi"


def read_signature(target):
    """Return ``(text, known)``; ``known`` is False when Python has no signature."""
    try:
        return str(inspect.signature(target)), True
    except (ValueError, TypeError):
        return UNAVAILABLE, False


def public_members(cls):
    """Public attribute names a facade class exposes."""
    return sorted(name for name in dir(cls) if not name.startswith("_"))


def report(classes):
    """Map each class name to its constructor signature text and member count."""
    return {cls.__name__: {"constructor": read_signature(cls)[0], "members": len(public_members(cls))} for cls in classes}


def main():
    from echopy import fontlab as fl

    for name, row in report([fl.flNode, fl.flGlyph, fl.flLayer, fl.flPackage]).items():
        print(f"{name}{row['constructor']}  [{row['members']} public members]")


if __name__ == "__main__":
    main()
```

Verified live in FontLab 9: `flNode`, `flGlyph`, `flLayer` and `flPackage` each
print the fallback signature with their public member counts (118, 129, 186 and
229).

## Own a helper without changing native classes

Echopy never rebinds a native member. `install_extensions` adds a helper only
where the name is free and reports `installed`, `existing` or `immutable`.
When a class is immutable, call the helper through `get_extension` instead.

```python
def call_owned(obj, member, key, *args, specs=None):
    """Call ``obj.member`` when owned or native, else the extension function for ``key``."""
    from fontlab_echopy.extensions import get_extension

    bound = getattr(obj, member, None)
    if callable(bound):
        return bound(*args)
    return get_extension(key, specs)(obj, *args)


def main():
    from echopy import fontlab as fl
    from fontlab_echopy.extensions import install_extensions

    status = install_extensions()
    for key, state in sorted(status.items()):
        print(key, "->", state.split(";")[0])
    glyph = fl.flGlyph()  # a detached empty glyph; native flGlyph() takes no name
    print("layer_names:", call_owned(glyph, "layer_names", "fontlab.flGlyph.layer_names"))


if __name__ == "__main__":
    main()
```

Verified live in FontLab 9: `flGlyph` reports `immutable` for `has_layer` and
`layer_names`, so the helper is reached through `get_extension`, and a detached
empty glyph returns an empty layer list. `flGlyph()` takes no name.
