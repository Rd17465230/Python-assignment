from tkinter import *
from tkinter import messagebox
from resize import Resize
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

#78910456489
class GpaPage(Frame, Resize):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg="#f0f4f8")
        Resize.__init__(self)
        self.controller = controller
        self.semesters = []

        self.title_label = Label(self, text="GPA Calculator", bg="#f0f4f8", fg="#2c3e50")
        self.title_label.pack()

        self.button_frame = Frame(self, bg="#f0f4f8")
        self.button_frame.pack()
        
        self.add_semester_btn = Button(self.button_frame, text="Add Semester", command=self.add_semester)
        self.add_semester_btn.pack(side="left")
        self.calculate_cgpa_btn = Button(self.button_frame, text="Calculate CGPA", command=self.calculate_all)
        self.calculate_cgpa_btn.pack(side="left")
        self.back_menu_btn = Button(self.button_frame, text="Back to Menu", command=self.controller.show_main_menu)
        self.back_menu_btn.pack(side="left")

        self.main_frame = Frame(self, bg="#f0f4f8")
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = Canvas(self.main_frame, bg="#ffffff", highlightthickness=1, highlightbackground="#dcdcdc")
        self.scrollbar = Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="#ffffff")

        def update_scrollregion(event=None):
            self.update_idletasks()
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)

        self.scrollable_frame.bind("<Configure>", update_scrollregion)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            bbox = self.canvas.bbox("all")
            if bbox:
                _, _, _, content_bottom = bbox
                canvas_height = self.canvas.winfo_height()

                if content_bottom > canvas_height:
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", on_mousewheel)

        self.summary_label = Label(self, text="Overall CGPA: N/A", bg="#f0f4f8", fg="#2c3e50")
        self.summary_label.pack()

        self.add_semester()

    def update_layout(self):
        title_font_size = max(12, int(self.base_font_size * 1.8 * self.scaling_factor))
        self.title_label.config(font=("Helvetica", title_font_size, "bold"))
        self.title_label.pack_configure(pady=int(15 * self.scaling_factor))

        button_font_size = max(10, int(self.base_font_size * self.scaling_factor))
        button_style = {
            "font": ("Helvetica", button_font_size),
            "bg": "#3498db",
            "fg": "white",
            "padx": int(10 * self.scaling_factor),
            "pady": int(5 * self.scaling_factor),
            "relief": "flat"
        }
        self.button_frame.pack_configure(pady=int(10 * self.scaling_factor))
        self.add_semester_btn.config(**button_style)
        self.calculate_cgpa_btn.config(**button_style)
        self.back_menu_btn.config(**button_style)
        self.add_semester_btn.pack_configure(padx=int(5 * self.scaling_factor))
        self.calculate_cgpa_btn.pack_configure(padx=int(5 * self.scaling_factor))
        self.back_menu_btn.pack_configure(padx=int(5 * self.scaling_factor))

        self.main_frame.pack_configure(padx=int(10 * self.scaling_factor), pady=int(10 * self.scaling_factor))

        summary_font_size = max(10, int(self.base_font_size * 1.2 * self.scaling_factor))
        self.summary_label.config(font=("Helvetica", summary_font_size, "italic"))
        self.summary_label.pack_configure(pady=int(10 * self.scaling_factor))

        for sem in self.semesters:
            self.update_semester_layout(sem)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_semester_layout(self, sem):
        sem_frame = sem["frame"]
        sem_index = self.semesters.index(sem) + 1
        sem["index"] = sem_index
        font_size = int(self.base_font_size * self.scaling_factor)
        sem_font_size = int(self.base_font_size * 1.2 * self.scaling_factor)
        padx = int(5 * self.scaling_factor)
        pady = int(2 * self.scaling_factor)

        sem_frame.config(font=("Helvetica", sem_font_size, "bold"), text=f"Semester {sem_index}")
        sem_frame.pack_configure(pady=int(10 * self.scaling_factor), 
                                 padx=int(10 * self.scaling_factor), fill="x", expand=True, anchor="center")

        total_minsize = int(self.winfo_width() * 0.8 / 7)
        for i in range(7):
            sem_frame.grid_columnconfigure(i, minsize=max(100, total_minsize))

        for widget in sem_frame.grid_slaves(row=0):
            widget.config(font=("Helvetica", font_size, "bold"))

        for widget in sem_frame.grid_slaves(row=0, column=5):
            widget.config(font=("Helvetica", font_size), padx=padx, pady=pady)

        sem["gpa_label"].config(font=("Helvetica", font_size))
        sem["cgpa_label"].config(font=("Helvetica", font_size))

        for course in sem["courses"]:
            course["course_name"].config(font=("Helvetica", font_size))
            course["credit"].config(font=("Helvetica", font_size))
            course["widgets"][1].config(font=("Helvetica", font_size))  
            course["widgets"][-1].config(font=("Helvetica", font_size))  

    @staticmethod
    def grade_to_point(grade):
        mapping = {
            "A+": 4.0, "A": 4.0, "A-": 3.67,
            "B+": 3.33, "B": 3.0, "B-": 2.67,
            "C+": 2.33, "C": 2.0, "C-": 1.67,
            "D+": 1.33, "D": 1.0, "D-": 0.67,
            "F": 0.0
        }
        return mapping.get(grade, 0.0)

    @staticmethod
    def calculate_gpa(courses):
        total_points = 0
        total_credits = 0
        for c in courses:
            point = GpaPage.grade_to_point(c["grade"])
            credit = c["credit"]
            total_points += point * credit
            total_credits += credit
        return total_points / total_credits if total_credits else 0

    @staticmethod
    def calculate_cgpa(semesters):
        total_weighted = 0
        total_credits = 0
        for sem in semesters:
            total_weighted += sem["sem_gpa"] * sem["sem_credits"]
            total_credits += sem["sem_credits"]
        return total_weighted / total_credits if total_credits else 0

    def add_course(self, sem):
        course_numbers = [
            int(course["course_name"].get().replace("Course ", ""))
            for course in sem["courses"]
            if course["course_name"].get().startswith("Course ")
        ]
        next_course_num = max(course_numbers, default=0) + 1
        row = len(sem["courses"]) + 1
        frame = sem["frame"]

        course_entry = Entry(frame, width=20, font=("Helvetica", int(self.base_font_size * self.scaling_factor)),
                              relief="flat", bg="#ecf0f1", fg="#2c3e50")
        course_entry.insert(0, f"Course {next_course_num}")
        course_entry.grid(row=row, column=0, padx=int(5 * self.scaling_factor), pady=int(2 * self.scaling_factor))
        
        credit_entry = Entry(frame, width=5, font=("Helvetica", int(self.base_font_size * self.scaling_factor)), 
                             relief="flat", bg="#ecf0f1", fg="#2c3e50")
        credit_entry.grid(row=row, column=1, padx=int(5 * self.scaling_factor), pady=int(2 * self.scaling_factor))

        grade_var = StringVar(value="A")
        grade_menu = OptionMenu(frame, grade_var, "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F")
        grade_menu.config(font=("Helvetica", int(self.base_font_size * self.scaling_factor)), bg="#ecf0f1", fg="#2c3e50", 
                          relief="flat")
        grade_menu.grid(row=row, column=2, padx=int(5 * self.scaling_factor), pady=int(2 * self.scaling_factor))

        course = {
            "course_name": course_entry,
            "grade": grade_var,
            "credit": credit_entry,
            "widgets": [course_entry, grade_menu, credit_entry],
            "row": row
        }

        def remove():
            if len(sem["courses"]) <= 1:
                messagebox.showwarning("Warning", "Each semester need at least 1 course.")
                return
            
            for w in course["widgets"]:
                w.destroy()
            if course in sem["courses"]:
                sem["courses"].remove(course)
            self._regrid_courses(sem)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        remove_btn = Button(frame, text="Remove", command=remove, font=("Helvetica", int(self.base_font_size * self.scaling_factor)),
                             bg="#e74c3c", fg="white", relief="flat")
        remove_btn.grid(row=row, column=3, padx=int(5 * self.scaling_factor), pady=int(2 * self.scaling_factor))
        course["widgets"].append(remove_btn)

        sem["courses"].append(course)

    def add_semester(self):
        sem_index = len(self.semesters) + 1
        sem_frame = LabelFrame(self.scrollable_frame, text=f"Semester {sem_index}", 
                               font=("Helvetica", int(self.base_font_size * 1.2 * self.scaling_factor), "bold"), 
                               padx=int(10 * self.scaling_factor), pady=int(10 * self.scaling_factor), 
                               bg="#ffffff", fg="#2c3e50", relief="flat", bd=1)
        sem_frame.pack_configure(pady=int(10 * self.scaling_factor), padx=int(10 * self.scaling_factor))
        for i in range(7):
            sem_frame.grid_columnconfigure(i, minsize=int(80 * self.scaling_factor))

        Label(sem_frame, text="Course Name", font=("Helvetica", int(self.base_font_size * self.scaling_factor), "bold")
              , bg="#ffffff").grid(row=0, column=0, padx=int(5 * self.scaling_factor))
        Label(sem_frame, text="Credits", font=("Helvetica", int(self.base_font_size * self.scaling_factor), "bold")
              , bg="#ffffff").grid(row=0, column=1, padx=int(5 * self.scaling_factor))
        Label(sem_frame, text="Grade", font=("Helvetica", int(self.base_font_size * self.scaling_factor), "bold")
              , bg="#ffffff").grid(row=0, column=2, padx=int(5 * self.scaling_factor))

        add_btn = Button(sem_frame, text="Add Course", command=lambda: self.add_course(sem), 
                         font=("Helvetica", int(self.base_font_size * self.scaling_factor)), 
                         bg="#3498db", fg="white", relief="flat")
        add_btn.grid(row=0, column=3, pady=(0, int(5 * self.scaling_factor)))

        remove_btn = Button(sem_frame, text="Remove Semester", command=lambda: self.remove_semester(sem), font="Helvetica", bg="#e74c3c", fg="white", relief="flat")
        remove_btn.grid(row=0, column=4, pady=(0, int(5 * self.scaling_factor)))

        gpa_label = Label(sem_frame, text="GPA: N/A", 
                          font=("Helvetica", int(self.base_font_size * self.scaling_factor)), 
                          bg="#ffffff", fg="#2c3e50")
        gpa_label.grid(row=0, column=5, padx=int(10 * self.scaling_factor))

        cgpa_label = Label(sem_frame, text="CGPA: N/A", 
                           font=("Helvetica", int(self.base_font_size * self.scaling_factor)),
                             bg="#ffffff", fg="#2c3e50")
        cgpa_label.grid(row=1, column=5, padx=int(10 * self.scaling_factor))

        sem = {
            "index": sem_index,
            "frame": sem_frame,
            "courses": [],
            "sem_credits": 0,
            "sem_gpa": 0,
            "gpa_label": gpa_label,
            "cgpa_label": cgpa_label
        }
        
        self.semesters.append(sem)
        self.add_course(sem)
        self.update_semester_layout(sem)

    def remove_semester(self, sem):
        try:
            if len(self.semesters) <= 1:
                messagebox.showwarning("Warning", "Cannot remove the last semester.")
                return

            if sem in self.semesters:
                sem["frame"].destroy()
                self.semesters.remove(sem)

            for i, remaining_sem in enumerate(self.semesters, 1):
                remaining_sem["frame"].config(text=f"Semester {i}")

            self.update_layout()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.yview_moveto(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove semester: {str(e)}")

    def _regrid_courses(self, sem):
        frame = sem["frame"]
        font_size = int(self.base_font_size * self.scaling_factor)
        padx = int(5 * self.scaling_factor)
        pady = int(2 * self.scaling_factor)

        for course in sem["courses"]:
            for widget in course["widgets"]:
                widget.grid_forget()

        Label(frame, text="Course Name", font=("Helvetica", font_size, "bold"), bg="#ffffff").grid(row=0, column=0, padx=padx)
        Label(frame, text="Credits", font=("Helvetica", font_size, "bold"), bg="#ffffff").grid(row=0, column=1, padx=padx)
        Label(frame, text="Grade", font=("Helvetica", font_size, "bold"), bg="#ffffff").grid(row=0, column=2, padx=padx)

        for i, course in enumerate(sem["courses"], 1):
            course["row"] = i
            course["course_name"].grid(row=i, column=0, padx=padx, pady=pady)
            course["credit"].grid(row=i, column=1, padx=padx, pady=pady)
            course["widgets"][1].grid(row=i, column=2, padx=padx, pady=pady)
            course["widgets"][-1].grid(row=i, column=4, padx=padx, pady=pady)

    def process_courses(self, sem):
        processed = []
        for course in sem["courses"]:
            try:
                name = course["course_name"].get().strip()
                credit_str = course["credit"].get().strip()
                if not credit_str:
                    messagebox.showwarning("Input Error", f"Credit field empty in Sem {sem["index"]} {name or 'a course'}")
                    return None
                credit = float(credit_str)
                if credit <= 0:
                    messagebox.showwarning("Input Error", f"Credits must be positive in Sem {sem["index"]} {name or 'a course'}")
                    return None
                grade = course["grade"].get()
                processed.append({
                    "name": name,
                    "credit": credit,
                    "grade": grade
                })
            except ValueError:
                messagebox.showwarning("Input Error", f"Invalid credit value in Sem {sem["index"]} {name or 'a course'}")
                return None
        return processed

    def calculate_all(self):
        overall_cgpa = 0
        for i, sem in enumerate(self.semesters):
            subjects = self.process_courses(sem)
            if subjects is None:
                return
            if not subjects:
                sem["gpa_label"].config(text="GPA: N/A")
                sem["cgpa_label"].config(text="CGPA: N/A")
                continue
            gpa = GpaPage.calculate_gpa(subjects)
            total_credits = sum(s["credit"] for s in subjects)
            
            sem["sem_gpa"] = gpa
            sem["sem_credits"] = total_credits
            sem["gpa_label"].config(text=f"GPA: {gpa:.4f}")
            
            cgpa = GpaPage.calculate_cgpa(self.semesters[:i+1])
            sem["cgpa_label"].config(text=f"CGPA: {cgpa:.4f}")
            overall_cgpa = cgpa

        self.summary_label.config(text=f"Overall CGPA: {overall_cgpa:.4f}" if overall_cgpa else "Overall CGPA: N/A")
        self.show_gpa_chart()

    def show_gpa_chart(self):
        gpa_list = []
        sem_labels = []

        for i, sem in enumerate(self.semesters):
            gpa_list.append(sem["sem_gpa"])
            sem_labels.append(f"Sem {i + 1}")

        plt.figure(figsize=(7, 5))
        plt.plot(sem_labels, gpa_list, marker='o', linestyle='-', linewidth=2)
        plt.ylim(0, 4.0)
        plt.title("GPA Progression by Semester")
        plt.xlabel("Semester")
        plt.ylabel("GPA")
        plt.tight_layout()

        mng = plt.get_current_fig_manager()
        screen_width = mng.window.winfo_screenwidth()
        x_pos = screen_width - 700 - 50   
        y_pos = 100  

        mng.window.wm_geometry(f"+{x_pos}+{y_pos}")

        plt.show()

