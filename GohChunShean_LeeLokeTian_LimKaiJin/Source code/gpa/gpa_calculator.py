from tkinter import *

semesters=[]

def grade_to_point(grade):
    mapping = {
        "A+": 4.0, "A": 4.0, "A-": 3.67,
        "B+": 3.33, "B": 3.0, "B-": 2.67,
        "C+": 2.33, "C": 2.0, "C-": 1.67,
        "D+": 1.33,"D": 1.0, "D-":0.67,
        "F": 0.0
    }
    return mapping.get(grade, 0.0)

def calculate_gpa(courses):
    total_points = 0
    total_credits = 0
    for c in courses:
        point = grade_to_point(c["grade"])
        credit = c["credit"]
        total_points += point * credit
        total_credits += credit
    return total_points / total_credits if total_credits else 0

def calculate_cgpa(semesters):
    total_weighted = 0
    total_credits = 0
    for sem in semesters:
        total_weighted += sem["sem_gpa"] * sem["sem_credits"]
        total_credits += sem["sem_credits"]
    return total_weighted / total_credits if total_credits else 0

def add_course(sem):
    row = len(sem["courses"]) + 1
    frame = sem["frame"]

    course_entry = Entry(frame)
    course_entry.insert(0, f"Course {row}")
    course_entry.grid(row=row, column=0, padx=5)
    
    credit_entry = Entry(frame, width=5)
    credit_entry.grid(row=row, column=1, padx=5)

    grade_var = StringVar(value="A")
    grade_menu = OptionMenu(frame, grade_var, "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F")
    grade_menu.grid(row=row, column=2, padx=5)

    course = {
        "course_name": course_entry,
        "grade": grade_var,
        "credit": credit_entry,
        "widgets": [course_entry, grade_menu, credit_entry], 
    }

    def remove():
        for w in course["widgets"]:
            w.destroy()
        remove_btn.destroy()
        sem["courses"].remove(course)

    remove_btn = Button(frame, text="Remove", command=remove)
    remove_btn.grid(row=row, column=4, padx=5)
    course["widgets"].append(remove_btn)

    sem["courses"].append(course)

def add_semester(main_frame):
    sem_index = len(semesters) + 1
    sem_frame = LabelFrame(main_frame, text=f"Semester {sem_index}", padx=10, pady=5)
    sem_frame.pack(pady=10, fill="x")
    for i in range(7):
        sem_frame.grid_columnconfigure(i, minsize=80)
    Label(sem_frame, text="Course Name (Optional)", padx=5).grid(row=0,column=0)
    Label(sem_frame, text="Credits", padx=5).grid(row=0,column=1)
    Label(sem_frame, text="Grade", padx=5).grid(row=0,column=2)

    add_btn = Button(sem_frame, text="Add Course", command=lambda: add_course(sem))
    add_btn.grid(row=0, column=5, pady=(0,5))

    gpa_label = Label(sem_frame, text="GPA: N/A", font=("Arial", 10))
    gpa_label.grid(row=0, column=6, padx=5)

    cgpa_label = Label(sem_frame, text="CGPA: N/A", font=("Arial", 10))
    cgpa_label.grid(row=1, column=6, padx=5)


    sem = {
        "frame": sem_frame,
        "courses": [],
        "sem_credits": 0,
        "gpa_label": gpa_label ,
        "cgpa_label": cgpa_label
    }
    
    semesters.append(sem)
    add_course(sem)

def process_courses(sem):
    processed = []
    for course in sem["courses"]:
        try:
            name = course["course_name"].get().strip()
            credit = float(course["credit"].get())
            grade = course["grade"].get()

            processed.append({
                "name": name,
                "credit": credit,
                "grade": grade
            })
        except Exception as e:
            print(f"Error processing course: {e}")
    return processed

def calculate_all():
    for i, sem in enumerate(semesters):
        subjects = process_courses(sem)
        if not subjects:
            continue
        gpa = calculate_gpa(subjects)
        total_credits = sum(s["credit"] for s in subjects)
        
        sem["sem_gpa"] = gpa
        sem["sem_credits"] = total_credits

        sem["gpa_label"].config(text=f"GPA: {gpa:.4f}")

        cgpa = calculate_cgpa(semesters[:i+1])
        sem["cgpa_label"].config(text=f"CGPA: {cgpa:.4f}")


def main():
    gpa = Toplevel()
    gpa.title("GPA Calculator")
    gpa.geometry("700x600")

    title = Label(gpa, text="TAR UMT GPA Calculator", font=("Arial", 16, "bold"))
    title.pack(pady=10)

    button_frame = Frame(gpa)
    button_frame.pack()

    Button(button_frame, text="Add Semester", command=add_semester).pack(side="left", padx=5)
    Button(button_frame, text="Calculate CGPA", command=calculate_all).pack(side="left", padx=5)

    scroll_canvas = Canvas(gpa)
    scroll_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(gpa, orient=VERTICAL, command=scroll_canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    scroll_canvas.configure(yscrollcommand=scrollbar.set)

    # Create an internal frame inside the canvas
    main_frame = Frame(scroll_canvas)
    canvas_window = scroll_canvas.create_window((0, 0), window=main_frame, anchor="nw")

    # Make canvas scrollable when content grows
    def on_frame_configure(event):
        scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

    main_frame.bind("<Configure>", on_frame_configure)

    # Enable mouse wheel scroll
    def _on_mousewheel(event):
        scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    add_semester(main_frame) 

    result_label = Label(gpa, text="", justify="left", font=("Arial", 12))
    result_label.pack(pady=10)

    gpa.protocol("WM_DELETE_WINDOW", lambda: gpa.destroy()) 