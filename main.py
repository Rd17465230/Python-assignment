from tkinter import *
from PIL import Image, ImageTk
from resize import Resize
from pages.gpa_page import GpaPage
from pages.homeworkPlanner import HomeworkPlanner
from pages.simpleReminder import SimpleReminder
from pages.login_page import LoginPage
from taskbar import TaskBar
import matplotlib.pyplot as plt


class HomePage(Frame, Resize):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        Resize.__init__(self)
        self.controller = controller

        self.ori_img = Image.open(r"photo/background.jpg")
        self.bg_label = Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.title = Label(self,
                           text="Welcome to TAR UMT Student Assistant",
                           bg="#ADD8E6",font=("Arial", 25, "bold"))
        self.title.place(relx=0.5, rely=0.2,
                         relwidth=0.5, relheight=0.1,
                         anchor="center")

        self.after(1, self.update_layout)

    def update_layout(self):
        w, h = self.winfo_width(), self.winfo_height()
        if w > 0 and h > 0:
            resized_img = self.ori_img.resize((w, h), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_img)
            self.bg_label.configure(image=self.bg_image)
            self.bg_label.image = self.bg_image

class StudentAssistantApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("TAR UMT Student Assistant")
        self.iconphoto(False, PhotoImage(file="photo/app_icon.png"))

        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: None)

        self.root_container = Frame(self)
        self.root_container.pack(fill="both", expand=True)

        self.frames_container = Frame(self.root_container)
        self.frames_container.pack(side="top", fill="both", expand=True)

        self.taskbar = TaskBar(self.root_container, self)
        self.taskbar.place(relx=0, rely=1.0, relwidth=1, anchor='sw')
        self.taskbar.lower()

        self.frames = {}


        login_frame = LoginPage(self.frames_container, self)
        self.frames["LoginPage"] = login_frame
        login_frame.place(relwidth=1, relheight=1)

        home_frame = HomePage(self.frames_container, self)
        self.frames["HomePage"] = home_frame
        home_frame.place(relwidth=1, relheight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        if page_name == "GpaPage" or page_name == "HomePage":
            self.taskbar.lift() 
        else:
            self.taskbar.lower()

        if page_name not in self.frames:
            if page_name == "GpaPage":
                self.frames[page_name] = GpaPage(self.frames_container, self)
            elif page_name == "SimpleReminder":
                self.frames[page_name] = SimpleReminder(self.frames_container, self)
            elif page_name == "HomeworkPlanner":
                self.frames[page_name] = HomeworkPlanner(self.frames_container, self)
            self.frames[page_name].place(relwidth=1, relheight=1)

        self.frames[page_name].tkraise()

    def show_main_menu(self):
        self.show_frame("HomePage")

    def on_closing(self):
        plt.close('all')
        self.destroy()


if __name__ == "__main__":
    app = StudentAssistantApp()
    app.mainloop()
