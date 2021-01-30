import json
import csv


class VersionedStatesEngine(object):
    def __init__(self):
        self._states = None
        self._last_states = None
        self._inputs = None
        self._descriptions = None

    def get_states(self) -> dict:
        return self._states

    def get_input(self) -> set:
        return self._inputs

    def get_descriptions(self) -> dict:
        return self._descriptions

    def back(self):
        self._states = None if self._last_states is None else dict(
            self._last_states)

    def input(self, input_text=str):
        self._inputs = set(
            i.strip() for i in input_text.replace('\n', ',').strip().split(',')
            if bool(i.strip()))

    def add(self, version=str, state=str):
        # backup
        self._last_states = None if self._states is None else dict(
            self._states)
        if self._states is None:
            self._states = {}
        if version not in self._states:
            self._states[version] = {}
        self._states[version].update({i: state for i in self._inputs})

    def load(self, filename=str):
        with open(filename) as fs:
            self._states = json.loads(fs.read())

    def save(self, filename=str):
        if self._states is not None:
            with open(filename, 'w') as fs:
                fs.write(json.dumps(self._states, indent=' '))

    def export(self, filename=str):
        if self._states is not None:
            all_names = sorted(
                list(
                    set(name for version in self._states
                        for name in self._states[version])))
            with open(filename, 'w', newline='') as fs:
                writer = csv.DictWriter(
                    fs,
                    fieldnames=['item'] +
                    ([] if self._descriptions is None else ['description']) +
                    sorted(list(self._states.keys())))
                writer.writeheader()
                for name in all_names:
                    row = {'item': name}
                    if self._descriptions is not None:
                        row['description'] = self._descriptions[
                            name] if name in self._descriptions else ''
                    row.update({version: '' for version in self._states})
                    row.update({
                        version: self._states[version][name]
                        for version in self._states
                        if name in self._states[version]
                    })
                    writer.writerow(row)

    def load_description(self, filename=str):
        with open(filename, 'r') as fi:
            reader = csv.DictReader(fi)
            rows = tuple(row for row in reader)
            assert all('item' in row and 'description' in row
                       for row in rows), 'invalid description'
            assert len(set(
                row['item']
                for row in rows)) == len(rows), 'duplicate description'
            self._descriptions = {
                row['item']: row['description']
                for row in rows
            }


if __name__ == '__main__':
    import unittest
    import os

    class TestReplay(unittest.TestCase):
        def setUp(self):
            with open('test_description.csv', 'w') as fs:
                fs.write('''item,description
case01,desc1
case03,desc3
case04,desc4
''')

            with open('test_states.json', 'w') as fs:
                fs.write('''{
 "v1": {
  "case01": "passed",
  "case02": "failed",
  "case03": "failed"
 },
 "v2": {
  "case03": "passed",
  "case04": "passed"
 }
}
''')

        def tearDown(self):
            os.remove('test_description.csv')
            os.remove('test_states.json')

            def remove_optional(filename: str):
                if os.path.isfile(filename):
                    os.remove(filename)

            remove_optional('test_states_from_case.json')
            remove_optional('test_export.csv')
            remove_optional('test_export_with_description.csv')

        def test(self):
            engine = VersionedStatesEngine()

            # test initialization
            self.assertIsNone(engine.get_states())
            self.assertIsNone(engine.get_input())
            self.assertIsNone(engine.get_descriptions())

            # test input and add
            engine.input('''case01,case02,
  case03
''')
            self.assertIsNone(engine.get_states())
            self.assertEqual(engine.get_input(),
                             {'case01', 'case02', 'case03'})

            engine.add(version='v1', state='failed')

            self.assertEqual(engine.get_states(), {
                'v1': {
                    'case01': 'failed',
                    'case02': 'failed',
                    'case03': 'failed'
                }
            })

            engine.input('case01')
            engine.add(version='v1', state='passed')

            self.assertEqual(engine.get_input(), {'case01'})
            self.assertEqual(engine.get_states(), {
                'v1': {
                    'case01': 'passed',
                    'case02': 'failed',
                    'case03': 'failed'
                }
            })

            engine.input('case04,case03')
            engine.add(version='v2', state='passed')

            self.assertEqual(engine.get_input(), {'case03', 'case04'})
            self.assertEqual(
                engine.get_states(), {
                    'v1': {
                        'case01': 'passed',
                        'case02': 'failed',
                        'case03': 'failed'
                    },
                    'v2': {
                        'case03': 'passed',
                        'case04': 'passed'
                    }
                })

            # test load
            engine_from_file = VersionedStatesEngine()
            engine_from_file.load('test_states.json')
            self.assertEqual(engine.get_states(),
                             engine_from_file.get_states())

            # test save
            engine.save('test_states_from_case.json')
            with open('test_states.json') as fs1:
                with open('test_states_from_case.json') as fs2:
                    self.assertEqual(json.loads(fs1.read()),
                                     json.loads(fs2.read()))

            # test export
            engine.export('test_export.csv')
            with open('test_export.csv') as fs:
                self.assertEqual(
                    fs.read(), '''item,v1,v2
case01,passed,
case02,failed,
case03,failed,passed
case04,,passed
''')
            # test add description and export with it
            engine.load_description('test_description.csv')
            self.assertEqual(engine.get_descriptions(), {
                'case01': 'desc1',
                'case03': 'desc3',
                'case04': 'desc4'
            })
            engine.export('test_export_with_description.csv')
            with open('test_export_with_description.csv') as fs:
                self.assertEqual(
                    fs.read(), '''item,description,v1,v2
case01,desc1,passed,
case02,,failed,
case03,desc3,failed,passed
case04,desc4,,passed
''')

            # test back
            engine.back()
            self.assertEqual(engine.get_states(), {
                'v1': {
                    'case01': 'passed',
                    'case02': 'failed',
                    'case03': 'failed'
                }
            })
            engine.back()
            self.assertEqual(engine.get_states(), {
                'v1': {
                    'case01': 'passed',
                    'case02': 'failed',
                    'case03': 'failed'
                }
            })  # further back is invalid

    unittest.main()
