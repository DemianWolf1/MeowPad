from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from tkinter.ttk import *
import webbrowser
import datetime


class SmartTextBoxFrame(Frame):
    def __init__(self, master, **kw):
        Frame.__init__(self, master)
        self.pack(fill=BOTH, expand=True)
        self.vfr = Frame(self)
        self.vfr.pack(fill=BOTH, expand=True)
        self.textbox = Text(self.vfr, **kw)
        self.textbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.vscroll = Scrollbar(self.vfr)
        self.hscroll = Scrollbar(self, orient=HORIZONTAL)
        self.vscroll.pack(side=LEFT, fill=Y)
        self.hscroll.pack(side=BOTTOM, fill=X)
        self.vscroll["command"] = self.textbox.yview
        self.hscroll["command"] = self.textbox.xview
        self.textbox["yscrollcommand"] = self.vscroll_set
        self.textbox["xscrollcommand"] = self.hscroll_set

    def vscroll_set(self, *args):
        self.vscroll.set(*args)
        if self.vscroll.get() == (0.0, 1.0):
            self.vscroll.pack_forget()
        else:
            self.vscroll.pack(side=LEFT, fill=Y)

    def hscroll_set(self, *args):
        self.hscroll.set(*args)
        if self.hscroll.get() == (0.0, 1.0):
            self.hscroll.pack_forget()
        else:
            self.hscroll.pack(side=BOTTOM, fill=X)

class StatusBar(Frame):

    def __init__(self, master, **kw):
        Frame.__init__(self, master, **kw)
        self.labels = {}

    def set_label(self, name, text='', side='left', width=0):
        if name not in self.labels:
            label = Label(self, relief=GROOVE, anchor='w')
            label.pack(side=side)
            self.labels[name] = label
        else:
            label = self.labels[name]
        if width != 0:
            label.config(width=width)
        label.config(text=text)

class FilterDialog(Toplevel):
    def __init__(self):
        pass

class GoToDialog(Toplevel):
    def __init__(self, master, *args, **kwargs):
        Toplevel.__init__(self)
        self.title("Go to...")
        self.transient(self.master)
        self.to_line = BooleanVar(self, value=True)
        self.to_column = BooleanVar(self, value=True)
        vcmd = self.register(self.entries_vcmd)

        preline_frame = Frame(self)
        line_frame = Frame(preline_frame)
        Checkbutton(line_frame, text="Choose line:", variable=self.to_line, command=self.chkbtn_onclick).pack(side=LEFT)
        self.line_entry = Entry(line_frame, width=5, validate="key",
                                validatecommand=(vcmd, "%P"))
        self.line_entry.pack(side=LEFT)
        line_frame.pack(side=RIGHT)
        preline_frame.pack(fill=X)

        precolumn_frame = Frame(self)
        column_frame = Frame(precolumn_frame)
        Checkbutton(column_frame, text="Choose column:", variable=self.to_column, command=self.chkbtn_onclick).pack(side=LEFT)
        self.column_entry = Entry(column_frame, width=5, validate="key",
                                  validatecommand=(vcmd, "%P"))
        self.column_entry.pack(side=LEFT)
        column_frame.pack(side=RIGHT)
        precolumn_frame.pack(fill=X)

        self.ok_btn = Button(self, text="OK", command=self.ok_command)
        self.ok_btn.pack()

    def chkbtn_onclick(self):
        if self.to_line.get() == self.to_column.get() == False:
            self.ok_btn["state"] = "disabled"
        else:
            self.ok_btn["state"] = "normal"
        if not self.to_line.get():
            self.line_entry["state"] = "disabled"
        else:
            self.line_entry["state"] = "normal"
        if not self.to_column.get():
            self.column_entry.configure(state="disabled")
        else:
            self.column_entry.configure(state="normal")


    def entries_vcmd(self, P):
        # checks if entry's value is an integer or empty
        if P.isdigit() or P == "":
            return True
        return False


    def ok_command(self):
        cur_coords = self.master.textbox.index(INSERT).split(".")
        print(cur_coords)
        if self.to_line.get():
            if self.to_column.get():
                coords = ".".join((self.line_entry.get(), self.column_entry.get()))
            else:
                coords = ".".join((self.line_entry.get(), cur_coords[1]))
        else:
            coords = ".".join((cur_coords[0], self.line_entry.get()))
        self.master.textbox.mark_set("", coords)


