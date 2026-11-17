# this_file: tests/test_restored_network_opengl.py
"""Framing, coordinate and import checks for the restored local-network demos."""
import importlib.util
import struct
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lessons/src'))
from fontlab_python_lessons import network_demos as network


def test_fortune_frames_when_fragmented_then_wait_for_complete_unicode():
    packet = network.fortune_frame('Zażółć 🌿')
    for size in range(len(packet)):
        partial = bytearray(packet[:size])
        assert network.take_frame(partial) is None
        assert partial == packet[:size]
    buffer = bytearray(packet + packet)
    assert network.take_frame(buffer) == 'Zażółć 🌿'
    assert network.take_frame(buffer) == 'Zażółć 🌿'
    assert buffer == b''


@pytest.mark.parametrize('packet', [b'\0\1x', struct.pack('!HI', 6, 1) + b'ab'])
def test_invalid_fortune_frame_is_rejected(packet):
    with pytest.raises(ValueError):
        network.take_frame(bytearray(packet))


def test_oversized_fortune_is_rejected():
    with pytest.raises(ValueError):
        network.fortune_frame('x' * 40000)


def test_local_url_refuses_external_endpoints():
    peer = SimpleNamespace(host='127.0.0.1', port=12345)
    assert network.local_url('http://127.0.0.1:12345/sample', peer).path == '/sample'
    for url in ['https://127.0.0.1:12345/sample', 'http://example.com/sample',
                'http://127.0.0.1:12346/sample', 'http://user@127.0.0.1:12345/sample']:
        with pytest.raises(ValueError):
            network.local_url(url, peer)


def test_restored_menu_imports_have_no_native_or_network_effects():
    paths = [*ROOT.glob('Scripts/Network/*.py'), *ROOT.glob('Scripts/OpenGL/*.py'),
             *ROOT.glob('Scripts/Multimedia/*.py')]
    assert len(paths) == 14
    for index, path in enumerate(paths):
        spec = importlib.util.spec_from_file_location('network_menu_' + str(index), path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert callable(module.build)
        assert callable(module.main)
