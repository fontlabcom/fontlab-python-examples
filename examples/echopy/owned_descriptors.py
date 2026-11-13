# this_file: examples/echopy/owned_descriptors.py
"""Own a helper on a native class without replacing anything FontLab ships.

Echopy never rebinds a native member. ``install_extensions`` adds a helper only
where the name is free and reports ``installed``, ``existing`` or ``immutable``.
This example calls the helper through the installed attribute when it exists and
otherwise through ``get_extension``, so it works on immutable native classes too.
"""


def call_owned(obj, member, key, *args, specs=None):
    """Call ``obj.member`` when owned or native, else the extension function for ``key``."""
    from fontlab_echopy.extensions import get_extension

    bound = getattr(obj, member, None)
    if callable(bound):
        return bound(*args)
    return get_extension(key, specs)(obj, *args)


def main():
    from fly import fl
    from fontlab_echopy.extensions import install_extensions

    status = install_extensions()
    for key, state in sorted(status.items()):
        print(key, "->", state.split(";")[0])
    glyph = fl.flGlyph()  # a detached empty glyph; native flGlyph() takes no name
    print("layer_names:", call_owned(glyph, "layer_names", "fontlab.flGlyph.layer_names"))


if __name__ == "__main__":
    main()