class MeowPad(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.filename = "Untitled"
        self.untitled = True
        self.wrap_var = StringVar(self, value="char")
        self.update_wtitle()
        self.create_menu()
        self.create_wgts()

    def update_wtitle(self):
        self.title("MeowPad 1.00 - {}".format(self.filename))

    def create_menu(self):
        self.menubar = Menu(self, tearoff=False)
        self.config(menu=self.menubar)
        
        self.filemenu = Menu(self.menubar, tearoff=False)
        self.editmenu = Menu(self.menubar, tearoff=False)
        self.toolsmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu = Menu(self.menubar, tearoff=False)

        self.menubar.add_cascade(menu=self.filemenu, label="File")
        self.menubar.add_cascade(menu=self.editmenu, label="Edit")
        self.menubar.add_cascade(menu=self.toolsmenu, label="Tools")
        self.menubar.add_cascade(menu=self.helpmenu, label="Help")

        self.filemenu.add_command(label="New", accelerator="Ctrl+N", command=self.new)
        self.filemenu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open)
        # TODO: Open recent
        self.filemenu.add_command(label="Save", accelerator="Ctrl+S", command=self.save)
        self.filemenu.add_command(label="Save as...", accelerator="Ctrl+Shift+S", command=self.save_as)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Print", accelerator="Ctrl+P", command=self.print)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", accelerator="Alt+F4", command=self.exit)

        self.editmenu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        self.editmenu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut", accelerator="Ctrl+X", command=self.cut)
        self.editmenu.add_command(label="Copy", accelerator="Ctrl+C", command=self.copy)
        self.editmenu.add_command(label="Paste", accelerator="Ctrl+V", command=self.paste)
        self.editmenu.add_command(label="Select all", accelerator="Ctrl+A", command=self.select_all)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Find...", accelerator="Ctrl+F", command=self.find)
        self.editmenu.add_command(label="Find next...", accelerator="F3", command=self.find_next)
        self.editmenu.add_command(label="Find in selection...", accelerator="Ctrl+Shift+F", command=self.find_in_selection)
        self.editmenu.add_command(label="Find in files...", accelerator="Ctrl+Alt+F", command=self.find_in_files)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Replace...", accelerator="Ctrl+R", command=self.replace)
        self.editmenu.add_command(label="Filter...", accelerator="Alt+F", command=self.filter)
        self.editmenu.add_command(label="Filter in selection...", accelerator="Alt+Shift+F", command=self.filter_in_selection)
        self.editmenu.add_command(label="Filter as previous...", accelerator="Alt+F3", command=self.filter_as_previous)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Go to...", accelerator="Ctrl+G", command=self.go_to)
        self.editmenu.add_command(label="Smart complete", accelerator="Ctrl+Tab", command=self.smart_complete)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Insert date&time", accelerator="F5", command=self.insert_datetime)

        self.toolswrapmenu = Menu(self.toolsmenu, tearoff=False)
        self.toolswrapmenu.add_radiobutton(label="By chars", value=CHAR, variable=self.wrap_var, command=self.set_wrap)
        self.toolswrapmenu.add_radiobutton(label="By words", value=WORD, variable=self.wrap_var, command=self.set_wrap)
        self.toolswrapmenu.add_radiobutton(label="Disabled", value=NONE, variable=self.wrap_var, command=self.set_wrap)

        self.toolsmenu.add_command(label="Configuration...", command=self.configuration)
        self.toolsmenu.add_command(label="Check for updates", command=self.check_for_updates)
        self.toolsmenu.add_separator()
        self.toolsmenu.add_cascade(label="Text wrap", menu=self.toolswrapmenu)

        self.helpmenu.add_command(label="MeowPad Help", accelerator="F1", command=self.help)
        self.helpmenu.add_command(label="About MeowPad", accelerator="Ctrl+F1", command=self.about)

        self.protocol("WM_DELETE_WINDOW", self.exit)

    def create_wgts(self):
        self.textbox = SmartTextBoxFrame(self).textbox
        self.textbox.configure(undo=True, maxundo=-1)
        self.statusbar = StatusBar(self)
        self.textbox.bind("<<update-statusbar>>", self.update_statusbar)
        self.textbox.event_add("<<update-statusbar>>", "<KeyRelease>", "<ButtonRelease>")
        self.update_statusbar()
        self.statusbar.pack(side=RIGHT)

    def update_statusbar(self, event=None):
        line, column = self.textbox.index(INSERT).split('.')
        self.statusbar.set_label("line", "Line: {}".format(line))
        self.statusbar.set_label("column", "Column: {}".format(column))

    def set_wrap(self):
        self.textbox.configure(wrap=self.wrap_var.get())

    def new(self):
        pass

    def _open(self):
        _filename = askopenfilename()
        if _filename:
            try:
                file = open(_filename, "r")
                data = file.read()
                file.close()
                self.textbox.delete("1.0", END)
                self.textbox.insert(END, data)
                self.textbox.edit_modified(False)
                return True
            except:
                showerror("Error", """There is an error occured while saving the file.
            Check your permissions for this file!""")
    def open(self):
        if self.textbox.edit_modified():
            confirm = askyesnocancel("Open another file?", "Do you want to save changes in \"{}\"".format(self.filename))
            if confirm:
                is_saved = self.save()
                if is_saved:
                    self._open()
            elif confirm == False:
                self._open()
        else:
            self._open()

    def save(self, modify_edit_modified=True):
        if self.textbox.edit_modified():
            if self.untitled:
                _filename = asksaveasfilename()
                if _filename:
                    try:
                        file = open(_filename, "w")
                        file.write(self.textbox.get("1.0", END))
                        file.close()
                        if modify_edit_modified:
                            self.textbox.edit_modified(False)
                        return True
                    except:
                        showerror("Error", """There is an error occured while saving the file.
Check your permissions for this file!""")
                else:
                    return False

    def save_as(self):
        pass

    def print(self):
        pass

    def exit(self):
        if self.textbox.edit_modified():
            confirm = askyesnocancel("Exit?", "Do you want to save changes in \"{}\"".format(self.filename))
            if confirm:
                self.save()
                self.destroy()
            elif confirm == False:
                self.destroy()
        else:
            self.destroy()

    def undo(self):
        self.textbox.event_generate("<<Undo>>")

    def redo(self):
        self.textbox.event_generate("<<Redo>>")

    def cut(self):
        self.textbox.event_generate("<<Cut>>")

    def copy(self):
        self.textbox.event_generate("<<Copy>>")

    def paste(self):
        self.textbox.event_generate("<<Paste>>")

    def select_all(self):
        self.textbox.tag_add("sel", '1.0', 'end')

    def find(self):
        pass

    def find_next(self):
        pass

    def find_in_selection(self):
        pass
    
    def find_in_files(self):
        pass

    def replace(self):
        pass

    def filter(self):
        pass

    def filter_in_selection(self):
        pass

    def filter_as_previous(self):
        pass

    def go_to(self):
        GoToDialog(self)

    def smart_complete(self):
        pass

    def insert_datetime(self):
        self.textbox.insert(INSERT, datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

    def configuration(self):
        pass

    def check_for_updates(self):
        pass

    def help(self):
        webbrowser.open("help.html")

    def about(self):
        showinfo("About MeowPad", """MeowPad 1.00, (C) Demian Wolf, 2019
MeowPad is an easy, fast, open-source, Python-based, cross-platform text-editor for viewing and editing .txt files, and simple .rtf, .doc(x), .htm(l) etc files.
It can be useful for ordinary users, web-designers and programmers.
Thank you for using my program!""")

if __name__ == "__main__":
    root = MeowPad()
    root.mainloop()
