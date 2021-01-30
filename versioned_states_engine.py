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

    def get_input(self) -> tuple:
        return self._inputs

    def get_descriptions(self) -> dict:
        return self._descriptions

    def back(self):
        self._states = None if self._last_states is None else dict(
            self._last_states)

    def input(self, input_text=str):
        self._inputs = tuple(
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
        self._states = json.loads(open(filename).read())

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
            descriptions = {row['item']: row['description'] for row in rows}


if __name__ == '__main__':
    pass
