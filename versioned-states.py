import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog

import versioned_states_engine

kWidthButton = 20
kHeightButton = 3
kWidthText = 80
kHeightText = 20

gEngine = versioned_states_engine.VersionedStatesEngine()


def func_input():
    gEngine.input(text_input.get('1.0', tkinter.END))
    func_display_input()


def func_display_input():
    text_display.config(state='normal')
    text_display.delete('1.0', tkinter.END)
    inputs = gEngine.get_input()
    if inputs is not None:
        text_display.insert(
            tkinter.END, f'add {len(inputs)} new objects:\n' +
            ', '.join(str(i) for i in inputs))
    text_display.config(state='disabled')


def func_summarize():
    descriptions = gEngine.get_descriptions()
    states = gEngine.get_states()
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
    version = func_read_version()
    state = func_read_state()
    condition = {
        'state': bool(state),
        'version': bool(version),
        'inputs': gEngine.get_input() is not None
    }
    if all(c for c in condition.values()):
        gEngine.add(version=version, state=state)
        func_summarize()
    else:
        cause = ', '.join(f'invalid {c}' for c in condition
                          if not condition[c])
        tkinter.messagebox.showerror('', cause)


def func_back():
    gEngine.back()
    func_summarize()


def func_read_state():
    return text_state.get('1.0', tkinter.END).strip()


def func_read_version():
    return text_version.get('1.0', tkinter.END).strip()


def func_load():
    filename = tkinter.filedialog.askopenfilename(filetypes=[('JSON',
                                                              '.json')])
    if bool(filename):
        gEngine.load(filename)
        func_summarize()


def func_save():
    if gEngine.get_states() is not None:
        filename = tkinter.filedialog.asksaveasfilename()
        if bool(filename):
            filename = filename if filename.endswith(
                '.json') else filename + '.json'
            gEngine.save(filename)


def func_export():
    if gEngine.get_states() is not None:
        filename = tkinter.filedialog.asksaveasfilename()
        if bool(filename):
            filename = filename if filename.endswith(
                '.csv') else filename + '.csv'
            gEngine.export(filename)


def func_load_description():
    filename = tkinter.filedialog.askopenfilename(filetypes=[('CSV', '.csv')])
    if bool(filename):
        gEngine.load_description(filename)
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
