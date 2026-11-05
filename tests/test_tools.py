"""Local tool regression checks; all Git writes stay in temporary directories."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


deps = load('check_dependencies')
ctx = load('context')


class DependencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'prompt-audience-research'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.repo / 'required.md').write_text('pinned\n')
        (self.repo / 'second.md').write_text('second\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        self.item = dict(name='prompt-audience-research', url='https://example.invalid/sample.git',
                         revision=self.git('rev-parse', 'HEAD').strip(),
                         files=['required.md', 'second.md'], purpose='fixture', routes=['audience'])

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.DEVNULL).decode()

    def test_pinned_bytes_and_hidden_edits(self):
        self.assertEqual(deps.check_dependency(self.root, self.item), 'ok')
        for flag in ('--assume-unchanged', '--skip-worktree'):
            with self.subTest(flag=flag):
                (self.repo / 'required.md').write_text('pinned\n')
                self.git('update-index', flag, 'required.md')
                (self.repo / 'required.md').write_text('hidden edit\n')
                self.assertIn('differs from pinned bytes', deps.check_dependency(self.root, self.item))
                self.git('update-index', '--no-assume-unchanged', '--no-skip-worktree', 'required.md')

    def test_checks_all_required_files(self):
        (self.repo / 'required.md').unlink()
        (self.repo / 'second.md').write_text('changed\n')
        result = deps.check_dependency(self.root, self.item)
        self.assertIn('required.md: missing/invalid', result)
        self.assertIn('second.md: required file differs', result)

    def test_strict_head_even_identical_required_bytes(self):
        (self.repo / 'other').write_text('new')
        self.git('add', '.')
        self.git('commit', '-qm', 'other commit')
        self.assertEqual(deps.check_dependency(self.root, self.item), 'stale revision')

    def test_git_replace_cannot_substitute_pinned_bytes(self):
        pinned = self.item['revision']
        (self.repo / 'required.md').write_text('replacement bytes\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'replacement fixture')
        replacement = self.git('rev-parse', 'HEAD').strip()
        self.git('update-ref', 'HEAD', pinned)
        self.git('replace', pinned, replacement)
        self.assertEqual(self.git('rev-parse', 'HEAD').strip(), pinned)
        self.assertEqual(self.git('show', pinned + ':required.md'), 'replacement bytes\n')
        self.assertIn('differs from pinned bytes', deps.check_dependency(self.root, self.item))

    def test_dirty_unrelated_file(self):
        (self.repo / 'untracked').write_text('x')
        self.assertIn('dirty checkout', deps.check_dependency(self.root, self.item))

    def test_symlink_file_and_checkout(self):
        (self.repo / 'required.md').unlink()
        (self.repo / 'required.md').symlink_to('second.md')
        self.assertIn('missing/invalid', deps.check_dependency(self.root, self.item))
        (self.root / 'alias').symlink_to(self.repo, target_is_directory=True)
        alias = dict(self.item, name='alias')
        self.assertIn('symlink', deps.check_dependency(self.root, alias))

    def test_pinned_symlink_rejected(self):
        (self.repo / 'required.md').unlink()
        (self.repo / 'required.md').symlink_to('second.md')
        self.git('add', '.')
        self.git('commit', '-qm', 'symlink fixture')
        self.item['revision'] = self.git('rev-parse', 'HEAD').strip()
        self.assertIn('missing/invalid', deps.check_dependency(self.root, self.item))

    def manifest(self, items):
        path = self.root / 'dependencies.json'
        path.write_text(json.dumps({'dependencies': items}))
        return path

    def test_bad_manifest_and_escape(self):
        for change in ({'files': ['../outside']}, {'files': ['/outside']},
                       {'files': ['a//b']}, {'files': ['a\\b']},
                       {'revision': 'HEAD'}, {'routes': ['unknown']}, {'name': '../escape'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                deps.read_manifest(self.manifest([dict(self.item, **change)]))

    def test_selected_route_ignores_missing_other_checkout(self):
        other = dict(self.item, name='absent', routes=['clip'])
        self.manifest([self.item, other])
        old = deps.REPOSITORY
        deps.REPOSITORY = self.root
        self.addCleanup(setattr, deps, 'REPOSITORY', old)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(deps.main(['--repos-root', str(self.root), '--route', 'audience']), 0)
            self.assertEqual(deps.main(['--repos-root', str(self.root)]), 2)

    def test_absent_route_fails_closed_without_output(self):
        self.manifest([dict(self.item, routes=['clip'])])
        old = deps.REPOSITORY
        deps.REPOSITORY = self.root
        self.addCleanup(setattr, deps, 'REPOSITORY', old)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(deps.main(['--repos-root', str(self.root), '--route', 'audience']), 2)
        self.assertEqual(stdout.getvalue(), '')

    def test_incomplete_route_components_fail_closed(self):
        for route, component in [('hvco', 'promt-hvco'), ('clip', 'prompt-clip-landing')]:
            primary = dict(self.item, name=component, routes=[route])
            copy = dict(self.item, name='promt-copywriting', routes=[route, 'copywriting'])
            for entries in ([primary], [copy], [primary, dict(copy, routes=['copywriting'])]):
                with self.subTest(route=route, names=[i['name'] for i in entries]):
                    with self.assertRaises(ValueError):
                        deps.select_entries(entries, route)
            self.assertEqual(deps.select_entries([primary, copy], route), [primary, copy])
        with self.assertRaises(ValueError):
            deps.select_entries([self.item], None)

    def test_manifest_route_coupling(self):
        # Manifest syntax and route coupling do not depend on the user's checkouts.
        items = deps.read_manifest(ROOT / 'dependencies.json')
        copy = next(i for i in items if i['name'] == 'promt-copywriting')
        self.assertEqual(set(copy['routes']), {'hvco', 'clip', 'copywriting'})


class ContextTests(unittest.TestCase):
    def test_full_subsections_no_truncation(self):
        body = 'длинная карточка\n' * 10000
        source = '# Root\n## First\n' + body + '### Nested\ncomplete\n## Second\nexcluded\n'
        result = ctx.sections(source, ['First'])
        self.assertEqual(result, '## First\n' + body + '### Nested\ncomplete\n')

    def test_fences_and_overlap(self):
        source = '# A\n```md\n## Fake\n```\n## B\nbody\n# C\nend\n'
        self.assertEqual(ctx.sections(source, ['A', 'B']), source[:source.index('# C')])
        with self.assertRaises(ValueError):
            ctx.sections(source, ['Fake'])

    def test_duplicates_unknown_hidden(self):
        for text, selectors in [('# A\nx\n# A\ny\n', ['A']), ('# A\nx', ['A', 'A']),
                                ('# A\nx', ['missing']), ('# A\nx\u200b', ['A'])]:
            with self.subTest(selectors=selectors), self.assertRaises(ValueError):
                ctx.sections(text, selectors)

    def test_validation_before_any_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.md'
            output = Path(directory) / 'result.md'
            source.write_text('# A\ncomplete\n')
            for extra in ([], ['--output', str(output)]):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
                    status = ctx.main(['--file', str(source), '--heading', 'A', '--heading', 'missing'] + extra)
                self.assertEqual(status, 2)
                self.assertEqual(stdout.getvalue(), '')
                self.assertFalse(output.exists())

    def test_output_file_exclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.md'
            output = Path(directory) / 'result.md'
            source.write_text('# A\ncomplete\n')
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(ctx.main(['--file', str(source), '--heading', 'A', '--output', str(output)]), 0)
                self.assertEqual(output.read_text(), source.read_text())
                self.assertEqual(ctx.main(['--file', str(source), '--heading', 'A', '--output', str(output)]), 2)


if __name__ == '__main__':
    unittest.main()
