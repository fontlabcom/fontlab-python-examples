# MenuTitle: GetGo - Masters Axes and Instances
# SPDX-License-Identifier: Apache-2.0
# this_file: examples/getgo/designspace.py
"""GG Cosm (CC0-1.0): report master, axis and eight export-instance coordinates.
Source font: https://code.fontlab.com/getgo-fonts/cosm-var/
Original example code: Apache-2.0. Design coordinates differ from user coordinates.
"""

from examples.getgo._shared import owned_font


def masters(package) -> dict:
    """Inspect a registered package; coordinates follow the reported axis order.

    User and design ranges differ. Native valueWeight reads design coordinates
    even when flLocation keys use axis short names. No master is selected.
    """
    axes, names = list(package.axes), list(package.masters)
    locations = [
        {
            "master": name,
            "coordinates": [
                float(axis.valueWeight(package.location(name), 0.0)) for axis in axes
            ],
        }
        for name in names
    ]
    return {
        "masters": names,
        "default_master": package.defaultMaster,
        "locations": locations,
        "axes": [
            {
                "name": a.name,
                "tag": a.tag,
                "short_name": a.shortName,
                "minimum": a.minimal,
                "default": a.default,
                "maximum": a.maximum,
                "design_minimum": a.designMin,
                "design_default": a.designDef,
                "design_maximum": a.designMax,
            }
            for a in axes
        ],
    }


def instance_rows(package) -> list[dict]:
    """Read instance locations in reported axis order using valueWeight."""
    axes = list(package.axes)
    return [
        {
            "name": instance.name,
            "exportable": bool(instance.exportable),
            "coordinates": [
                float(axis.valueWeight(instance.location, 0.0)) for axis in axes
            ],
        }
        for instance in package.instances
    ]


def run() -> dict:
    """Inspect the registered variable font without selecting another master."""
    with owned_font("cosm-var") as (package, record):
        selected = package.master
        result = {
            "source": record["page_url"],
            **masters(package),
            "instances": instance_rows(package),
        }
        if package.master != selected:
            raise AssertionError("Inspection changed the selected master")
        return result


if __name__ == "__main__":
    print(run())
