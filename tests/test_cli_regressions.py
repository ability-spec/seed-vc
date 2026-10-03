"""Run the actual inference CLI parser and save logic without loading torch/models."""
import argparse
import ast
import os
from pathlib import Path
from types import SimpleNamespace
import pytest
from inference_cli import str2bool, audio_identity

SOURCE = Path(__file__).resolve().parents[1] / 'inference_v2.py'

def parser():
    tree = ast.parse(SOURCE.read_text())
    main = next(n for n in tree.body if isinstance(n, ast.If) and '__name__' in ast.unparse(n.test))
    statements = []
    for node in main.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'args' for t in node.targets): break
        statements.append(node)
    scope = {'argparse': argparse, 'str2bool': str2bool}
    exec(compile(ast.Module(body=statements, type_ignores=[]), str(SOURCE), 'exec'), scope)
    return scope['parser']

@pytest.mark.parametrize('value,expected', [('False', False), ('0', False), ('true', True), ('1', True)])
def test_compile_boolean(value, expected):
    assert parser().parse_args(['--target', 'ref.wav', '--compile', value]).compile is expected

def test_invalid_compile_rejected():
    with pytest.raises(SystemExit): parser().parse_args(['--target', 'ref.wav', '--compile', 'maybe'])

def test_batch_saves_multidot_and_same_stem_sources_separately(tmp_path):
    tree = ast.parse(SOURCE.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_save_one')
    saved = []
    scope = {'os': os, 'audio_identity': audio_identity, 'convert_voice_v2': lambda *a: (24000, [0]), 'sf': SimpleNamespace(write=lambda path, *a: saved.append(path))}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), 'exec'), scope)
    args = SimpleNamespace(length_adjust=1, diffusion_steps=15, similarity_cfg_rate=.7)
    for name in ['speech.one.wav', 'speech.two.wav', 'a/speech.wav', 'b/speech.wav']:
        scope['_save_one'](tmp_path / name, 'reference.wav', tmp_path / 'out', args)
    assert len(set(saved)) == 4
    assert any('speech.one' in p for p in saved)
