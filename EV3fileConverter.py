import os
import shutil
import tkinter as tk
import zipfile
import zlib
from tkinter import filedialog
from tkinter import font
from tkinter import ttk
from PIL import Image, ImageTk

'''
This program is designed to expand the LEGO EV3 project file into
small files mostly in ascii format.  Some files still remain in binary
but all of your programs will be converted to ascii.
This conversion may be useful if you want to do version control in a
team environment using GitHub, SVN, or other source code version control
system.  When you are ready you can convert the directory to a EV3 file
that you can open in the EV3 software from LEGO

Created on 01MAR2017 by Kevin Choi (choikk@gmail.com)
Team DreamCatchers (#16105) FLL Coach in Maryland

Software Version 0.1.2

Copyright (2017) Kevin Choi
All Rights Reserved.


For one-file executable, run
(for Windows)
>> pyinstaller myEV3fileConverterWin64.spec
or
(for OSX)
>> pyinstaller myEV3fileConverterOSX.spec
'''

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ''' Initialize the class'''
        tk.Frame.__init__(self, parent, *args, **kwargs)
#        root.iconbitmap('images/Main_icon.ico')
        self.parent = parent
        self.ev3FileName = ""
        self.ev3DirName = ""
        self.expandedFiles = []
        self.fileMenu1 = ""
        self.fileMenu2 = ""
        self.fileMenu3 = ""
        self.parent.geometry("875x485+250+250")

        cfont = font.Font(family="Consolas", size=10, weight="normal")
        self.char_size = cfont.measure("a")
        self.bind("<Configure>", self.on_resize)
        self.height = 485
        self.width = 875

#        self.height = self.winfo_reqheight()
#        self.width = self.winfo_reqwidth()
        self.label_width = round((self.width - 43) * 0.32 / self.char_size)
