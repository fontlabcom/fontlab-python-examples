# this_file: Scripts/Tools/Pair Proof Generator.py
# SPDX-License-Identifier: Apache-2.0
"""What: Generate current-font glyph pairs from two explicit name lists.
How: Combine all left/right names, or zip equal-length lists. Apply each side's
suffix, then validate every resulting name against the current font.
Why: Cartesian combinations expose spacing relationships absent from an
adjacent-pair proof. Unencoded alternates remain usable through slash names.
Usage: Enter space-separated names without slashes. Choose Product or Zip.
Optional fillers are name lists. Copy Fresh Result to a Glyph window text bar.
Benefit: Prepare every requested pair in stable order without editing kerning.
This tool generates proofs. Use File > Export > Metrics for AFM kerning output
and scriptmix Kerning > Classes Browser for class inspection.
scriptmix Kerning > Missing Pairs also builds Cartesian combinations, filtered
to missing kerning. This tool keeps all pairs and adds Zip, suffixes and fillers.
It does not extract existing-kerning proof strings or export KRN, Unicode
strings or OpenType class declarations.

Independent behaviour-only rewrite of the pair-generation idea from Pairs.py.
Credit: Vassil Kateliev and Karandash Type Foundry; kateliev/TypeRig, MPL-2.0.
No TypeRig code, comments, icons or resources are included.
Original profile setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Proof Composition Lab; opens the Pair Proof Generator profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E07", profile='Pair Proof Generator')


if __name__ == "__main__":
    main()
