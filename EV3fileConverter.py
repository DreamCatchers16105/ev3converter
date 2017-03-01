import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import zipfile
import zlib

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        root.iconbitmap('images/Main_icon.ico')
        self.parent = parent
        self.ev3FileName = ""
        self.ev3DirName = ""
        self.expandedFiles = []
        self.parent.geometry("900x450+400+400")

        self.initUI()

    def initUI(self):
        self.parent.title("Simple menu")

        ## MENU
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu1 = tk.Menu(menubar)
        fileMenu1.add_command(label="Open EV3 File...", command=self.onOpenFile)
        fileMenu1.add_command(label="Open EV3 Dir...", command=self.onOpenDir)
        fileMenu1.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=fileMenu1)

        fileMenu2 = tk.Menu(menubar)
        fileMenu2.add_command(label="EV3 file to Expand", command=self.rightButtonCall)
        fileMenu2.add_command(label="Expanded directory to EV3 file", command=self.leftButtonCall)
        menubar.add_cascade(label="Convert", menu=fileMenu2)

        fileMenu3 = tk.Menu(menubar)
        fileMenu3.add_command(label="Preference...", command=self.onPreference)
        fileMenu3.add_command(label="About...", command=self.onAbout)
        menubar.add_cascade(label="Help", menu=fileMenu3)

        ## BUTTONS
        ## Column 1 (center)
        # Convert button: to the right
        self.tmp_right_img = tk.PhotoImage(file="images/right.gif")
        self.button_right = tk.Button(self, text="Expand", image=self.tmp_right_img, command=lambda: self.rightButtonCall(),
                                      compound="top", height=75, width=40, state='disabled')
        self.button_right.grid(row=1, column=1)

        # Convert button: to the left
        self.tmp_left_img = tk.PhotoImage(file="images/left.gif")
        self.button_left = tk.Button(self, text="To EV3", image=self.tmp_left_img, command=lambda: self.leftButtonCall(),
                                     compound="top", height=75, width=40, state='disabled')
        self.button_left.grid(row=2, column=1)

        ## Column 0
        self.ev3TreeLabel = tk.Label(self, text='EV3 file', relief='ridge', width=30, bg='white')
        self.ev3TreeLabel.grid(row=0, column=0, sticky='N')


        self.ev3Tree = ttk.Treeview(self, height=1)
        self.ev3Tree.grid(row=1, column=0, rowspan=3, sticky='N')
        self.ev3Tree.column("#0", minwidth=200, width=400, stretch="NO")
        self.ev3Tree.bind("<Double-1>", self.OnDoubleClick)

        ## Column 2
        self.dirTreeLabel = tk.Label(self, text='Expanded files', relief='ridge', width=30, bg='white')
        self.dirTreeLabel.grid(row=0, column=2, sticky='N')

        self.dirTree = ttk.Treeview(self, height=20)
        self.dirTree.grid(row=1, column=2, rowspan=3)
        self.dirTree.column("#0", minwidth=200, width=400, stretch="NO")

    def OnDoubleClick(self, event):
        newev3FileName = filedialog.asksaveasfile(mode='w', defaultextension=".ev3")
        self.ev3FileName = newev3FileName.name

        self.ev3Tree.delete(*self.ev3Tree.get_children())
        self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
        if os.stat(self.ev3FileName).st_size > 0:
            self.button_right.config(state='normal')
            self.ev3TreeLabel.config(bg='green')
        else:
            self.button_right.config(state='disabled')
            self.ev3TreeLabel.config(bg='yellow')

    def SUBS(self, path, parent):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            parent_element = self.dirTree.insert(parent, 'end', text=p, open=True)
            if os.path.isdir(abspath):
                self.SUBS(abspath, parent_element)

    def onOpenFile(self):
        self.ev3FileName = filedialog.askopenfilename(filetypes=(("EV3 files", "*.ev3"), ("All files", ("*.*"))))
        self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
        if os.stat(self.ev3FileName).st_size > 0:
            self.button_right.config(state='normal')
            self.ev3TreeLabel.config(bg='green')

    def onOpenDir(self):
        self.ev3DirName = filedialog.askdirectory()

        for file in os.listdir(self.ev3DirName):
            if file.startswith("."):
                pass
            else:
                self.expandedFiles.append(file)

        if self.ev3DirName:
            self.button_left.config(state='normal')

        root = self.dirTree.insert('', 'end', text=self.ev3DirName, open=True)
        self.SUBS(self.ev3DirName, root)
        self.dirTreeLabel.config(bg='green')

    def leftButtonCall(self):
        print(self.ev3DirName, " click!")
        if self.ev3FileName == "":
            self.ev3FileName = self.ev3DirName + ".ev3"
#            print(self.ev3FileName, " click!")
            self.ev3Tree.delete(*self.ev3Tree.get_children())
            self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
            if os.path.isfile(self.ev3FileName):
                if os.stat(self.ev3FileName).st_size > 0:
                    self.button_right.config(state='normal')
                    self.ev3TreeLabel.config(bg='green')
            else:
                self.button_right.config(state='disabled')
                self.ev3TreeLabel.config(bg='yellow')

        zout = zipfile.ZipFile(self.ev3FileName, "w", zipfile.ZIP_DEFLATED)
#        head, tail = os.path.split(self.ev3DirName)
#        zout = zipfile.ZipFile(head+"/test.ev3", "w", zipfile.ZIP_DEFLATED)
        zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
        for fname in os.listdir(self.ev3DirName):
            zout.write(self.ev3DirName+"/"+fname, fname)

        zout.close()
        self.ev3FileName = self.ev3DirName+".ev3"
        self.ev3Tree.insert('', 'end', text=self.ev3FileName, open=True)
        if os.stat(self.ev3FileName).st_size > 0:
            self.ev3TreeLabel.config(bg='green')

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
        self.dirTreeLabel.config(bg='green')


    def onEV3ToExpand(self):
        pass

    def onExpandToEV3(self):
        pass

    def onAbout(self):
        pass

    def onPreference(self):
        pass

    def onExit(self):
        self.quit()


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