#        print (self.char_size, self.width, self.label_width)
        self.initUI()

    def initUI(self):
        '''Buttons and menu definition '''
        self.parent.title("EV3 File Converter")

        ## MENU
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        self.fileMenu1 = tk.Menu(menubar)
        self.fileMenu1.add_command(label="New EV3 File...", command=self.onNewFile)
        self.fileMenu1.add_command(label="Open EV3 File...", command=self.onOpenFile)
        self.fileMenu1.add_command(label="Open EV3 Dir...", command=self.onOpenDir)
        self.fileMenu1.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=self.fileMenu1)

        self.fileMenu2 = tk.Menu(menubar)
        self.fileMenu2.add_command(label="EV3 file to Expand", command=self.rightButtonCall, state='disabled')
        self.fileMenu2.add_command(label="Expanded directory to EV3 file", command=self.leftButtonCall, state='disabled')
        menubar.add_cascade(label="Convert", menu=self.fileMenu2)

        self.fileMenu3 = tk.Menu(menubar)
        self.fileMenu3.add_command(label="Preference...", command=self.onPreference)
        self.fileMenu3.add_command(label="About...", command=self.onAbout)
        menubar.add_cascade(label="Help", menu=self.fileMenu3)

        ## BUTTONS
        ## Column 1 (center)
        # Convert button: to the right
        rightpath=self.resource_path("right.gif")
        self.tmp_right_img = tk.PhotoImage(file=rightpath)
        self.button_right = tk.Button(self, text="Expand", image=self.tmp_right_img, command=lambda: self.rightButtonCall(),
                                      compound="top", height=75, width=40, state='disabled')
        self.button_right.grid(row=3, column=2)
        self.tempLabel = tk.Label(self, text=None, relief=None, width=round(40/self.char_size), bg=None)
        self.tempLabel.grid(row=0, column=2, sticky='N',pady=1)

        self.button_ev3new = tk.Button(self, text="New..",
                                      command=lambda: self.onNewFile(),
                                      compound="top", height=1, width=5, state='normal')
        self.button_ev3new.grid(row=1, column=0, sticky='NW', padx=5, pady=1)

        self.button_ev3open = tk.Button(self, text="Open..",
                                      command=lambda: self.onOpenFile(),
                                      compound="top", height=1, width=5, state='normal')
        self.button_ev3open.grid(row=1, column=1, sticky='NW', padx=5, pady=1)

        self.button_diropen = tk.Button(self, text="Open Dir..",
                                      command=lambda: self.onOpenDir(),
                                      compound="top", height=1, width=8, state='normal')
        self.button_diropen.grid(row=1, column=3, sticky='NW', padx=5, pady=1)

        # Convert button: to the left
        leftpath = self.resource_path("left.gif")
        self.tmp_left_img = tk.PhotoImage(file=leftpath)
        self.button_left = tk.Button(self, text="To EV3", image=self.tmp_left_img, command=lambda: self.leftButtonCall(),
                                     compound="top", height=75, width=40, state='disabled')
        self.button_left.grid(row=4, column=2)

        ## Column 0
        self.ev3TreeLabel = tk.Label(self, text='EV3 file', relief='ridge', width=self.label_width, bg='white')
        self.ev3TreeLabel.grid(row=0, column=0, columnspan=2, sticky='WNE',padx=5,pady=1)

        self.ev3Tree = ttk.Treeview(self, height=1)
        self.ev3Tree.grid(row=2, column=0, rowspan=3, columnspan=2, sticky='NWE',padx=5, pady=1)
        self.ev3Tree.column('#0', minwidth=20, width=50, stretch=True)
        # self.ev3Tree.bind("<Button-1>", self.onOpenFileTree)
        # self.ev3Tree.bind("<Double-1>", self.onDoubleClickL)
        # self.ev3Tree.bind("<Enter>", self.on_enterL)
        # self.ev3Tree.bind("<Leave>", self.on_leaveL)
        self.ev3Tree.grid_columnconfigure(0, weight=2)

        ## Column 2
        self.dirTreeLabel = tk.Label(self, text='Expanded files', relief='ridge', width=self.label_width, bg='white')
        self.dirTreeLabel.grid(row=0, column=3, sticky='WNE', padx=5, pady=1)

        self.dirTree = ttk.Treeview(self, height=22)
        self.dirTree.grid(row=2, column=3, rowspan=60, sticky='WEN',padx=5, pady=1)
        self.dirTree.column("#0", minwidth=20, width=50, stretch=True)
        # self.dirTree.bind("<Button-1>", self.onOpenDirTree)
        # self.dirTree.bind("<Double-1>", self.onDoubleClickR)
        # self.dirTree.bind("<Enter>", self.on_enterR)
        # self.dirTree.bind("<Leave>", self.on_leaveR)
        self.dirTree.grid_columnconfigure(0, weight=2)

#       logo = Image.open(self.resource_path("DreamCatchers_Logo_512.jpg"))
#        photo = ImageTk.PhotoImage(logo)

