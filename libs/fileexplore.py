#! /usr/bin/env python3
##############################################################################################
"""
    Filedialogue script to find and open files on a linux disk system
    Copyright (C) 2026  Kristen K LeDoux

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
###############################################################################################

#import tkinter as tk
import os
import sys
import libs.psutil
import tkinter as tk
#import logging
"""
with open('fileexplore_errors.log', 'w') as f:
# Redirect standard error to the file
#sys.stdout = open('fileexplore_errors.log', 'w')
#sys.stderr = sys.stdout
    sys.stderr = open('fileexplore_errors.log', 'w')
"""
class get_filename():        #
    def __init__(self,initdir=os.path.expanduser('~'),multi = 0, f_ext=["*"]):
        self.multi_select = multi       #single or multi select of files
        self.f_ext = f_ext              #list of file extensions to include in file list (all if just ["*"])
        self.curr_dir = initdir         #initial directory to display
        self.curr_file = ""             #place for file 
        self.curr_drive = initdir       #current drive
        self.got_file = ""              #file selected to return is single select
        self.multi_files = []           #list of files to return if multiselect
        self.checked = 1                #alpha or age checkbox initial value
        self.hidden = 0                 #hidden checkbox initial value
        self.drive_mounts=[]            #lists for mounts directories and files
        self.directrees=[]        
        self.directree_files=[]        
        self.make_window()              #build the window
       
    def init_lists(self):           #get lists for default or ordered dirctory
        self.get_mounts()           #read and get the drives available
        self.get_dirs_files()       #get a list of files and directories for current directory
        self.fill_lists()           #fill the lists with the data 
        self.set_drives_list()        

    def name_is(self):              #for returning single selection
        return self.curr_dir, self.got_file          

    def names_are(self):            #for returning multi selections 
        return self.curr_dir, self.multi_files 
            
    def get_mounts(self):
        home_directory = os.path.expanduser('~')
        self.drive_mounts.clear()
        self.drive_mounts.append(home_directory)     #start a list of drive mounts with the home directory          
        #get drive mount points in linux
        for partition in libs.psutil.disk_partitions():
            # For Linux, '/dev/sd' followed by a letter (e.g., 'sdb1') is common for USB.
            if partition.device.startswith('/dev/sd'):
                # Filter out internal drives if necessary (e.g., by checking mountpoint)
                if "/boot" not in partition.mountpoint:         #eliminate boot partitions as not usb in any case I am using
                    if "snap" not in partition.mountpoint:      #eliminate snap as snap sucks
                        self.drive_mounts.append(partition.mountpoint)     #include all others in list
                        #print(partition.mountpoint)      

    def set_drives_list(self):
        # Retrieve all items as a Python tuple/list
        all_items = self.drives_lst.get(0, tk.END)
        try:
            # Use Python's built-in index method
            index = all_items.index(self.curr_drive)
            #print(f"Item '{self.curr_dir}' found at index: {index}")
        except ValueError:
            # Handle cases where the item is not found
            #print(f"Item '{self.curr_dir}' not found in the list.")
            return -1
        self.drives_lst.selection_clear(0, tk.END)
        self.drives_lst.selection_set(index)
        self.drives_lst.see(index)

    def filter_ext(self, file):
        extension = file.rpartition(".")[-1]    #[-1] will give without dot 
        #print (file, " ",extension)        
        if extension in self.f_ext:
            return True
        else:
            return False    
            
    def get_dirs_files(self):
        self.directree_files.clear()
        self.directrees.clear()
        if "*" not in self.f_ext:
            filt = True
        else:
            filt = False
        if not os.path.isdir(self.curr_dir):          #make sure directory path exists
            self.curr_dir =os.path.expanduser('~')      #if directory doesn't exist set to home
        temp = []
        for file in os.listdir(self.curr_dir): 
            if not self.hidden:
                if file.startswith("."):
                    continue        #skip over all hidden files so not in list  
            if os.path.isfile(os.path.join(self.curr_dir, file)):       #if this is a file
                if filt:        #if there is a filter
                    if self.filter_ext(file):                    #check extension in list. If it is append
                        temp.append(os.path.join(self.curr_dir, file))
                else:
                    temp.append(os.path.join(self.curr_dir, file))
            else:                                                       #if this is a directory
                if self.curr_dir != "/":        #if not root add a /
                    full_path = self.curr_dir + "/" + file      #file is a directory name here
                else:
                    full_path = self.curr_dir + file
                self.directrees.append(full_path)     
        #self.directrees.sort(key=str.lower)
        temp = sorted(temp,key=os.path.getmtime,reverse=True) #sort files by newest to oldest (reverse)
        for file in temp:
            _,_,justname = file.rpartition("/")
            self.directree_files.append(justname)
        if self.checked: 
            self.directrees.sort(key=str.lower)                       
            self.directree_files.sort(key=str.lower) 
                                       
    def fill_lists(self):
        #fill in the drives listbox
        self.drives_lst.delete(0,tk.END)        #clear the list
        for i in self.drive_mounts:
            self.drives_lst.insert(tk.END,i)
        self.dirs_lst.delete(0,tk.END)
        for i in self.directrees:
            currdirlen = len(self.curr_dir)
            self.dirs_lst.insert(tk.END,i[currdirlen:])
        self.files_lst.delete(0,tk.END)
        for i in self.directree_files:
            self.files_lst.insert(tk.END,i) 
        self.set_drives_list()
        self.lbl_currdir.configure(text=self.curr_dir)
        self.lbl_fname.configure(text=self.curr_file)                  
                                      
    #end fill_lists                        

    def dr_select(self):
        selected_index = self.drives_lst.curselection()  # Get the selected item's index               
        if selected_index:
            self.curr_drive =  self.drives_lst.get(selected_index[0])  # Get the selected item
            self.curr_dir = self.curr_drive
            self.get_dirs_files()
            self.fill_lists()  
        self.drives_lst.selection_clear(0, "end")
        self.drives_lst.selection_set(selected_index)
        self.curr_file = "" 
        self.lbl_fname.configure(text=self.curr_file)
        
    def dir_select(self):
        selected_index = self.dirs_lst.curselection()  # Get the selected item's index
        try:
            index = selected_index[0] 
        except:
            return -1                         
        if selected_index:
            #self.curr_dir =  self.dirs_lst.get(selected_index[0])  # Get the selected item
            self.curr_dir = self.directrees[index]
            self.get_dirs_files()
            self.fill_lists()  
        self.dirs_lst.selection_clear(0, "end")
        self.dirs_lst.selection_set(selected_index)
        self.curr_file = ""
        self.lbl_fname.configure(text=self.curr_file)        
        
    def files_select(self):
        selected_index = self.files_lst.curselection()  # Get the selected item's index 
        try:        #make sure list is not empty
            index = selected_index[0] 
        except:
            return -1   
        if self.multi_select == 0:          #when multiple select is one filename returned                                  
            if selected_index:
                self.curr_file =  self.files_lst.get(selected_index[0])  # Get the selected item
                #self.get_dirs_files()
                #self.fill_lists()
            self.lbl_fname.configure(text=self.curr_file)  
            self.files_lst.selection_clear(0, "end")
            self.files_lst.selection_set(selected_index) 
            self.files_lst.see(selected_index) 
        else:               #if multi select selecting one or more files 
            self.multi_files.clear()
            selected_indices = self.files_lst.curselection()
            #selected_items = []
            for index in selected_indices:
                item_text = self.files_lst.get(index)
                self.multi_files.append(item_text)
            print(self.multi_files)         
                                 
    def listselect(self):       #called on a double click
        selected_index = self.files_lst.curselection()  # Get the selected item's index
        if selected_index:
            start_dir = self.files_lst.get(selected_index[0])  # Get the selected item
        else:
            start_dir = ""
            #print("No item selected")
            return
        if start_dir:
            if start_dir == "":
                start_dir = os.path.expanduser('~')
                print("this is run")
            #print(" start ",start_dir)
            self.got_file = start_dir
    #end def listselect

    def change_dir_up(self):
        #print(self.curr_dir)
        parent,_,_ = self.curr_dir.rpartition("/")
        #print(parent)
        if parent:
            self.curr_dir = parent
        else:       
            self.curr_dir = parent + "/"  
        self.get_dirs_files()
        self.fill_lists()        
    #end def change_dir_up  
    
    def cb_aa_clicked(self):        #alpha or age
        if self.checked:
            self.checked = 0
        else:
            self.checked = 1
        self.init_lists()   

    def cb_hidden_clicked(self):        #hidden files included
        if self.hidden:
            self.hidden = 0
        else:
            self.hidden = 1
        self.init_lists() 
      
    def make_window(self):
        # create the maininitwin window
        self.maininitwin = tk.Tk()
        self.maininitwin.title("Filedialog Plus")
        self.maininitwin.geometry('1000x800')
        self.maininitwin.configure(bg="white")
        # Configure the main window's grid to allow frames to expand
        self.maininitwin.grid_columnconfigure(0, weight=1)
        self.maininitwin.grid_columnconfigure(1, weight=4)
        self.maininitwin.grid_columnconfigure(2, weight=4)
        self.maininitwin.grid_rowconfigure(0, weight=1)
        self.maininitwin.grid_rowconfigure(1, weight=25)
        self.maininitwin.grid_rowconfigure(2, weight=1) 
        f_fb = "light gray"     #frame backgrounds
        
        def dr_selected(event):
            self.dr_select()
               
        def dir_selected(event):
            self.dirs_lst.after(100)        
            self.dir_select()
                
        def file_selected(event):
            '''  delay mouse action to allow for double click to occur if needed
            '''
            self.files_lst.after(100)
            self.files_select()            

        def f_double_click(event):
            #if self.curr_file:
            self.listselect()
            self.maininitwin.destroy()  
                
        #heading frames
        h0_frame = tk.Frame(master = self.maininitwin, bg=f_fb)
        h0_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        lbl_m_ip = tk.Label(
            master = h0_frame,
            font=('arial', 14, 'normal'),
            bg = f_fb,
            fg = "black",
            text = "Available Mounted Drives",
            width = 21,
            anchor = "w"
        )
        lbl_m_ip.pack(side = tk.BOTTOM, anchor = "w")

        h1_frame = tk.Frame(master = self.maininitwin, bg=f_fb)
        h1_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")       
        lbl_frm = tk.Frame(master = h1_frame, bg=f_fb)
        lbl_frm.pack(side = tk.BOTTOM, fill = tk.X)       
        lbl_dirs = tk.Label(
            master = lbl_frm,
            font=('arial', 14, 'normal'),
            bg = f_fb,
            fg = "black",
            text = "Directories",
            width = 16,
            anchor = "w"
        )
        #lbl_dirs.grid(column=0, padx=10, pady=10, sticky="ew")        
        lbl_dirs.pack(side = tk.LEFT, anchor = "w")            
        btn_up = tk.Button(
            master = lbl_frm,
            text = "UP",
            width = 4,
            command = self.change_dir_up 
        )
        #btn_up.grid(column=1)#, padx=10, pady=10, sticky="nsew")            
        btn_up.pack(side = tk.RIGHT)#, anchor = "e")
                
        h2_frame = tk.Frame(master = self.maininitwin, bg=f_fb)
        h2_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.lbl_currdir = tk.Label(
            master = h2_frame,
            font=('arial', 14, 'normal'),
            bg = f_fb,
            fg = "black",
            text = self.curr_dir,
            width = 48,
            anchor = "w"
        )
        self.lbl_currdir.pack(side = tk.BOTTOM, anchor = "w")        
        lbl_m_ip = tk.Label(
            master = h2_frame,
            font=('arial', 14, 'normal'),
            bg = f_fb,
            fg = "black",
            text = "Files in Directory",
            width = 48,
            anchor = "w"
        )
        lbl_m_ip.pack(side = tk.BOTTOM, anchor = "w")                                    
        #create the drive frame dr_frame and list                  
        dr_frame = tk.Frame(master = self.maininitwin, bg=f_fb)
        dr_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        drlist_frm = tk.Frame(master = dr_frame, bg="white") 
        drlist_frm.pack(side=tk.TOP, fill = "both", expand=True)       
        self.drives_lst = tk.Listbox(master = drlist_frm, exportselection=False, selectmode=tk.SINGLE)
        scr_text= tk.Scrollbar(master = drlist_frm, command=self.drives_lst.yview, orient="vertical")
        self.drives_lst.configure(yscrollcommand=scr_text.set)
        #self.drives_lst.bind('<Button-1>', dr_mouse_click)
        self.drives_lst.bind("<<ListboxSelect>>", dr_selected)
        #self.drives_lst.bind('<Double-1>', dr_double_click)
        self.drives_lst.pack(side="left", fill="both", expand=True)#, fill="both")#, expand=True)   
        scr_text.pack(side="right", fill="y")

        opt_frm = tk.Frame(master = dr_frame, bg="light gray")
        opt_frm.pack(side = tk.BOTTOM, fill = tk.X) 
        # This is the section of code which creates a checkbox for alpha
        self.ch_bx_aa=tk.Checkbutton(opt_frm,
            text='ALPHA / AGE',
            command = self.cb_aa_clicked,
            font=('arial', 12, 'normal'),
            highlightthickness = 0)
        self.ch_bx_aa.pack(side = tk.TOP, anchor = "w")
        self.ch_bx_aa.select() 
        # This is the section of code which creates a checkbox for hidden files
        self.ch_hidden=tk.Checkbutton(opt_frm,
            text='Hidden',
            command = self.cb_hidden_clicked,
            font=('arial', 12, 'normal'),
            highlightthickness = 0)
        self.ch_hidden.pack(side = tk.TOP, anchor = "w")
        #self.ch_hidden.select()                
        #create the directory frame d_frame and list                  
        d_frame = tk.Frame(master = self.maininitwin, bg=f_fb)
        d_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.dirs_lst = tk.Listbox(master = d_frame, exportselection=False, selectmode=tk.SINGLE)
        self.scr_text1= tk.Scrollbar(master = d_frame, command=self.dirs_lst.yview, orient="vertical")
        self.dirs_lst.configure(yscrollcommand=self.scr_text1.set)
        self.dirs_lst.bind("<<ListboxSelect>>", dir_selected)
        #self.dirs_lst.bind('<Double-1>', f_double_click)        
        self.dirs_lst.bind('<Return>', f_double_click)
        self.dirs_lst.bind('<KP_Enter>', f_double_click)        
        self.dirs_lst.pack(side="left", fill="both", expand=True)   
        self.scr_text1.pack(side="right", fill="y")        

        #create the files frame f_frame and list                  
        f_frame = tk.Frame(master = self.maininitwin, bg=f_fb)
        f_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        if self.multi_select == 0:          #0 is single select
            self.files_lst = tk.Listbox(master = f_frame, exportselection=False, selectmode=tk.SINGLE)
        else:
            self.files_lst = tk.Listbox(master = f_frame, exportselection=False, selectmode=tk.EXTENDED)
        self.scr_text2= tk.Scrollbar(master = f_frame, orient="vertical")
        self.scr_text2.config(command=self.files_lst.yview)
        self.files_lst.configure(yscrollcommand=self.scr_text2.set)
        self.files_lst.bind("<<ListboxSelect>>", file_selected)
        self.files_lst.bind('<Double-1>', f_double_click)
        self.files_lst.bind('<Return>', f_double_click)  
        self.files_lst.bind('<KP_Enter>', f_double_click)      
        self.files_lst.pack(side="left", fill="both", expand=True)#, fill="both")#, expand=True)   
        self.scr_text2.pack(side="right", fill="y")         

        fn_frame = tk.Frame(master = self.maininitwin, bg=f_fb)
        fn_frame.grid(row=2, columnspan=3, padx=10, pady=10, sticky="nsew")
        fn_frm = tk.Frame(master = fn_frame)
        fn_frm.pack(side = tk.TOP, anchor = "w")
        self.lbl_fname = tk.Label(
            master = fn_frm,
            font=('arial', 14, 'normal'),
            bg = f_fb,
            fg = "black",
            text = self.curr_file,
            width = 96,
            anchor = "w"
        )
        self.lbl_fname.pack(side = tk.BOTTOM, anchor = "w")         
        
        self.maininitwin.after(100, self.init_lists())
        # run the application
        self.maininitwin.wait_window()
"""
The called function that will return the filename or filenames
Call with options
First option is initial directory.  This defaults to users home directory unless option sent.
Second option is list of file extensions to display.  Defaults to all.
"""      
def file_is(initdir=os.path.expanduser('~'), f_ext=["*"]):
    fname = get_filename(initdir, 0, f_ext)# create an instance for single select 0
    sdir, sfile = fname.name_is()
    sfile = sdir + "/" + sfile          #return file with full path
    home_directory = os.path.expanduser('~')
    if sdir == "":
        sdir = home_directory 
    #sys.stderr = sys.__stderr__            
    return sdir, sfile
    
def files_are(initdir=os.path.expanduser('~'), f_ext=["*"]): #create an instance for multi select
    fname = get_filename(initdir, 1)# create an instance for multi select 1
    sdir, sfiles = fname.names_are()
    ffiles = []
    for file in sfiles:         #create full path for all files selected
        ffiles.append(sdir + "/" + file)
    home_directory = os.path.expanduser('~')
    if sdir == "":
        sdir = home_directory  
    #sys.stderr = sys.__stderr__                    
    return sdir, ffiles

if __name__ == '__main__':
    spath, sfile = file_is()
    print ("This is the path ",spath)
    print ("This is the filename ",sfile) 
    print (sfile) 

