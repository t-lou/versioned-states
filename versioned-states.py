import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import json
import csv

kWidthButton = 20
kHeightButton = 3
kWidthText = 80
kHeightText = 20

last_states = None
states = None
inputs = None
descriptions = None


def func_input():
    global inputs
    inputs = tuple(i.strip()
                   for i in text_input.get('1.0', tkinter.END).replace(
                       '\n', ',').strip().split(',') if bool(i.strip()))
    func_display_input()


def func_display_input():
    text_display.config(state='normal')
    text_display.delete('1.0', tkinter.END)
    if input is not None:
        text_display.insert(
            tkinter.END, f'add {len(inputs)} new objects:\n' +
            ', '.join(str(i) for i in inputs))
    text_display.config(state='disabled')


def func_summarize():
    text_summary.config(state='normal')
    text_summary.delete('1.0', tkinter.END)
    text_summary.insert(
        tkinter.END,
        f'there are {len(descriptions) if descriptions is not None else 0} descriptions\n\n'
    )
    if states is None:
        text_summary.insert(tkinter.END, 'null')
    else:
        all_states = set(states[version][name] for version in states
                         for name in states[version])
        for version in sorted(list(states.keys())):
            text_summary.insert(
                tkinter.END, f'version {version}\n' + ', '.join(
                    f'{s}:{len(tuple(i for i in states[version] if states[version][i] == s))}'
                    for s in all_states) + '\n')
    text_summary.config(state='disabled')


def func_add():
    global states, last_states
    version = func_read_version()
    state = func_read_state()
    condition = {
        'state': bool(state),
        'version': bool(version),
        'inputs': inputs is not None
    }
    if all(c for c in condition.values()):
        # backup
        last_states = None if states is None else dict(states)
        if states is None:
            states = {}
        if version not in states:
            states[version] = {}
        states[version].update({i: state for i in inputs})
    else:
        cause = ', '.join(f'invalid {c}' for c in condition
                          if not condition[c])
        tkinter.messagebox.showerror('', cause)

    func_summarize()


def func_back():
    global states
    states = None if last_states is None else dict(last_states)
    func_summarize()


def func_read_state():
    return text_state.get('1.0', tkinter.END).strip()


def func_read_version():
    return text_version.get('1.0', tkinter.END).strip()


def func_load():
    global states
    states = json.loads(
        open(tkinter.filedialog.askopenfilename(filetypes=[('JSON',
                                                            '.json')])).read())
    func_summarize()


def func_save():
    if states is not None:
        filename = tkinter.filedialog.asksaveasfilename()
        filename = filename if filename.endswith(
            '.json') else filename + '.json'
        with open(filename, 'w') as fs:
            fs.write(json.dumps(states, indent=' '))


def func_export():
    if states is not None:
        all_names = sorted(
            list(set(name for version in states for name in states[version])))
        filename = tkinter.filedialog.asksaveasfilename()
        filename = filename if filename.endswith('.csv') else filename + '.csv'
        with open(filename, 'w', newline='') as fs:
            writer = csv.DictWriter(
                fs,
                fieldnames=['item'] +
                ([] if descriptions is None else ['description']) +
                sorted(list(states.keys())))
            writer.writeheader()
            for name in all_names:
                row = {'item': name}
                if descriptions is not None:
                    row['description'] = descriptions[
                        name] if name in descriptions else ''
                row.update({version: '' for version in states})
                row.update({
                    version: states[version][name]
                    for version in states if name in states[version]
                })
                writer.writerow(row)


def func_load_description():
    global descriptions
    with open(tkinter.filedialog.askopenfilename(filetypes=[('CSV', '.csv')]),
              'r') as fi:
        reader = csv.DictReader(fi)
        rows = tuple(row for row in reader)
        assert all('item' in row and 'description' in row
                   for row in rows), 'invalid description'
        assert len(set(row['item']
                       for row in rows)) == len(rows), 'duplicate description'
        descriptions = {row['item']: row['description'] for row in rows}

    func_summarize()


root = tkinter.Tk()
root.title('versioned-states')

frame_texts = tkinter.Frame(root)
frame_buttons = tkinter.Frame(root)

text_input = tkinter.Text(frame_texts, width=kWidthText, height=kHeightText)

text_state = tkinter.Text(frame_texts, width=kWidthText, height=2)

text_version = tkinter.Text(frame_texts, width=kWidthText, height=2)

text_display = tkinter.Text(frame_texts,
                            width=kWidthText,
                            height=kHeightText,
                            state=tkinter.DISABLED)

text_summary = tkinter.Text(frame_texts,
                            width=kWidthText,
                            height=kHeightText,
                            state=tkinter.DISABLED)

tkinter.Label(frame_texts, text='input').pack(side=tkinter.TOP)
text_input.pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
tkinter.Label(frame_texts, text='state').pack(side=tkinter.TOP)
text_state.pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
tkinter.Label(frame_texts, text='version').pack(side=tkinter.TOP)
text_version.pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
tkinter.Label(frame_texts, text='confirmation input').pack(side=tkinter.TOP)
text_display.pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
tkinter.Label(frame_texts, text='summary').pack(side=tkinter.TOP)
text_summary.pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)

text_display.bind('<1>', lambda event: text_display.focus_set())
text_summary.bind('<1>', lambda event: text_summary.focus_set())

tkinter.Button(frame_buttons,
               height=kHeightButton,
               width=kWidthButton,
               text='load',
               command=func_load).pack(side=tkinter.TOP,
                                       expand=tkinter.YES,
                                       fill=tkinter.BOTH)

tkinter.Button(frame_buttons,
               height=kHeightButton,
               width=kWidthButton,
               text='save',
               command=func_save).pack(side=tkinter.TOP,
                                       expand=tkinter.YES,
                                       fill=tkinter.BOTH)

tkinter.Button(frame_buttons,
               height=kHeightButton,
               width=kWidthButton,
               text='input',
               command=func_input).pack(side=tkinter.TOP,
                                        expand=tkinter.YES,
                                        fill=tkinter.BOTH)

tkinter.Button(frame_buttons,
               height=kHeightButton,
               width=kWidthButton,
               text='add',
               command=func_add).pack(side=tkinter.TOP,
                                      expand=tkinter.YES,
                                      fill=tkinter.BOTH)

tkinter.Button(frame_buttons,
               height=kHeightButton,
               width=kWidthButton,
               text='back',
               command=func_back).pack(side=tkinter.TOP,
                                       expand=tkinter.YES,
                                       fill=tkinter.BOTH)

tkinter.Button(frame_buttons,
               height=kHeightButton,
               width=kWidthButton,
               text='load desc',
               command=func_load_description).pack(side=tkinter.TOP,
                                                   expand=tkinter.YES,
                                                   fill=tkinter.BOTH)

tkinter.Button(frame_buttons,
               height=kHeightButton,
               width=kWidthButton,
               text='export',
               command=func_export).pack(side=tkinter.TOP,
                                         expand=tkinter.YES,
                                         fill=tkinter.BOTH)

frame_texts.pack(side=tkinter.LEFT, expand=tkinter.YES, fill=tkinter.BOTH)
frame_buttons.pack(side=tkinter.LEFT, expand=tkinter.YES, fill=tkinter.BOTH)

tkinter.mainloop()
