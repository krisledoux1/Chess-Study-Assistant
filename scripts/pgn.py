#! /usr/bin/env python3

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
import sys
import tkinter as tk
import tkinter.ttk as ttk
import time
import os.path
###############################################################################################
#version 1.0.0

class pgn_handler:
    def __init__(self, parent, wname, bname):
        self.parent = parent
        self.headers = []           #list for headers of PGN
        self.save_analyze = 0       #close is 0 save is 1 save and analyze is 2
        self.result = tk.StringVar()        #result selected from radio buttons
        self.result.set("*")        

        # make_window(self):
        self.pgn = tk.Toplevel(self.parent)
        self.pgn.title("PGN Handler")
        self.pgn.geometry("700x500+566+195")
        self.pgn.attributes('-topmost', 'true')
        self.pgn.resizable(1,  1)
        self.pgn.configure(background="#43c3cc")

        self.Label1 = tk.Label(self.pgn)
        self.Label1.place(relx=0.043, rely=0.06, height=21, width=70)
        self.Label1.configure(anchor='w')
        self.Label1.configure(compound='left')
        self.Label1.configure(text="Date")

        self.Label2 = tk.Label(self.pgn)
        self.Label2.place(relx=0.043, rely=0.16, height=21, width=70)
        self.Label2.configure(anchor='w')
        self.Label2.configure(compound='left')
        self.Label2.configure(text="White")

        self.Label3 = tk.Label(self.pgn)
        self.Label3.place(relx=0.043, rely=0.26, height=21, width=70)
        self.Label3.configure(anchor='w')
        self.Label3.configure(compound='left')
        self.Label3.configure(text="Black")

        self.Label4 = tk.Label(self.pgn)
        self.Label4.place(relx=0.043, rely=0.36, height=21, width=70)
        self.Label4.configure(anchor='w')
        self.Label4.configure(compound='left')
        self.Label4.configure(text="Result")

        self.Label5 = tk.Label(self.pgn)
        self.Label5.place(relx=0.043, rely=0.46, height=21, width=70)
        self.Label5.configure(anchor='w')
        self.Label5.configure(compound='left')
        self.Label5.configure(text="Comment")
        
        self.Label6 = tk.Label(self.pgn)
        self.Label6.place(relx=0.043, rely=0.56, height=21, width=70)
        self.Label6.configure(anchor='w')
        self.Label6.configure(compound='left')
        self.Label6.configure(text="Event")

        self.Label7 = tk.Label(self.pgn)
        self.Label7.place(relx=0.043, rely=0.66, height=21, width=70)
        self.Label7.configure(anchor='w')
        self.Label7.configure(compound='left')
        self.Label7.configure(text="Site")

        self.Label8 = tk.Label(self.pgn)
        self.Label8.place(relx=0.043, rely=0.76, height=21, width=70)
        self.Label8.configure(anchor='w')
        self.Label8.configure(compound='left')
        self.Label8.configure(text="Round")

        self.ent_date = tk.Entry(self.pgn)
        self.ent_date.place(relx=0.186, rely=0.06, height=23, relwidth=0.143)
        self.ent_date.configure(exportselection="0")
        self.ent_date.configure(font="TkFixedFont")

        self.whitename= tk.StringVar(value=wname) 
        self.ent_white = tk.Entry(self.pgn, textvariable = self.whitename)
        self.ent_white.place(relx=0.186, rely=0.16, height=23, relwidth=0.717)
        self.ent_white.configure(exportselection="0")
        self.ent_white.configure(font="TkFixedFont")

        self.blackname= tk.StringVar(value=bname) 
        self.ent_black = tk.Entry(self.pgn, textvariable = self.blackname)
        self.ent_black.place(relx=0.186, rely=0.26, height=23, relwidth=0.717)
        self.ent_black.configure(exportselection="0")
        self.ent_black.configure(font="TkFixedFont")

        self.ent_comment = tk.Entry(self.pgn)
        self.ent_comment.place(relx=0.186, rely=0.46, height=23, relwidth=0.717)
        self.ent_comment.configure(exportselection="0")
        self.ent_comment.configure(font="TkFixedFont")

        self.ent_event = tk.Entry(self.pgn)
        self.ent_event.place(relx=0.186, rely=0.56, height=23, relwidth=0.717)
        self.ent_event.configure(exportselection="0")
        self.ent_event.configure(font="TkFixedFont")

        self.ent_site = tk.Entry(self.pgn)
        self.ent_site.place(relx=0.186, rely=0.66, height=23, relwidth=0.717)
        self.ent_site.configure(exportselection="0")
        self.ent_site.configure(font="TkFixedFont")

        self.ent_round = tk.Entry(self.pgn)
        self.ent_round.place(relx=0.186, rely=0.76, height=23, relwidth=0.143)
        self.ent_round.configure(exportselection="0")
        self.ent_round.configure(font="TkFixedFont")

        self.Radiobutton1 = tk.Radiobutton(self.pgn)
        self.Radiobutton1.place(relx=0.343, rely=0.36, relheight=0.046
                , relwidth=0.129)
        self.Radiobutton1.configure(text="1-0")
        self.Radiobutton1.configure(variable=self.result)
        self.Radiobutton1.configure(value="1-0")  
        self.Radiobutton1.configure(command=self.rb_pressed)              

        self.Radiobutton2 = tk.Radiobutton(self.pgn)
        self.Radiobutton2.place(relx=0.486, rely=0.36, relheight=0.046
                , relwidth=0.13)
        self.Radiobutton2.configure(text="0-1")
        self.Radiobutton2.configure(variable=self.result)
        self.Radiobutton2.configure(value="0-1")
        self.Radiobutton2.configure(command=self.rb_pressed)  
                
        self.Radiobutton3 = tk.Radiobutton(self.pgn)
        self.Radiobutton3.place(relx=0.629, rely=0.36, relheight=0.046
                , relwidth=0.13)
        self.Radiobutton3.configure(text="1/2-1/2")
        self.Radiobutton3.configure(variable=self.result)
        self.Radiobutton3.configure(value="1/2-1/2")
        self.Radiobutton3.configure(command=self.rb_pressed)  
                
        self.Radiobutton4 = tk.Radiobutton(self.pgn)
        self.Radiobutton4.place(relx=0.771, rely=0.36, relheight=0.046
                , relwidth=0.13)
        self.Radiobutton4.configure(text="*")
        self.Radiobutton4.configure(variable=self.result)
        self.Radiobutton4.configure(value="*")      
        self.Radiobutton4.configure(command=self.rb_pressed)  
                
        self.lbl_result = tk.Label(self.pgn)
        self.lbl_result.place(relx=0.186, rely=0.36, height=21, width=100)
        self.lbl_result.configure(anchor='w')
        self.lbl_result.configure(compound='left')
        self.lbl_result.configure(text=self.result.get())

        self.Button1 = tk.Button(self.pgn)
        self.Button1.place(relx=0.20, rely=0.88, height=31, width=90)
        self.Button1.configure(compound='left')
        self.Button1.configure(text="Save PGN")
        self.Button1.configure(command=self.save)
        """
        self.Button2 = tk.Button(self.pgn)
        self.Button2.place(relx=0.35, rely=0.88, height=31, width=140)
        self.Button2.configure(compound='left')
        self.Button2.configure(text="Save & Analyze")
        self.Button2.configure(command=self.saveandanalyze)
        """
        self.Button3 = tk.Button(self.pgn)
        self.Button3.place(relx=0.686, rely=0.88, height=31, width=90)
        self.Button3.configure(compound='left')
        self.Button3.configure(text="Close")
        self.Button3.configure(command=self.close)
        
        self.get_date() 
        
        self.pgn.wait_window()         

    def rb_pressed(self):
        self.lbl_result.config(text = self.result.get())
        print(self.result.get())

    def get_date(self):
        today = time.strftime("%Y.%m.%d")
        self.ent_date.delete(0,tk.END)
        self.ent_date.insert(0,today)  

    def list_headers(self):         #read entry fields and put in list of headers
        self.headers.append(self.ent_event.get())
        self.headers.append(self.ent_site.get())        
        self.headers.append(self.ent_date.get())
        self.headers.append(self.ent_round.get())                                                         
        self.headers.append(self.ent_white.get())
        self.headers.append(self.ent_black.get())        
        self.headers.append(self.result.get())
        self.headers.append(self.ent_comment.get()) 
        #print("was called")        
                
    def destroy_window(self):
        self.pgn.destroy()
        
    def close(self):
        self.save_analyze = 0           # 0 = don't save or analyze
        self.destroy_window()
                                
    def save(self):
        self.save_analyze = 1           # 1 = save but don't analyze
        self.list_headers()
        self.destroy_window()
    """    
    def saveandanalyze(self):
        self.save_analyze = 2           # 2 = save and analyze
        self.list_headers()        
        self.destroy_window()
    """                
    def get_info(self):
        return self.save_analyze, self.headers 
        
def get_headers(window, wname, bname):
    pgn = pgn_handler(window, wname, bname)       #create an object
    saveanalyze, headers = pgn.get_info()   #open the window and get the info
    pgn = ""        #set the object to null
    return saveanalyze, headers

if __name__ == '__main__':
    window = tk.Tk()
    save, headers = get_headers(window, "Ralph Maccio", "Tinkerbell")          #create object chessboard for play or pgn entry    
    print(headers)
    window.mainloop()    
    #pgn_support.main()




