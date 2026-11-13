# this_file: examples/echopy/signature_reading.py
"""Read Echopy native-class signatures, with a fallback when none exist.

Run inside FontLab 9 with ``fontlab-fly`` and Echopy installed. Native
constructors are builtin types, so ``inspect.signature`` raises ``ValueError``
for them. This example reports that honestly instead of inventing a signature.
"""

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
    from fly import fl

    for name, row in report([fl.flNode, fl.flGlyph, fl.flLayer, fl.flPackage]).items():
        print(f"{name}{row['constructor']}  [{row['members']} public members]")


if __name__ == "__main__":
    main()
