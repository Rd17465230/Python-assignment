from tkinter import *
from PIL import Image, ImageTk
import gpa.gpa_calculator

def open_gpa():
    main.withdraw()  
    gpa.gpa_calculator.main()  
    main.deiconify()  

main = Tk()
main.title("TAR UMT Student Assistant App")
main.geometry("800x450")

resized = Image.open(r"photo\background.jpg").resize((800, 450), Image.Resampling.LANCZOS)
bg_image = ImageTk.PhotoImage(resized)

bg_label = Label(main, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

title = Label(main, text="Welcome to TAR UMT Student Assistant", font=("Arial", 16, "bold"), bg="#ADD8E6")
title.place(relx=0.5, rely=0.2, anchor="center")

btn1 = Button(main, text="GPA Calculator", width=25, height=2, command= open_gpa)
btn1.place(relx=0.5, rely=0.4, anchor="center")

btn2 = Button(main, text="LLT", width=25, height=2)
btn2.place(relx=0.5, rely=0.5, anchor="center")

btn3 = Button(main, text="LKJ", width=25, height=2)
btn3.place(relx=0.5, rely=0.6, anchor="center")

main.mainloop()

