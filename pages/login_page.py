# pages/login_page.py
from tkinter import *
from tkinter import messagebox

class LoginPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f4f8")
        self.controller = controller

        form = Frame(self, bg="#ffffff", bd=2, relief="groove")
        form.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.35, relheight=0.4)

        Label(form, text="Login", font=("Helvetica", 20, "bold"), bg="#ffffff").pack(pady=20)

        Label(form, text="Id:", bg="#ffffff", anchor="w").pack(fill="x", padx=20)
        self.id_entry = Entry(form, font=("Helvetica", 12))
        self.id_entry.pack(fill="x", padx=20, pady=(0,10))

        Label(form, text="Password:", bg="#ffffff", anchor="w").pack(fill="x", padx=20)
        self.password_entry = Entry(form, show="*", font=("Helvetica", 12))
        self.password_entry.pack(fill="x", padx=20, pady=(0,20))

        Button(
            form, text="Login",
            bg="#3498db", fg="white", font=("Helvetica", 14, "bold"),
            relief="flat", cursor="hand2",
            command=self.attempt_login
        ).pack(pady=10, fill="x", padx=20)

    def attempt_login(self):
        id = self.id_entry.get().strip()
        password = self.password_entry.get().strip()

        if id == "2407308" and password == "12345678":
            messagebox.showinfo("Login Success", "Welcome!")
            self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
