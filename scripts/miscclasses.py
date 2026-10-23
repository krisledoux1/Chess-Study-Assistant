##############################################################################################
"""
    Chess Study Assistant scripts to create a graphic user interface for Chess Study
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
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import logging
###############################################################################################
#version 1.0.0

class tkbackterm():  #display terminal type output on another frame
    def __init__(self, parent, maxlines = 2000):
        self.parent = parent
        self.maxlines = maxlines

    def buildframe(self):
        self.control_fr = Frame(master = self.parent,bg = "gray")
        self.control_fr.pack(side = TOP, fill = X)
        self.page_fr = Frame(master = self.parent, bg = "white")
        self.page_fr.pack(side = TOP, fill = "both", expand = True)
        self.page_fr.grid_rowconfigure(0, weight = 1)
        self.page_fr.grid_columnconfigure(0, weight = 1)
        self.mainfr = Frame(master = self.page_fr,bg = "white")    #create a frame for each display
        self.mainfr.grid(row = 0, column = 0, sticky ="nsew") #.pack(side = tk.TOP, fill = "both", expand = True)
        self.termfr = Frame(master = self.page_fr,bg = "light blue")    #create a frame for each display
        self.termfr.grid(row = 0, column = 0, sticky ="nsew") #.pack(side = tk.TOP, fill = "both", expand = True)
        # Text widget for output (read-only for user, programmatically updated only)
        self.output_box = ScrolledText(self.termfr, bg='black', fg='white', wrap='word')
        self.output_box.pack(expand=True, fill='both')
        self.output_box.config(state=DISABLED) # Disable user input into the output area
        """
        self.btn_start = Button(
        master = self.termfr,
        text = "Stop Calc",
        #command = self.workerbee,
        width = 15
        )  
        self.btn_start.pack()
        """
        return self.mainfr, self.termfr
                    
    def term(self, text):
        text = text + "\n"
        self.output_box.config(state="normal")  # Enable the widget
        self.output_box.insert(END, text)
        self.output_box.see(END)
        self.output_box.update_idletasks()        
        # Returns "line_count.last_char_index"
        end_index = self.output_box.index("end-1c") 
        line_count = int(end_index.split('.')[0])
        if line_count > self.maxlines:     
            self.output_box.delete("1.0", "51.0")                
        self.output_box.config(state="disabled") # Disable it again  

class err_redirect():
    def __init__(self,p):
        self.p = p        
    def write(self,text):
        #text = text + "\n"
        self.p.term(text, "red")        
    def flush(self):
        pass  

class redirect():
    def __init__(self,p):
        self.p = p        
    def write(self,text):
        #text = text + "\n"
        self.p.term(text, "blue")        
    def flush(self):
        pass  
             
class tkwoterm():  #display terminal type output on another window
    def __init__(self, parent, maxlines = 2000):
        self.parent = parent
        self.maxlines = maxlines           
        
    def buildframe(self):
        
        self.termwin = Toplevel(bg= "black",takefocus=True)
        self.termwin.title('Stockfish Output   (Hold mouse at screen left middle to cancel)')
        width = self.termwin.winfo_screenwidth()
        height = self.termwin.winfo_screenheight() 
        w_h = "892x" + str(height-60)       
        self.termwin.geometry(w_h)
        # Text widget for output (read-only for user, programmatically updated only)
        self.output_box = ScrolledText(self.termwin, bg='black', fg='white', wrap='word')
        self.output_box.pack(expand=True, fill='both')
        self.output_box.tag_config("red_text", foreground='red')
        self.output_box.tag_config("blue_text", foreground = 'light blue')
        #self.output_box.config(state=DISABLED) # Disable user input into the output area
        #self.parent.mainloop() 

    def iconify(self):
        self.termwin.iconify()
        
    def deiconify(self):
        self.termwin.deiconify()
        self.termwin.update()
        self.termwin.focus_force()        
    
    def destroyframe(self):
        self.termwin.destroy()         
                    
    def term(self, text, color = 'white'):
        #self.output_box.config(state="normal")  # Enable the widget
        text = text + "\n"
        if color == "white":                    
            self.output_box.insert(END, text)
        elif color == "red":
            self.output_box.insert(END, text, "red_text") 
        else:
            self.output_box.insert(END, text, "blue_text")                   
        self.output_box.see(END)
        self.output_box.update_idletasks()        
        # Returns "line_count.last_char_index"
        end_index = self.output_box.index("end-1c") 
        line_count = int(end_index.split('.')[0])
        if line_count > self.maxlines:     
            self.output_box.delete("1.0", "51.0")                
        #self.output_box.config(state="disabled") # Disable it again   
        
      
               