from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

class TaskBar(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg="#1f2a44", height=60)
        self.controller = controller

        self.icons = {
            "home":     self._load_icon("photo/home.png"),
            "gpa":      self._load_icon("photo/gpa.png"),
            "reminder": self._load_icon("photo/reminder.png"),
            "planner":  self._load_icon("photo/planner.png"),
            "exit":     self._load_icon("photo/exit.png")
        }

        self.btn_style = {
            "bg": "#34495e",
            "fg": "white",
            "activebackground": "#3d5a73",
            "activeforeground": "white",
            "relief": "flat",
            "bd": 0,
            "font": ("Segoe UI", 11, "bold"),
            "cursor": "hand2",
            "compound": "left"
        }

        self.columnconfigure((0,1,2,3,4), weight=1, uniform="buttons")
        self.rowconfigure(0, weight=1)

        self._make_button("Home",             "MainMenu",        self.icons["home"],     0)
        self._make_button("GPA Calculator",   "GpaPage",         self.icons["gpa"],      1)
        self._make_button("Simple Reminder",  "SimpleReminder",  self.icons["reminder"], 2)
        self._make_button("Homework Planner", "HomeworkPlanner", self.icons["planner"],  3)
        self._make_exit_button("Exit", self.icons["exit"], 4)

    def _load_icon(self, path, size=(20, 20)):
        img = Image.open(path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _make_button(self, text, page, icon, col):
        b = Button(self, text=text, image=icon,
                   command=lambda: self.controller.show_frame(page),
                   **self.btn_style)
        b.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        b.bind("<Enter>", lambda e: b.config(bg="#3d5a73"))
        b.bind("<Leave>", lambda e: b.config(bg=self.btn_style["bg"]))

    def _make_exit_button(self, text, icon, col):
        def on_exit():
            if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
                self.controller.quit()

        b = Button(self, text=text, image=icon,
                   command=on_exit,
                   **self.btn_style)
        b.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        b.bind("<Enter>", lambda e: b.config(bg="#c0392b"))
        b.bind("<Leave>", lambda e: b.config(bg=self.btn_style["bg"]))
