from tkinter import *
from PIL import Image, ImageTk
from resize import Resize

class MainMenu(Frame, Resize):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        Resize.__init__(self)
        self.controller = controller

        # Background image
        self.ori_img = Image.open(r"photo/background.jpg")
        self.bg_label = Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Title and buttons
        self.title = Label(self, text="Welcome to TAR UMT Student Assistant", bg="#ADD8E6")
        self.title.place(relx=0.5, rely=0.2, relwidth=0.5, relheight=0.1, anchor="center")

        self.button1 = Button(self, text="GPA Calculator", 
                             command=lambda: controller.show_frame("GpaPage"))
        self.button1.place(relx=0.5, rely=0.4, relwidth=0.3, relheight=0.08, anchor="center")

        self.button2 = Button(self, text="Simple Reminder", 
                             command=lambda: controller.show_frame("SimpleReminder"))
        self.button2.place(relx=0.5, rely=0.5, relwidth=0.3, relheight=0.08, anchor="center")

        self.button3 = Button(self, text="Homework planner",
                              command=lambda: controller.show_frame("HomeworkPlanner"))
        self.button3.place(relx=0.5, rely=0.6, relwidth=0.3, relheight=0.08, anchor="center")

        # Initial update
        self.after(1, self.update_layout)

    def update_layout(self):
        # Update background image
        width = self.winfo_width()
        height = self.winfo_height()
        if width > 0 and height > 0:
            resized_img = self.ori_img.resize((width, height), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_img)
            self.bg_label.configure(image=self.bg_image)
            self.bg_label.image = self.bg_image

        # Update fonts
        title_font_size = max(12, int(self.base_font_size * 1.4 * self.scaling_factor))
        button_font_size = max(10, int(self.base_font_size * self.scaling_factor))

        self.title.configure(font=("Arial", title_font_size, "bold"))
        self.button1.configure(font=("Arial", button_font_size))
        self.button2.configure(font=("Arial", button_font_size))
        self.button3.configure(font=("Arial", button_font_size))