#        self.label = tk.Label(image=photo)
#        self.label.image = photo  # keep a reference!
#        self.label.grid(row=2, column=0, sticky='WN',padx=5, pady=1)

    def onNewFile(self):
        newev3FileName = filedialog.asksaveasfile(mode='w', title='New EV3 file',filetypes=[("EV3 file",".ev3")],defaultextension=".ev3")
        try:
            self.ev3FileName = newev3FileName.name

            self.ev3Tree.delete(*self.ev3Tree.get_children())
            self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
            if os.stat(self.ev3FileName).st_size > 0:
                self.button_right.config(state='normal')
                self.ev3TreeLabel.config(bg='#ADFF2F')
            else:
                self.button_right.config(state='disabled')
                self.ev3TreeLabel.config(bg='yellow')
        except:
            pass

    def onDoubleClickL(self, event):
        newev3FileName = filedialog.asksaveasfile(mode='w', filetypes=[("EV3 file",".ev3")],defaultextension=".ev3")
        try:
            self.ev3FileName = newev3FileName.name

            self.ev3Tree.delete(*self.ev3Tree.get_children())
            self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
            if os.stat(self.ev3FileName).st_size > 0:
                self.button_right.config(state='normal')
                self.ev3TreeLabel.config(bg='#ADFF2F')
            else:
                self.button_right.config(state='disabled')
                self.ev3TreeLabel.config(bg='yellow')
        except:
            pass

    def onDoubleClickR(self, event):
        self.onOpenDir()

    def SUBS(self, path, parent):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            parent_element = self.dirTree.insert(parent, 'end', text=p, open=True)
            if os.path.isdir(abspath):
                self.SUBS(abspath, parent_element)

    def onOpenFileTree(self, event):
        self.ev3FileName = filedialog.askopenfilename(filetypes=(("EV3 files", "*.ev3"), ("All files", ("*.*"))))

        try:

            self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
            if os.stat(self.ev3FileName).st_size > 0:
                self.button_right.config(state='normal')
                self.fileMenu2.entryconfig("EV3 file to Expand", state="normal")
                self.ev3TreeLabel.config(bg='#ADFF2F')
        except:
            pass

    def onOpenFile(self):
        self.ev3FileName = filedialog.askopenfilename(filetypes=(("EV3 files", "*.ev3"), ("All files", ("*.*"))))

        try:
            self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
            if os.stat(self.ev3FileName).st_size > 0:
                self.button_right.config(state='normal')
                self.fileMenu2.entryconfig("EV3 file to Expand", state="normal")
                self.ev3TreeLabel.config(bg='#ADFF2F')
        except:
            pass

    def onOpenDirTree(self, event):
        self.ev3DirName = filedialog.askdirectory()

        try:
            for file in os.listdir(self.ev3DirName):
                if file.startswith("."):
                    pass
                else:
                    self.expandedFiles.append(file)

            if self.ev3DirName:
                self.button_left.config(state='normal')
                self.fileMenu2.entryconfig("Expanded directory to EV3 file", state="normal")

            root = self.dirTree.insert('', 'end', text=self.ev3DirName, open=True)
            self.SUBS(self.ev3DirName, root)
            self.dirTreeLabel.config(bg='#ADFF2F')
        except:
            pass

    def onOpenDir(self):
        self.ev3DirName = filedialog.askdirectory()

        try:
            for file in os.listdir(self.ev3DirName):
                if file.startswith("."):
                    pass
                else:
                    self.expandedFiles.append(file)

            if self.ev3DirName:
                self.button_left.config(state='normal')
                self.fileMenu2.entryconfig("Expanded directory to EV3 file", state="normal")

            root = self.dirTree.insert('', 'end', text=self.ev3DirName, open=True)
            self.SUBS(self.ev3DirName, root)
            self.dirTreeLabel.config(bg='#ADFF2F')
        except:
            pass

    def leftButtonCall(self):
#        print(self.ev3DirName, " click!")
        if self.ev3FileName == "":
            self.ev3FileName = self.ev3DirName + ".ev3"
            print(self.ev3FileName, " click!")
            self.ev3Tree.delete(*self.ev3Tree.get_children())
            self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
            if os.path.isfile(self.ev3FileName):
                if os.stat(self.ev3FileName).st_size > 0:
                    self.button_right.config(state='normal')
                    self.fileMenu2.entryconfig("EV3 file to Expand", state="normal")
                    self.ev3TreeLabel.config(bg='#ADFF2F')
            else:
                self.button_right.config(state='disabled')
                self.fileMenu2.entryconfig("EV3 file to Expand", state="disabled")
                self.ev3TreeLabel.config(bg='yellow')

        zout = zipfile.ZipFile(self.ev3FileName, "w", zipfile.ZIP_DEFLATED)
