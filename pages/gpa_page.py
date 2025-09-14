# pages/gpa_page.py
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json, os

SAVE_FILE = os.path.join(os.path.dirname(__file__), "gpa_data.json")

class GpaPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f4f8")
        self.controller = controller
        self.semesters = []

        self.icon_remove = ImageTk.PhotoImage(
            Image.open("photo/remove.png").resize((20, 20))
        )

        self.ori_img = Image.open(r"photo/background.jpg")
        self.bg_label = Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._resize_bg)

        self.title_label = Label(
            self, text="GPA Calculator",
            bg="#f0f4f8", fg="#2c3e50",
            font=("Helvetica", 28, "bold")
        )
        self.title_label.pack(pady=20)

        content_frame = Frame(self, bg="#f0f4f8")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0,45))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=2) 
        content_frame.grid_columnconfigure(1, weight=3)  
        content_frame.grid_columnconfigure(2, weight=5)  

        btn_fonts = ("Helvetica", 14, "bold")

        icon_size = (24, 24)
        self.icon_add  = ImageTk.PhotoImage(Image.open("photo/add.png").resize(icon_size))
        self.icon_calc = ImageTk.PhotoImage(Image.open("photo/calculator.png").resize(icon_size))
        self.icon_back = ImageTk.PhotoImage(Image.open("photo/back.png").resize(icon_size))

        self.control_frame = Frame(content_frame, bg="#e8ecf0")
        self.control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.control_frame.grid_propagate(False)

        Button(
            self.control_frame,
            text="  Add Semester",       
            image=self.icon_add,
            compound="left",             
            bg="#1abc9c", fg="white",
            relief="flat",
            font=btn_fonts,
            command=self.add_semester
        ).pack(fill="both", expand=True, pady=8)

        Button(
            self.control_frame,
            text="  Calculate",
            image=self.icon_calc,
            compound="left",
            bg="#e67e22", fg="white",
            relief="flat",
            font=btn_fonts,
            command=self.calculate_all
        ).pack(fill="both", expand=True, pady=8)

        Button(
            self.control_frame,
            text="  Back to Menu",
            image=self.icon_back,
            compound="left",
            bg="#e74c3c", fg="white",
            relief="flat",
            font=btn_fonts,
            command=self.controller.show_main_menu
        ).pack(fill="both", expand=True, pady=8)

        self.scroll_frame_container = Frame(content_frame, bg="#f0f4f8")
        self.scroll_frame_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.canvas = Canvas(self.scroll_frame_container, bg="#ffffff",
                             highlightthickness=1, highlightbackground="#dcdcdc")
        self.scrollbar = Scrollbar(self.scroll_frame_container, orient="vertical",
                                   command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="#ffffff")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.plt_frame = Frame(content_frame, bg="#ffffff")
        self.plt_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self.fig, self.ax = plt.subplots(figsize=(6,4))
 
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.plt_frame)
        self.canvas_widget = self.canvas_plot.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        self.ax.text(0.5, 0.5, "No data to plot", ha="center", va="center", 
                     fontsize=16, color="#555555")
        self.ax.axis("off")
        self.fig.tight_layout()
        self.canvas_plot.draw()

        self.load_data()

    def _resize_bg(self, event):
        if event.width > 0 and event.height > 0:
            resized = self.ori_img.resize((event.width, event.height),
                                          Image.Resampling.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.bg_img)

    def _on_mousewheel(self, event):
        bbox = self.canvas.bbox("all")
        if bbox:
            _, _, _, bottom = bbox
            if bottom > self.canvas.winfo_height():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

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
        total_points = total_credits = 0
        for c in courses:
            total_points += GpaPage.grade_to_point(c["grade"]) * c["credit"]
            total_credits += c["credit"]
        return total_points / total_credits if total_credits else 0

    @staticmethod
    def calculate_cgpa(semesters):
        total_weighted = total_credits = 0
        for sem in semesters:
            total_weighted += sem["sem_gpa"] * sem["sem_credits"]
            total_credits += sem["sem_credits"]
        return total_weighted / total_credits if total_credits else 0

    def _regrid_courses(self, sem):
        for course in sem["courses"]:
            for w in course["widgets"]:
                w.grid_forget()

        for row_index, course in enumerate(sem["courses"], start=1):
            widgets = course["widgets"]
            widgets[0].grid(row=row_index, column=0, sticky="we", padx=5, pady=3)
            widgets[1].grid(row=row_index, column=1, sticky="w",  padx=5, pady=3)
            widgets[2].grid(row=row_index, column=2, sticky="w",  padx=5, pady=3)
            widgets[3].grid(row=row_index, column=3, padx=5, pady=3)

    def add_course(self, sem):
        sem["course_naming"] += 1
        index = sem["course_naming"]

        row = len(sem["courses"]) + 1
        frame = sem["frame"]

        name_e = Entry(frame, width=15, bg="#ecf0f1", fg="#2c3e50",
                       font=("Helvetica", 12))
        name_e.insert(0, f"Course {index}")
        name_e.grid(row=row, column=0, padx=5, pady=3, sticky="we")

        credit_var = StringVar(value="3")   
        credit_menu = OptionMenu(frame, credit_var, *[str(i) for i in range(1, 7)])
        credit_menu.config(font=("Helvetica", 12))
        credit_menu.grid(row=row, column=1, padx=5, pady=3, sticky="w")

        grade_var = StringVar(value="A")
        grade_menu = OptionMenu(frame, grade_var,
                                "A+", "A", "A-", "B+", "B", "B-",
                                "C+", "C", "C-", "D+", "D", "D-", "F")
        grade_menu.config(font=("Helvetica", 12),width=1)
        grade_menu.grid(row=row, column=2, padx=5, pady=3,sticky="w")

        course = {
            "course_name": name_e,
            "grade": grade_var,
            "credit": credit_var,
            "widgets": [name_e, credit_menu, grade_menu], 
            "row": row 
        }

        def remove():
            if len(sem["courses"]) <= 1:
                messagebox.showwarning("Warning", "Each semester needs at least 1 course.")
                return
            
            if not messagebox.askyesno("Confirm",
                                    f"Are you sure you want to remove this course from Semester {sem['index']}?"):
                return

            for w in course["widgets"]:
                w.destroy()
            rm_btn.destroy()

            sem["courses"].remove(course)
            self._regrid_courses(sem)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        rm_btn = Button(frame, text="Remove", bg="#e74c3c", fg="white",
                        font=("Helvetica", 11), command=remove)

        rm_btn.grid(row=row, column=3, padx=5, pady=3) 
        course["widgets"].append(rm_btn) 

        sem["courses"].append(course)

        name_e.focus_set() 
        self.canvas.update_idletasks()
        y1 = name_e.winfo_y()
        h  = self.scrollable_frame.winfo_height()
        view_h = self.canvas.winfo_height()
        if h > view_h:
            frac = min(max(y1 / (h - view_h), 0), 1)
            self.canvas.yview_moveto(frac)


    def add_semester(self):
        sem_index = len(self.semesters) + 1
        outer = Frame(self.scrollable_frame, bg="#ffffff")
        outer.pack(anchor="w", fill="x", padx=5, pady=10)

        top_frame = Frame(outer, bg="#ffffff")
        top_frame.pack(fill="x", pady=(0, 5))
        
        sem_title = Label(top_frame, text=f"Semester {sem_index}",
                        bg="#ffffff", fg="#2c3e50", font=("Helvetica", 14, "bold"))
        sem_title.pack(side="left")
        
        remove_sem_btn = Button(
            top_frame,
            image=self.icon_remove,         
            bg="#ffffff",                   
            activebackground="#f5f5f5",     
            borderwidth=0,                  
            relief="flat",
            command=lambda: self.remove_semester(sem)
        )
        remove_sem_btn.pack(side="right", padx=(5, 0))

        sem_frame = LabelFrame(
            outer, text="Courses",
            bg="#ffffff", fg="#2c3e50",
            font=("Helvetica", 12, "bold"),
            bd=1, relief="solid", padx=12, pady=10
        )
        sem_frame.pack(fill="x")
        
        sem_frame.grid_columnconfigure(0, weight=5, uniform="col")
        sem_frame.grid_columnconfigure(1, weight=2, uniform="col")
        sem_frame.grid_columnconfigure(2, weight=2, uniform="col")
        sem_frame.grid_columnconfigure(3, weight=0)

        Label(sem_frame, text="Course Name", bg="#ffffff", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        Label(sem_frame, text="Credits", bg="#ffffff", font=("Helvetica", 12, "bold")).grid(row=0, column=1, padx=5, sticky="w")
        Label(sem_frame, text="Grade", bg="#ffffff", font=("Helvetica", 12, "bold")).grid(row=0, column=2, padx=5, sticky="w")
   
        Button(sem_frame, text="Add Course", bg="#3498db", fg="white", font=("Helvetica", 11),
               command=lambda: self.add_course(sem)).grid(row=0, column=3, padx=5, pady=5)
        
        bottom_frame = Frame(outer, bg="#ffffff")
        bottom_frame.pack(fill="x", pady=(5, 0))
        
        gpa_label = Label(bottom_frame, text="GPA: N/A",
                            bg="#ffffff", fg="#2c3e50", font=("Helvetica", 12, "italic"))
        gpa_label.pack(side="left", padx=(12, 5)) 
        
        cgpa_label = Label(bottom_frame, text="CGPA: N/A",
                            bg="#ffffff", fg="#2c3e50", font=("Helvetica", 12, "italic"))
        cgpa_label.pack(side="left", padx=(5, 10))
        
        sem = {
            "index": sem_index,
            "frame": sem_frame,
            "top_frame": top_frame,
            "title": sem_title,
            "border_frame": outer,
            "bottom_frame": bottom_frame,
            "courses": [],
            "sem_credits": 0,
            "sem_gpa": 0,
            "gpa_label": gpa_label,
            "cgpa_label": cgpa_label,
            "course_naming": 0
        }
        
        self.semesters.append(sem)
        self.add_course(sem)

        first_entry = sem["courses"][0]["course_name"]
        first_entry.focus_set()
        self.canvas.update_idletasks()
        y1 = sem["border_frame"].winfo_y()
        h  = self.scrollable_frame.winfo_height()
        view_h = self.canvas.winfo_height()
        if h > view_h:
            frac = min(max(y1 / (h - view_h), 0), 1)
            self.canvas.yview_moveto(frac)
                
    def remove_semester(self, sem_to_remove):
        try:
            if len(self.semesters) <= 1:
                messagebox.showwarning("Warning", "Cannot remove the last semester.")
                return

            if not messagebox.askyesno(
                "Confirm",
                f"Are you sure you want to remove Semester {sem_to_remove['index']}? All its courses will be lost."
            ):
                return

            if sem_to_remove in self.semesters:
                sem_to_remove["border_frame"].destroy() 
                self.semesters.remove(sem_to_remove)

                for i, current_sem in enumerate(self.semesters):
                    new_index = i + 1
                    current_sem["index"] = new_index
                    current_sem["title"].config(text=f"Semester {new_index}") 

                self.update_idletasks()

                self.canvas.configure(scrollregion=self.canvas.bbox("all"))

                self.canvas.yview_moveto(0)
        except Exception as e: 
            messagebox.showerror("Error", f"Failed to remove semester: {str(e)}")

    # ----------------- GPA Calculate -----------------  
    @staticmethod  
    def frange(start, stop, step):
        x = start
        while x <= stop:
            yield x
            x += step

    def process_courses(self, sem):
        processed = []
        for course in sem["courses"]:
            name = course["course_name"].get().strip()
            credit_str = course["credit"].get().strip()
            if not credit_str:
                messagebox.showwarning("Input Error",
                                       f"Credit field empty in Sem {sem['index']} {name or 'a course'}")
                return None
            try:
                credit = float(credit_str)
                if credit <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Input Error",
                                       f"Invalid credit value in Sem {sem['index']} {name or 'a course'}")
                return None
            grade = course["grade"].get()
            processed.append({"name": name, "credit": credit, "grade": grade})
        return processed

    def calculate_all(self):
        for i, sem in enumerate(self.semesters):
            subjects = self.process_courses(sem)
            if subjects is None:
                return
            if not subjects:
                sem["gpa_label"].config(text="GPA: N/A")
                sem["cgpa_label"].config(text="CGPA: N/A")
                continue
            gpa = GpaPage.calculate_gpa(subjects)
            credits = sum(s["credit"] for s in subjects)

            sem["sem_gpa"] = gpa
            sem["sem_credits"] = credits
            sem["gpa_label"].config(text=f"GPA: {gpa:.4f}")

            cgpa = GpaPage.calculate_cgpa(self.semesters[:i + 1])
            sem["cgpa_label"].config(text=f"CGPA: {cgpa:.4f}")
        self.show_gpa_chart()
        self.save_data()

    def show_gpa_chart(self):
        self.ax.clear()
        gpa_list = [sem["sem_gpa"] for sem in self.semesters if sem["sem_credits"] > 0]
        if not gpa_list:
            self.ax.text(0.5, 0.5, "No data to plot",
                        ha="center", va="center",
                        fontsize=16, color="#555555")
            self.ax.axis("off")
        else:
            sem_labels = [f"Sem {i+1}" for i, sem in enumerate(self.semesters)
                        if sem["sem_credits"] > 0]
            self.ax.plot(sem_labels, gpa_list, marker="o", linestyle="-", linewidth=2)

            max_gpa = max(gpa_list)
            upper = max(4.0, max_gpa) + 0.2
            upper = min(upper, 4.5)

            self.ax.set_ylim(0, upper)
            ticks = [round(x, 1) for x in GpaPage.frange(0, upper + 0.001, 0.2)]
            self.ax.set_yticks(ticks)

            self.ax.set_title("GPA Progression by Semester")
            self.ax.set_xlabel("Semester")
            self.ax.set_ylabel("GPA")
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.ax.axis("on")

        self.fig.tight_layout()
        self.canvas_plot.draw()

    def save_data(self):
        data = []
        for sem in self.semesters:
            courses = []
            for c in sem["courses"]:
                courses.append({
                    "name": c["course_name"].get(),
                    "credit": c["credit"].get(),
                    "grade": c["grade"].get()
                })
            data.append({"courses": courses})
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data: {e}")

    def load_data(self):
        if not os.path.exists(SAVE_FILE):
            self.add_semester()    
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
        except Exception as e:
            messagebox.showwarning("Load Error", f"Could not read saved data: {e}")
            self.add_semester()
            return

        if not isinstance(saved, list):
            self.add_semester()
            return

        for sem_data in saved:
            self.add_semester()        
            sem = self.semesters[-1]   
            for c in list(sem["courses"]):
                for w in c["widgets"]:
                    try:
                        w.destroy()
                    except AttributeError:
                        pass   
                sem["courses"].remove(c)

            for cdata in sem_data.get("courses", []):
                self.add_course(sem)
                course = sem["courses"][-1]
                course["course_name"].delete(0, END)
                course["course_name"].insert(0, cdata.get("name", ""))
                course["credit"].set(cdata.get("credit", "3"))
                course["grade"].set(cdata.get("grade", "A"))

        self.calculate_all()
