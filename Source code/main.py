from tkinter import *
from pages.main_menu import MainMenu
from pages.gpa_page import GpaPage
import matplotlib.pyplot as plt


#12313122
#qweqwewqe
class StudentAssistantApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("TAR UMT Student Assistant App")
        self.geometry("800x450")

        container = Frame(self)
        container.place(relwidth=1, relheight=1)

        self.frames = {}

        for F in (MainMenu, GpaPage):
            page = F(parent=container, controller=self)
            self.frames[F.__name__] = page
            page.place(relwidth=1, relheight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.show_frame("MainMenu")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def show_main_menu(self):
        self.show_frame("MainMenu")

    def on_closing(self):
        plt.close('all')
        self.destroy()  
    
if __name__ == "__main__":
    app = StudentAssistantApp()
    app.mainloop()