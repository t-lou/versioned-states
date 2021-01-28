# For tracing the changes of states in different versions

You may have a software in version 0.9, some new test cases are added, some old test cases are skipped,
and you may want to see how the failed tests distribute in different versions.

# Functions

![image](https://github.com/t-lou/versioned-states/blob/master/screenshots/gui.png)

- **load** load one existing file saved in json

- **save** save the modified states to json state

- **input** read and parsed the listed items from *input* textfield,
a confirmation is available in *confirmation input* textfield; the items are separated with either new line or ','

- **add** add the parsed items to project with version and state in corresponding textfields

- **load desc** load optional descriptions for the items, then it will be part of the exported report; descriptions must be csv file with *item* and *description* columns

- **export** export the report in csv file; with simple find-replace, Calc or Excel can give intuitive colored table

# Reports

- export

![image](https://github.com/t-lou/versioned-states/blob/master/screenshots/export.png)

- after simple decoration in Libreoffice Calc

![image](https://github.com/t-lou/versioned-states/blob/master/screenshots/export_extern.png)