#        head, tail = os.path.split(self.ev3DirName)
#        zout = zipfile.ZipFile(head+"/test.ev3", "w", zipfile.ZIP_DEFLATED)
        zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
        for fname in os.listdir(self.ev3DirName):
            zout.write(self.ev3DirName+"/"+fname, fname)

        zout.close()

        self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
        if os.stat(self.ev3FileName).st_size > 0:
            self.button_right.config(state='normal')
            self.fileMenu2.entryconfig("EV3 file to Expand", state="normal")
            self.ev3TreeLabel.config(bg='#ADFF2F')

    def rightButtonCall(self):
        self.dirTree.delete(*self.dirTree.get_children())
        #print(self.ev3FileName, " click!")
        tempfile = self.ev3FileName+'.tmp'
        shutil.copy(self.ev3FileName, tempfile)
        temppath = os.path.dirname(self.ev3FileName)
        filename = os.path.basename(self.ev3FileName)
        idx_dot = filename.index('.')
        filename_without_extension = filename[:idx_dot]
        newpath = temppath+"/"+filename_without_extension
        self.ev3DirName = newpath
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        zip_ref = zipfile.ZipFile(tempfile, 'r')
        zip_ref.extractall(newpath)
        zip_ref.close()
        os.remove(tempfile)

        root = self.dirTree.insert('', 'end', text=newpath, open=True)
        self.SUBS(newpath, root)
        self.button_left.config(state='normal')
        self.fileMenu2.entryconfig("Expanded directory to EV3 file", state="normal")
        self.dirTreeLabel.config(bg='#ADFF2F')


    def onAbout(self):
        t = tk.Toplevel(self)
        t.wm_title("About...")
        lines = ['This program is designed to expand the LEGO EV3 project file into ',
                 'small files mostly in ascii format.  Some files still remain in binary',
                 'but all of your programs will be converted to ascii.                 ',
                 'This conversion may be useful if you want to do version control in a  ',
                 'team environment using GitHub, SVN, or other source code version control',
                 'system.  When you are ready you can convert the directory to a EV3 file',
                 'that you can open in the EV3 software from LEGO',
                 '',
                 'Created on 01MAR2017 by Kevin Choi (choikk@gmail.com), ',
                 'Team DreamCatchers (#16105) FLL Coach in Maryland',
                 'Software Version 0.1.2',
                 '',
                 'Copyright (2017) Kevin Choi',
                 'All Rights Reserved',
                 '',
                 'Permission is hereby granted, free of charge, to any person obtaining a ',
                 'copy of this software and associated documentation files (the "Software"),',
                 'to deal in the Software without restriction, including without limitation ',
                 'the rights to use, copy, modify, merge, publish, distribute, sublicense, ',
                 'and/or sell copies of the Software, and to permit persons to whom the Software',
                 'is furnished to do so, subject to the following conditions:',
                 '',
                 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR ',
                 'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS',
                 'FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR ',
                 'COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN',
                 'AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION ',
                 'WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.']

        l = tk.Label(t,text="\n".join(lines))
        l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        pass

    def onPreference(self):
        t = tk.Toplevel(self)
        t.wm_title("Preference...")
        lines = ['Preference comes here...',
                 '',
                ]
        l = tk.Label(t,text="\n".join(lines))
        l.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        pass

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath("./images")
        return os.path.join(base_path, relative_path)


    def on_enterL(self, event):
        self.ev3TreeLabel.configure(text="Double click to assign a new file name")

    def on_leaveL(self, enter):
        self.ev3TreeLabel.configure(text="EV3 file")

    def on_enterR(self, event):
        self.dirTreeLabel.configure(text="Double click to open an expanded directory")

    def on_leaveR(self, enter):
        self.dirTreeLabel.configure(text="Expanded files")

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        self.width = event.width
        self.height = event.height

        # resize the canvas
        self.config(width=self.width, height=self.height)

        # TODO I don't understand why Windows and OSX have different width dimension.
        self.label_width  = round((self.width - 43) * 0.32/ self.char_size)
        self.label_height = round((self.height/ self.char_size))
        # rescale all the objects tagged with the "all" tag
#        self.scale("all",0,0,wscale,hscale)
        self.ev3TreeLabel.config(width=self.label_width)
        self.dirTreeLabel.config(width=self.label_width-3)

#        print (self.width / self.char_size, self.height / self.char_size, self.label_width, self.label_height)

    def onExit(self):
        self.quit()


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
