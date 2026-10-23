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
import tkinter as tk
from tkinter import ttk
import os
###############################################################################################
#version 1.0.0
        
class promo_win:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        self.top = tk.Toplevel(top)#, bg= self.ds_color)
        self.top.geometry("600x450+660+210")
        self.top.resizable(False,  False)
        self.top.title("Promotion")
        self.top.configure(background="#a4d3d8")
        #top.wait_visibility()  # Wait until visible to ensure grab works smoothly   
        #top.grab_set()  
        self.top.focus_set()              
        #top.configure(takefocus="1")
        cwd = os.getcwd()
        path = cwd + "/pieces_image/"
        #self.top = top
        self.promo_piece = ""

        self.Label1 = tk.Label(self.top)
        self.Label1.place(relx=0.183, rely=0.089, height=61, width=369)
        self.Label1.configure(activebackground="#d9d9d9")
        self.Label1.configure(compound='left')
        self.Label1.configure(font="-family {DejaVu Sans} -size 18")
        self.Label1.configure(text='''Select promotion piece''')
        
        self.imageq = tk.PhotoImage(file=path+"qwhite.png")
        self.button1 = ttk.Button(
            self.top,            
            image=self.imageq,
            command=self.queen_selected
        )
        self.button1.place(relx=0.3, rely=0.289, height=74, width=74)
        
        self.imager = tk.PhotoImage(file=path+"rwhite.png")
        self.button2 = ttk.Button(
            self.top,            
            image=self.imager,
            command=self.rook_selected
        )
        self.button2.place(relx=0.583, rely=0.289, height=74, width=74)  
             
        self.imageb = tk.PhotoImage(file=path+"bwhite.png")
        self.button3 = ttk.Button(
            self.top,            
            image=self.imageb,
            command=self.bishop_selected
        )
        self.button3.place(relx=0.583, rely=0.511, height=74, width=74)  

        self.imagen = tk.PhotoImage(file=path+"nwhite.png")
        self.button4 = ttk.Button(
            self.top,            
            image=self.imagen,
            command=self.knight_selected
        )
        self.button4.place(relx=0.3, rely=0.511, height=74, width=74)  
        self.top.wait_window()
        
    def get_selected(self):
        if self.promo_piece != "":
            return self.promo_piece

    def queen_selected(self):
        self.promo_piece = "q"
        self.top.destroy()

    def rook_selected(self):
        self.promo_piece = "r"
        self.top.destroy()
        
    def bishop_selected(self):
        self.promo_piece = "b" 
        self.top.destroy()
        
    def knight_selected(self):
        self.promo_piece = "n"
        self.top.destroy()        

def promo(window):
    pp = promo_win(window)
    promoted = ""
    promoted = pp.get_selected() 
    #print("Promoted to ", promoted)  
    del pp                      #object only used for this purpose so delete it      
    return promoted     
                       
if __name__ == "__main__":
    window = tk.Tk()
    ppiece = promo(window)
    print("The piece was promoted to ",ppiece)
    window.mainloop()





