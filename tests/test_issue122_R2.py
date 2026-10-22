# this_file: tests/test_issue122_R2.py
# SPDX-License-Identifier: Apache-2.0
"""Audit source dispositions without importing or executing third-party bodies.

What: Check all ninety identities, reasons, licences and exact source bytes.
How: Compare the independent rescue index and frozen batch with the records.
Why: Equal bytes do not make two source identities interchangeable.
Usage: Run this file with the installed App and real Fly on PYTHONPATH.
Benefit: Keep retirement evidence reproducible without starting foreign hosts.
Native fakes below are guard checks only; no runtime menu is added or accepted.
"""

import ast
import hashlib
import importlib
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
PRESERVED = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
SHARED = ROOT / "menu-adaptations.json"
IDENTITIES = (
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - Editor - indent2 -- 50bc59af4413.py', 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/Editor/indent2.py', '0b6345e7036af693bbfb3d2fabd660c87302a3ecf09c3cc09ad0cebc63cd58bf'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - scripts - atlasHealthPanel -- a8fc854a0efc.py', 'rescued/part3/sources/openhumanoids_director/src/python/scripts/atlasHealthPanel.py', '0e45770b8ae90e6c6f845abd384a093081a2e61b083ecc03bd526bfc58749e20'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - scripts - drakeViewer -- a3f42750154c.py', 'rescued/part3/sources/openhumanoids_director/src/python/scripts/drakeViewer.py', '3ebb04983927132eccb8625a3804c4d221b92f79dec6a71b939fa176e534f71a'),
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - LiveCoding - bytesong - bytesong -- a0bb7569538f.py', 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/LiveCoding/bytesong/bytesong.py', '616e025143000ec66217eaf5cfc0d5f6d6b2a73fccc67cc45f2dc8e3d87c1696'),
    ('Scripts/Archived Reference/P3 Sources - Bluscream_pyTSon_plugins - scripts - channelGroupManager - __init__ -- a53d1119bebc.py', 'rescued/part3/sources/Bluscream_pyTSon_plugins/scripts/channelGroupManager/__init__.py', 'f99c70b0e11c813defa7e12e0dcfe9084ac0a995431dfdc72da910caa55a8f85'),
    ('Scripts/Archived Reference/P3 Sources - eryar_PipeCAD - lib - pipecad - __init__ -- 126abde76ca2.py', 'rescued/part3/sources/eryar_PipeCAD/lib/pipecad/__init__.py', '3ae7a3cc4f4ff364ff45e53a626dd142675647e2f853c3bf1689a4ad94c02cc8'),
    ('Scripts/Archived Reference/P3 Sources - jcfr_PythonQt - examples - PyScriptingConsole - example -- de08b4b212e5.py', 'rescued/part3/sources/jcfr_PythonQt/examples/PyScriptingConsole/example.py', '47f8c26a441356be5b789d7a5682ce4a67d4cfb7230ed42dae54e120df9b08f2'),
    ('Scripts/Archived Reference/P3 Sources - Slicer_SlicerGitSVNArchive - Utilities - Scripts - qrcc -- 6189ed746ae3.py', 'rescued/part3/sources/Slicer_SlicerGitSVNArchive/Utilities/Scripts/qrcc.py', 'ad8f64ff690e8145a8a0ab9f37e836007b1f12e87308a654aebd1d51fe7ee135'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Tutorial - 04_Using_Qt -- 414f62d07eb9.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Tutorial/04_Using_Qt.py', '1e2a200291b6832e6f858c7e4f033ec67e8b6073c90724ca07c766de7231b6d5'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - tests - testRosPlugin -- 5a6c79fe2da4.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/tests/testRosPlugin.py', '348613a416bf09d250b1639f8ce1d0f66f12e3b4bb8d2f8910478dacb51dbb8c'),
    ('Scripts/Archived Reference/P3 Sources - knossos-project_knossos - python - user - custom_graphics_view -- c015a0126813.py', 'rescued/part3/sources/knossos-project_knossos/python/user/custom_graphics_view.py', 'ade1e6d73dbefc75edcd685f0ca2a4262a7f4c0b3d0889e4c1d5796807b290dd'),
    ('Scripts/Archived Reference/P3 Sources - Belsepubi_naali - bin - pymodules - localscene - loader -- 06dd307b4794.py', 'rescued/part3/sources/Belsepubi_naali/bin/pymodules/localscene/loader.py', 'e315c0d1843b72b6337502d819b6bd14d7cd676b4964a0661074702a8ebee438'),
    ('Scripts/Archived Reference/P3 Sources - carthurs_CRIMSONPythonModules - test -- defae7fe69f6.py', 'rescued/part3/sources/carthurs_CRIMSONPythonModules/test.py', 'a0481c1dabfcac2b971ba86d8088b1bc54bb801c9d4939cbb3f3f570498ffe84'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - director - consoleapp -- 073174dd7ad8.py', 'rescued/part3/sources/openhumanoids_director/src/python/director/consoleapp.py', 'f0b19aabaf8511cfb7e20968d55aca9af155334c72d620cc8f95866d89089115'),
    ('Scripts/Archived Reference/P3 Sources - jonnenauha_naali - bin - pymodules - localscene - loader -- ad7d2ad63a02.py', 'rescued/part3/sources/jonnenauha_naali/bin/pymodules/localscene/loader.py', 'e315c0d1843b72b6337502d819b6bd14d7cd676b4964a0661074702a8ebee438'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - WIP - ftable_viewer -- 0a81cf0fdd35.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/WIP/ftable_viewer.py', '9a9939a6f34a8043cd007de32a849f9b3c149738e90359ef835f247b173a5da5'),
    ('Scripts/Archived Reference/P3 Sources - knossos-project_knossos - python - examples - graphics_view -- 5e7aa976f62b.py', 'rescued/part3/sources/knossos-project_knossos/python/examples/graphics_view.py', '052c07188fc22262b362d092d7cf85eb17cff0496651b28f609a2cca0963b67c'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - invalue_chnget -- 3cf3c43ad8f9.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Editor/invalue_chnget.py', '71daae5ad508f2d0e563153855528ef1ff5e0f6b8549311a62c48ef3e90c201b'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - tests - testTaskQueue -- 26a64b770336.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/tests/testTaskQueue.py', '901e5c81c51e4a570c23e8b258f2dcb11fe795d787e95f0742515874c7145d8b'),
    ('Scripts/Archived Reference/P3 Sources - carthurs_CRIMSONPythonModules - upgradeScene -- 855bace19da3.py', 'rescued/part3/sources/carthurs_CRIMSONPythonModules/upgradeScene.py', '0b8b1144d4db0f15ac122a58eaa451d15d22e1c182b8d2358139e8c82f034a6c'),
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - Editor - strset_list -- 87b8485f3ca0.py', 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/Editor/strset_list.py', 'ab94e3837566b26468ce9d0348df4bbad1a3eb58f90cd44b7871a333527af167'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - app - WrapPythonQt -- e1f1724a6b9b.py', 'rescued/part3/sources/openhumanoids_director/src/app/WrapPythonQt.py', '72938ac6f0df23b31b8b72cfa851c63649e496c5c84ee4bdfca3d61c4f38b00e'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - director - mainwindowapp -- 34a44c939e9d.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/director/mainwindowapp.py', '842d3b0fcb201d3681ea0670a7f875ce830232b75f48b79b844b0c098ae9b91f'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - tests - testTaskQueue -- 7e3ae994f9c9.py', 'rescued/part3/sources/openhumanoids_director/src/python/tests/testTaskQueue.py', '901e5c81c51e4a570c23e8b258f2dcb11fe795d787e95f0742515874c7145d8b'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - director - robotposegui -- 9ac99f81fade.py', 'rescued/part3/sources/openhumanoids_director/src/python/director/robotposegui.py', '87381577e34bf26e439894a306e1f2d5f885ea88f1da455a03c38672b853e281'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - tests - testAtlasCommand -- 8399d02036e6.py', 'rescued/part3/sources/openhumanoids_director/src/python/tests/testAtlasCommand.py', 'e9625843ddf39808e93862ee9ca9f35ca8f82b1d5a6193f8c1066769e233f7e5'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - indent2 -- 0c02b8767224.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Editor/indent2.py', '0b6345e7036af693bbfb3d2fabd660c87302a3ecf09c3cc09ad0cebc63cd58bf'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - director - mainwindowapp -- 6c9bc00d1527.py', 'rescued/part3/sources/openhumanoids_director/src/python/director/mainwindowapp.py', '3305f0ffb7e6b6ef42bf5799c11e4f45076f6344c6ffb52c0754e2b93b53bb6e'),
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - OpenGL - openGL -- 40fe7decaef1.py', 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/OpenGL/openGL.py', '43e6c1cf0f1b650c0744351b7b265610858183809308462445ceb6f1294e7f4e'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - LiveCoding - bytesong - bytesong -- f72906f79bc3.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/LiveCoding/bytesong/bytesong.py', '616e025143000ec66217eaf5cfc0d5f6d6b2a73fccc67cc45f2dc8e3d87c1696'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - scripts - cameraViewer -- f187483f71dc.py', 'rescued/part3/sources/openhumanoids_director/src/python/scripts/cameraViewer.py', '545aea86789535e21d95299eff5273de1b12e771962815c801dc75329a5e8ac1'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - tests - testAtlasCommand -- a0dc0644e54c.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/tests/testAtlasCommand.py', 'c334add3307728c762ec3a2dac270014881b1d4aef260f25836aab4ca2aa9d5e'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - scripts - atlasRecoveryPanel -- 83fa155cfeb6.py', 'rescued/part3/sources/openhumanoids_director/src/python/scripts/atlasRecoveryPanel.py', '7f006660de46abad41e3618db341bc61882c11643cad0d2bc969ed103cdef011'),
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - Useful - UI_with_QtDesigner -- 77b62bb6235a.py', 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/Useful/UI_with_QtDesigner.py', '1b1e67db765f980ecce69ba9fb4fd153127a2f303c76d8b75888f24f0e1c57a6'),
    ('Scripts/Archived Reference/P3 Sources - knossos-project_knossos - python - examples - sreenshot -- 46c74d7d0cc1.py', 'rescued/part3/sources/knossos-project_knossos/python/examples/sreenshot.py', 'a8c1ea1061c600074f0dd47543da947969ba42441149512e694825e46eeede3b'),
    ('Scripts/Archived Reference/P3 Sources - carthurs_CRIMSONPythonModules - upgradeScene2 -- f0bd81f0d143.py', 'rescued/part3/sources/carthurs_CRIMSONPythonModules/upgradeScene2.py', '702386cf7bd60d44e553f18fa75679e76f41fa54d2ef530c7117826e84f1ddef'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - director - drakevisualizer -- bd8f9cdd251c.py', 'rescued/part3/sources/openhumanoids_director/src/python/director/drakevisualizer.py', '7701bf5e09e69a8b63aa0c6547cf9635ab7630cc838056b350b6319714d7395c'),
    ('Scripts/Archived Reference/P3 Sources - Bluscream_pyTSon_plugins - scripts - serverBrowser - __init__ -- 325e21ccdad5.py', 'rescued/part3/sources/Bluscream_pyTSon_plugins/scripts/serverBrowser/__init__.py', 'ff044e0ec53e4e6a905fa9a45123f9d92a401f152f8235eb42ea271fcef21720'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Color Organ - color-controller -- 2ae1da313a2c.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Color Organ/color-controller.py', 'ba44687a1a3d2a57bb7c2d5db0afa701ffec2b9c62616d7a16aaa2c13218c153'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - scripts - videoPlayer -- 917795e42e41.py', 'rescued/part3/sources/openhumanoids_director/src/python/scripts/videoPlayer.py', '4f1c2b5078d4eb1f710990c0d913915905bda6364d53c71748bb017b1757e4f0'),
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - bin - osx-package -- a2f2cc3bd1d0.py', 'rescued/part3/sources/hlolli_CsoundQt/bin/osx-package.py', '63af049a8a8b0558fe50e2e1ae7544c589a3d0505c1a428503d0faf0cb9f72aa'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - director - depthscanner -- 63584935d64a.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/director/depthscanner.py', 'e407306988e425a3d48a1fc527fa8b5c4e25ccb91390add5be08feb80c507c86'),
    ('Scripts/Archived Reference/P3 Sources - jonnenauha_naali - bin - pymodules - apitest - chessview - chessviewcontrol -- 9fbe92a19797.py', 'rescued/part3/sources/jonnenauha_naali/bin/pymodules/apitest/chessview/chessviewcontrol.py', 'c1d571a82330def421902d73f1f884e2dc62ecb8b10d7158a1d377d19453f256'),
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - WIP - ftable_viewer -- 87547c8db82d.py', 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/WIP/ftable_viewer.py', '9a9939a6f34a8043cd007de32a849f9b3c149738e90359ef835f247b173a5da5'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - scripts - atlasHealthPanel -- deb0f5408f4d.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/scripts/atlasHealthPanel.py', '0e45770b8ae90e6c6f845abd384a093081a2e61b083ecc03bd526bfc58749e20'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - rem_newline -- 610a1dd9c66c.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Editor/rem_newline.py', 'b8e8d63f9609c10043d7c92a2e0a8141a6deb24f8e400f41fa2134d51e72a057'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - scripts - drakeViewer -- 830e3145ecdc.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/scripts/drakeViewer.py', '3ebb04983927132eccb8625a3804c4d221b92f79dec6a71b939fa176e534f71a'),
    ('Scripts/Archived Reference/P3 Sources - cvetan5_naali - src - Application - PythonScriptModule - pymodules_old - apitest - chessview - chessviewcontrol -- 52c0ac3af3af.py', 'rescued/part3/sources/cvetan5_naali/src/Application/PythonScriptModule/pymodules_old/apitest/chessview/chessviewcontrol.py', '98bb14bcecd8ca1c8587b242984c6193a2d05994957e52f39297d829fce53a99'),
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - Tutorial - 04_Using_Qt -- 11d64d7977aa.py', 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/Tutorial/04_Using_Qt.py', '1e2a200291b6832e6f858c7e4f033ec67e8b6073c90724ca07c766de7231b6d5'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - app - WrapPythonQt -- 598a9dc27acb.py', 'rescued/part3/sources/RobotLocomotion_director/src/app/WrapPythonQt.py', 'b499249f3dfcf58b3a4c989fd18d66ac5e51d53a581950c3cad20d75e12e4504'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - invalues_for_widgets -- c17168f00f7e.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Editor/invalues_for_widgets.py', '1cb7f611f7ccb5ab577a30992f867019cdb7197ea5e5a5f1e35d32c2f3e63db9'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - director - robotposegui -- c3d6a4012020.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/director/robotposegui.py', 'ab3cb932dc1f54e02befd9884b06eacf033280ce3f0c8d77f0737d35da9319ce'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - tests - testFrameSync -- b51bb48a1648.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/tests/testFrameSync.py', 'e1e48d989138c8db81781c2672338993186cab9933bddd05526633e11a764a77'),
    ('Scripts/Archived Reference/P3 Sources - Slicer_SlicerGitSVNArchive - Utilities - Scripts - genqrc -- d21c5122a083.py', 'rescued/part3/sources/Slicer_SlicerGitSVNArchive/Utilities/Scripts/genqrc.py', 'eaa8a0be0ff99ebb24ee9de1d0476c40672bbb90188571fb3dba712e975692b5'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - scripts - atlasControlPanel -- bc692cad05e1.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/scripts/atlasControlPanel.py', '160ad911025dd17ff052b9088c62d7c562b48cfd88459d5eb3716ccb80dd72ff'),
    ('Scripts/Archived Reference/P3 Sources - jonnenauha_naali - bin - pymodules - localscene - dotscene -- b72fc92e8207.py', 'rescued/part3/sources/jonnenauha_naali/bin/pymodules/localscene/dotscene.py', '283255496c74afc4a98da927c372bf1187a699b0fd27fbf207a08899918e1bcd'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - strset_list -- 81da36a4000a.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Editor/strset_list.py', 'ab94e3837566b26468ce9d0348df4bbad1a3eb58f90cd44b7871a333527af167'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - director - consoleapp -- 1bee2af7b147.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/director/consoleapp.py', '819f468c91af52ea8873b481c73500cc14cba846cc072e8a74fb93cc26b7c115'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Useful - nanokontrol -- b47420cee429.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Useful/nanokontrol.py', 'f493a14821f8ce40b75c53f04e25f8d8a9f6b3c4816b4ea7648ece2cf74c16be'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - tests - testPropertiesPanel -- c2fa6435b02f.py', 'rescued/part3/sources/openhumanoids_director/src/python/tests/testPropertiesPanel.py', '7eeeffaecd6c901fc10aa465be15aa2f18dfbcfc43269a1c78cb693e4633f32e'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - tests - testPythonConsole -- da8ce4485a20.py', 'rescued/part3/sources/openhumanoids_director/src/python/tests/testPythonConsole.py', 'dfb110eaa15d9a7a2271d752cb534db829ac9489fa6d62d26c29073eb8d7473c'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - scripts - atlasControlPanel -- 806d8444d7ea.py', 'rescued/part3/sources/openhumanoids_director/src/python/scripts/atlasControlPanel.py', '160ad911025dd17ff052b9088c62d7c562b48cfd88459d5eb3716ccb80dd72ff'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - director - lcmlogplayer -- 40fed262c84a.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/director/lcmlogplayer.py', '580d9b5ec0887fcad17e50b75bc276a0bf567cac84309a2101c2bb0c1d665ac3'),
    ('Scripts/Archived Reference/P3 Sources - jcfr_PythonQt - examples - PyGuiExample - example -- 3e4a6176d468.py', 'rescued/part3/sources/jcfr_PythonQt/examples/PyGuiExample/example.py', '47f8c26a441356be5b789d7a5682ce4a67d4cfb7230ed42dae54e120df9b08f2'),
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - Editor - rem_newline -- aa354346b2df.py', 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/Editor/rem_newline.py', '58f77fed6d4f79e7b290ec55f35913f6a502332a20fc16e22adec4ee0cf65d30'),
    ('Scripts/Archived Reference/P3 Sources - Slicer_SlicerGitSVNArchive - Base - Python - tpycl - tpycl -- c5606d645ce6.py', 'rescued/part3/sources/Slicer_SlicerGitSVNArchive/Base/Python/tpycl/tpycl.py', '8291bac79505f1fe2c53c9847c7e4027b35ddec1990895398a2e9d71d602e541'),
    ('Scripts/Archived Reference/P3 Sources - Belsepubi_naali - bin - pymodules - localscene - dotscene -- d3944f3cb203.py', 'rescued/part3/sources/Belsepubi_naali/bin/pymodules/localscene/dotscene.py', '283255496c74afc4a98da927c372bf1187a699b0fd27fbf207a08899918e1bcd'),
    ('Scripts/Archived Reference/P3 Sources - cvetan5_naali - src - Application - PythonScriptModule - pymodules_old - localscene - loader -- 37078ac88917.py', 'rescued/part3/sources/cvetan5_naali/src/Application/PythonScriptModule/pymodules_old/localscene/loader.py', '7e3b073e4110ac5d2c5da201d2c9bd9d0189703a6a9529cc6677d7a7032bf7ca'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - scripts - videoPlayer -- f623d99f5e8d.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/scripts/videoPlayer.py', '4f1c2b5078d4eb1f710990c0d913915905bda6364d53c71748bb017b1757e4f0'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - director - imageviewapp -- 5203ecb953fd.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/director/imageviewapp.py', '181f82e7e9fec07784495304f93096f0a5e7e3e7c533fd801525437085902eec'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - tests - testObjectModel -- acb32f96c687.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/tests/testObjectModel.py', '1cce58964d8df1c43208c0b1a5f15cd1e47c6a6638683a2694f02998a02486cc'),
    ('Scripts/Archived Reference/P3 Sources - DAIRLab_dairlib - director - scripts - VisualizationGUI -- d6f1336a7f6b.py', 'rescued/part3/sources/DAIRLab_dairlib/director/scripts/VisualizationGUI.py', 'b0989ff9dc680d346bf0630427757b5928ddac1aa30d92ef778fe299860527d1'),
    ('Scripts/Archived Reference/P3 Sources - jcfr_PythonQt - examples - PyGettingStarted - GettingStarted -- 8fb96012cf02.py', 'rescued/part3/sources/jcfr_PythonQt/examples/PyGettingStarted/GettingStarted.py', '4fc610f527f167857b170115f69345a5c231cf1cc624614c9763340d49e07d30'),
    ('Scripts/Archived Reference/P3 Sources - cvetan5_naali - src - Application - PythonScriptModule - pymodules_old - localscene - dotscene -- 23229743bc55.py', 'rescued/part3/sources/cvetan5_naali/src/Application/PythonScriptModule/pymodules_old/localscene/dotscene.py', '214988c3b5338b12163a361b5dcf956de41ee434bd6057168dfaabde573d0af6'),
    ('Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Koenig-Essay - Koenig-Essay -- 63190a3ce39c.py', 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Koenig-Essay/Koenig-Essay.py', '34d579e230f7f163cab616cd1f43652f8b834951e4f1273b37f9f3ab03641e5c'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - tests - testObjectModel -- 811954286396.py', 'rescued/part3/sources/openhumanoids_director/src/python/tests/testObjectModel.py', '1cce58964d8df1c43208c0b1a5f15cd1e47c6a6638683a2694f02998a02486cc'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - docs - sphinx - tutorials - visualization - basicView1 -- d3658da79b7d.py', 'rescued/part3/sources/openhumanoids_director/docs/sphinx/tutorials/visualization/basicView1.py', '04cedc83dd853e85db58e49812e10e45129f14fbf6fbc7ad5fb1f1c7bb975e79'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - docs - sphinx - tutorials - visualization - basicView1 -- 669818329a9d.py', 'rescued/part3/sources/RobotLocomotion_director/docs/sphinx/tutorials/visualization/basicView1.py', '04cedc83dd853e85db58e49812e10e45129f14fbf6fbc7ad5fb1f1c7bb975e79'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - tests - testPythonConsole -- c1627d6b18a1.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/tests/testPythonConsole.py', 'dfb110eaa15d9a7a2271d752cb534db829ac9489fa6d62d26c29073eb8d7473c'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - scripts - atlasRecoveryPanel -- 5960c498ac0d.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/scripts/atlasRecoveryPanel.py', '7f006660de46abad41e3618db341bc61882c11643cad0d2bc969ed103cdef011'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - director - depthscanner -- 207c7a11f7e4.py', 'rescued/part3/sources/openhumanoids_director/src/python/director/depthscanner.py', '3c2e348c89a6102a4df5b0c265881da87382b66088f36a37e55972a329409985'),
    ('Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - Editor - invalue_chnget -- b934c1d9cea9.py', 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/Editor/invalue_chnget.py', '71daae5ad508f2d0e563153855528ef1ff5e0f6b8549311a62c48ef3e90c201b'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - tests - testPropertiesPanel -- c28e4642fd82.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/tests/testPropertiesPanel.py', '7eeeffaecd6c901fc10aa465be15aa2f18dfbcfc43269a1c78cb693e4633f32e'),
    ('Scripts/Archived Reference/P3 Sources - RobotLocomotion_director - src - python - scripts - cameraViewer -- b1ee14099988.py', 'rescued/part3/sources/RobotLocomotion_director/src/python/scripts/cameraViewer.py', '545aea86789535e21d95299eff5273de1b12e771962815c801dc75329a5e8ac1'),
    ('Scripts/Archived Reference/P3 Sources - Belsepubi_naali - bin - pymodules - apitest - chessview - chessviewcontrol -- 4a1a74766b03.py', 'rescued/part3/sources/Belsepubi_naali/bin/pymodules/apitest/chessview/chessviewcontrol.py', 'c1d571a82330def421902d73f1f884e2dc62ecb8b10d7158a1d377d19453f256'),
    ('Scripts/Archived Reference/P3 Sources - HopeFOAM_HopeFOAM - ThirdParty-0.1 - ParaView-5.0.1 - Plugins - PythonQtPlugin - WrapPythonQt -- 12a62820f848.py', 'rescued/part3/sources/HopeFOAM_HopeFOAM/ThirdParty-0.1/ParaView-5.0.1/Plugins/PythonQtPlugin/WrapPythonQt.py', '891ae8b20cbf040e0422504a7e2cd11b1fec7e75cb8a6c073fa32488213408a8'),
    ('Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - python - tests - testFrameSync -- d63d4e55feab.py', 'rescued/part3/sources/openhumanoids_director/src/python/tests/testFrameSync.py', 'e1e48d989138c8db81781c2672338993186cab9933bddd05526633e11a764a77'),
    ('Scripts/Archived Reference/P3 Sources - DAIRLab_dairlib - examples - Cassie - director_scripts - pd_panel -- ec9c61763bc8.py', 'rescued/part3/sources/DAIRLab_dairlib/examples/Cassie/director_scripts/pd_panel.py', 'b682e3e6103617987947921d00da673669750a227f1168c871d945c445ab82db'),
    ('Scripts/Archived Reference/P3 Sources - DAIRLab_dairlib - examples - Cassie - director_scripts - cassie_operator -- 37ce566be152.py', 'rescued/part3/sources/DAIRLab_dairlib/examples/Cassie/director_scripts/cassie_operator.py', '11efdbf9277f0db868617e1bb00f02c7d11de6ab72d50b7b365f7686d658fead'),
    ('Scripts/Archived Reference/P3 Sources - StructuralNeurobiologyLab_SyConn - syconn - analysis - syconn_knossos_viewer -- d8a596964448.py', 'rescued/part3/sources/StructuralNeurobiologyLab_SyConn/syconn/analysis/syconn_knossos_viewer.py', '8058393221072ab4304dc4a6e015fb1f99f63e9bdb5c78479c9d0e7cc455d6ac'),
)


@pytest.fixture
def fragment() -> dict[str, Any]:
    """Return the ninety batch records folded into menu-adaptations.json."""
    shared = json.loads(SHARED.read_text(encoding="utf-8"))
    menus = {menu for menu, _, _ in IDENTITIES}
    return {
        section: [row for row in shared[section] if row.get("source_menu") in menus]
        for section in ("adaptations", "retirements")
    }


def test_inventory_when_complete_then_all_ninety_rows_remain_distinct(fragment: dict[str, Any]) -> None:
    rows = fragment["retirements"]
    assert set(fragment) == {"adaptations", "retirements"}
    assert fragment["adaptations"] == [], "No replacement menu or font writer is proposed"
    actual = {(r["source_menu"], r["source"], r["source_sha256"]) for r in rows}
    assert len(rows) == len(actual) == len(IDENTITIES) == 90
    assert actual == set(IDENTITIES), "Every batch row needs exactly one disposition"
    index = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    indexed = {(r["menu"], r["target"], r["target_sha256"]) for r in index}
    assert actual <= indexed, "Preserve original menu identities, paths and hashes"


@pytest.mark.parametrize("menu,source,digest", IDENTITIES)
def test_source_when_read_then_hash_matches_and_dispatcher_stays_absent(menu: str, source: str, digest: str) -> None:
    assert hashlib.sha256((PRESERVED / source).read_bytes()).hexdigest() == digest, source
    assert not (ROOT / menu).exists(), "Never recreate a third-party dispatcher"


@pytest.mark.parametrize("menu,source,digest", IDENTITIES)
def test_retirement_when_integrated_then_schema_and_specific_reason(menu: str, source: str, digest: str, fragment: dict[str, Any]) -> None:
    row = next(r for r in fragment["retirements"] if r["source"] == source)
    assert set(row) == {"source_menu", "source", "source_sha256", "disposition", "reason", "license"}
    assert (row["source_menu"], row["source_sha256"], row["disposition"]) == (menu, digest, "retired")
    assert row["license"] and len(row["reason"]) > 35
    assert "FontLab" in row["reason"], "Name the missing FontLab workflow or host"
    for forbidden in ("issue 122", "R2", "archived", "unresolved", "draft", "see fragment"):
        assert forbidden not in row["reason"], "Public reasons carry no process wording"
    if "PipeCAD" in source:
        assert row["license"] == "LicenseRef-Proprietary"
        assert "proprietary" in row["reason"]
    elif "naali/" in source:
        assert row["license"] == "Apache-2.0"
    elif source.split("/")[3] in ("RobotLocomotion_director", "openhumanoids_director"):
        assert row["license"] == "BSD-3-Clause"
    elif "dairlib/" in source:
        assert row["license"] == "MIT"
    elif "CsoundQt/" in source or "PythonQt/" in source:
        assert row["license"] == "LGPL-2.1"


def test_csound_candidates_when_inspected_then_editor_operations_need_csound_host(fragment: dict[str, Any]) -> None:
    rows = [r for r in fragment["retirements"] if "/Editor/" in r["source"]]
    assert len(rows) == 9, "Keep both forks and the widget-channel generator"
    tokens = {"indent2.py": "opcodeExists", "rem_newline.py": "getSelectedText",
              "invalue_chnget.py": "setOrc", "strset_list.py": "strset",
              "invalues_for_widgets.py": "getSelectedWidgetsText"}
    for row in rows:
        body = (PRESERVED / row["source"]).read_text()
        assert tokens[Path(row["source"]).name] in body, row["source"]
        assert "q." in body, "CsoundQt provides this host object; no source is executed"


def test_real_app_names_in_g1_form() -> None:
    """Check real Fly aliases and installed App names cited for UI host coverage."""
    roots = {"fly", "fontlabapp"}
    saved = {k: v for k, v in sys.modules.items() if k.split(".")[0] in roots}
    for key in saved:
        del sys.modules[key]
    try:
        app = importlib.import_module("fontlabapp")
        app_root = Path(app.__file__).resolve().parent
        assert not app_root.is_relative_to(ROOT.parent / "fontlab-fontlabapp/src")
        fly = importlib.import_module("fly")
        assert fly.ALIASES["ap"] == "fontlabapp"
        for name, wanted in {
            "scripting": ("show_script_dialog", "close_script_dialog"),
            "qtsafe": ("qt_list", "main_window"),
            "draft_signals": ("Scope",),
        }.items():
            module = importlib.import_module("fly.ap." + name)
            assert module is importlib.import_module("fontlabapp." + name)
            assert Path(module.__file__).resolve().is_relative_to(app_root)
            assert all(callable(getattr(module, symbol)) for symbol in wanted)
    finally:
        for key in list(sys.modules):
            if key.split(".")[0] in roots:
                del sys.modules[key]
        sys.modules.update(saved)


class NativeNode:
    """Keep optional node arguments keyword-only, like the measured binding."""

    def __init__(self, point: Any, *, nodeType: str = "on") -> None:
        self.point, self.node_type = point, nodeType


class NativeContour:
    """Keep optional contour arguments keyword-only, like the measured binding."""

    def __init__(self, nodes: list[Any], *, closed: bool = False) -> None:
        self.nodes, self.closed = nodes, closed


RESERVED = {"render", "size", "layout", "update", "font", "move", "statusBar", "centralWidget", "geometry", "parent", "show", "close"}


class GuardWidget:
    """Reject Python attributes that shadow native QWidget or QDialog names."""

    def __setattr__(self, name: str, value: Any) -> None:
        if name in RESERVED:
            raise AttributeError(name)
        object.__setattr__(self, name, value)


def test_native_constructor_fakes_reject_positional_optional_arguments() -> None:
    for factory, args in ((NativeNode, ((0, 0), "off")), (NativeContour, ([], True))):
        with pytest.raises(TypeError):
            factory(*args)
    assert NativeNode((0, 0), nodeType="off").node_type == "off"
    assert NativeContour([], closed=True).closed is True


def test_fake_signatures_match_the_declared_native_contract() -> None:
    for factory, optional in ((NativeNode, "nodeType"), (NativeContour, "closed")):
        assert inspect.signature(factory).parameters[optional].kind is inspect.Parameter.KEYWORD_ONLY
    # No App functions are faked: G1 imports above inspect the installed modules.
    tree = ast.parse(Path(__file__).read_text(), feature_version=(3, 11))
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                   and n.func.attr == "setattr" for n in ast.walk(tree))


def test_class_attributes_do_not_shadow_native_widget_names() -> None:
    tree = ast.parse(Path(__file__).read_text(), feature_version=(3, 11))
    for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
        assert not ({n.name for n in cls.body if isinstance(n, ast.FunctionDef)} & RESERVED)
    widget = GuardWidget()
    for name in RESERVED:
        with pytest.raises(AttributeError, match=name):
            setattr(widget, name, None)
    widget.status_line = "Ready"
    assert widget.status_line == "Ready"


@pytest.mark.parametrize("filename,token,phrase", (
    ("atlasControlPanel.py", "sendFreezeCommand", "freeze, stop and reactive-recovery"),
    ("atlasRecoveryPanel.py", "sendRecoveryTriggerOn", "reactive-recovery trigger"),
    ("testObjectModel.py", "test parent item", "parent and child objects"),
    ("testPythonConsole.py", "_console.show()", "supplied console"),
    ("graphics_view.py", "addPixmap", "raster images"),
))
def test_precise_retirement_subject_matches_source(filename: str, token: str, phrase: str, fragment: dict[str, Any]) -> None:
    """Keep source-backed action names when a general family label is insufficient."""
    rows = [r for r in fragment["retirements"] if Path(r["source"]).name == filename]
    assert rows, filename
    for row in rows:
        assert token in (PRESERVED / row["source"]).read_text(), row["source"]
        assert phrase in row["reason"], row["source"]
