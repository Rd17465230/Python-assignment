from tkinter import *
from tkinter import messagebox
from resize import Resize
from datetime import datetime
from tkcalendar import DateEntry
import os

DATA_FILE = "homework_data.txt"

class HomeworkPlanner(Frame, Resize):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg="#f0f4f8")
        Resize.__init__(self)
        self.controller = controller

        # ---------- data ----------
        self.tasks = []   # each task: {"subject": str, "deadline": str, "status": str, "details": str}
        self.current_page = 0
        self.page_size = 4

        # ---------- title ----------
        self.today_date = datetime.today().strftime("%Y-%m-%d")

        self.title_label = Label(self, text=f"Homework Planner\t\t\tToday: {self.today_date}", bg="#f0f4f8", fg="#2c3e50")
        self.title_label.pack(side="top",pady=10)

        # ---------- input area ----------
        self.input_frame = Frame(self, bg="#f0f4f8")
        self.input_frame.pack(padx=10, pady=5, fill="x")

        # Configure columns to handle content correctly
        # Column 0: Filter menu (no weight, takes its size)
        # Column 1: Labels (e.g., Subject, Status) (no weight, takes its size)
        # Column 2: Entry widgets (e.g., Subject entry, Status menu) (weight=1, expands)
        # Column 3: Labels (e.g., Deadline, Details) (no weight, takes its size)
        # Column 4: Entry widgets (e.g., Deadline entry, Details entry) (weight=1, expands)
        # Column 5: Add button (no weight)
        self.input_frame.grid_columnconfigure(0, weight=0)
        self.input_frame.grid_columnconfigure(1, weight=0)
        self.input_frame.grid_columnconfigure(2, weight=1)
        self.input_frame.grid_columnconfigure(3, weight=0)
        self.input_frame.grid_columnconfigure(4, weight=1)
        self.input_frame.grid_columnconfigure(5, weight=0)

        

        # Row 0: Subject and Deadline
        self.lbl_subject = Label(self.input_frame, text="Subject:", bg="#f0f4f8", anchor="e")
        self.lbl_subject.grid(row=0, column=1, padx=5, pady=2, sticky="e")
        self.subject_entry = Entry(self.input_frame)
        self.subject_entry.grid(row=0, column=2, padx=5, pady=2, sticky="we")

        self.lbl_deadline = Label(self.input_frame, text="Deadline:", bg="#f0f4f8", anchor="e")
        self.lbl_deadline.grid(row=0, column=3, padx=5, pady=2, sticky="e")
        self.deadline_entry = DateEntry(
            self.input_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern="yyyy-mm-dd",
            selectmode="day"  

        )
        self.deadline_entry.grid(row=0, column=4, padx=5, pady=2, sticky="we")
        self.deadline_entry.focus_set()

        # Add button
        self.add_btn = Button(self.input_frame, text="Add Homework", command=self.add_task, bg="#3498db", fg="white")
        self.add_btn.grid(row=0, column=5, rowspan=2, padx=8, pady=2, sticky="ns")

        # Row 1: Filter, Status, and Details
        self.filter_var = StringVar(value="All")
        self.filter_menu = OptionMenu(
            self.input_frame,
            self.filter_var,
            "All",
            "About to Expire",
            "Not Started",
            "In Progress",
            "Completed",
            command=lambda _: self.apply_filter()
        )
        self.filter_menu.config(width=12)
        self.filter_menu.grid(row=1, column=0, padx=8, pady=2, sticky="w")

        self.lbl_status = Label(self.input_frame, text="Status:", bg="#f0f4f8", anchor="e")
        self.lbl_status.grid(row=1, column=1, padx=0, pady=2, sticky="e")
        self.status_var = StringVar(value="Not Started")
        self.status_menu = OptionMenu(self.input_frame, self.status_var, "Not Started", "In Progress", "Completed")
        self.status_menu.config(width=12)
        self.status_menu.grid(row=1, column=2, padx=5, pady=2, sticky="we")  

        self.lbl_details = Label(self.input_frame, text="Details:", bg="#f0f4f8", anchor="e")
        self.lbl_details.grid(row=1, column=3, padx=5, pady=2, sticky="e")
        self.details_entry = Entry(self.input_frame)
        self.details_entry.grid(row=1, column=4, padx=5, pady=2, sticky="we")

        # ---------- task list container ----------
        self.task_frame = Frame(self, bg="#f0f4f8")
        self.task_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # ---------- pagination controls ----------
        self.pagination_frame = Frame(self, bg="#f0f4f8")
        self.pagination_frame.pack(pady=5)

        self.prev_btn = Button(self.pagination_frame, text="Previous", command=self.prev_page, bg="#3498db", fg="white")
        self.prev_btn.pack(side="left", padx=5)

        self.page_status = Label(self.pagination_frame, text="", bg="#f0f4f8", fg="#2c3e50")
        self.page_status.pack(side="left", padx=10)

        self.next_btn = Button(self.pagination_frame, text="Next", command=self.next_page, bg="#3498db", fg="white")
        self.next_btn.pack(side="left", padx=5)

        # ---------- statistics ----------
        self.stats_label = Label(self, text="", bg="#f0f4f8", fg="#2c3e50")
        self.stats_label.pack(pady=5)

        # ---------- back button ----------
        self.back_menu_btn = Button(self, text="Back to Menu", command=self.controller.show_main_menu, bg="#95a5a6", fg="white")
        self.back_menu_btn.pack(pady=10)

        self.subject_entry.focus_set()

        # ---------- load saved tasks ----------
        self.load_from_file()
        self.apply_filter()

    # ========== File Handling ==========
    def save_to_file(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            for t in self.tasks:
                line = f"{t['subject']}|{t['deadline']}|{t['status']}|{t['details']}\n"
                f.write(line)

    def load_from_file(self):
        self.tasks.clear()
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 4:
                        subject, deadline, status, details = parts
                        self.tasks.append({"subject": subject, "deadline": deadline, "status": status, "details": details})

    # ========== Core Actions ==========
    def add_task(self):
        subject = self.subject_entry.get().strip()
        deadline = self.deadline_entry.get().strip()
        status = self.status_var.get()
        details = self.details_entry.get().strip()

        if not subject or not deadline:
            messagebox.showwarning("Input Error", "Please enter both subject and deadline.")
            return
        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            if deadline_date < datetime.now().date():
                messagebox.showwarning("Input Error", "Deadline cannot be earlier than today.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Deadline must be in format YYYY-MM-DD.")
            return
        
        subject = self.subject_entry.get().strip().capitalize()

        self.tasks.append({"subject": subject, "deadline": deadline, "status": status, "details": details})

        self.subject_entry.delete(0, END)
        self.deadline_entry.delete(0, END)
        self.details_entry.delete(0, END)
        self.status_var.set("Not Started")
        self.subject_entry.focus_set()

        self.save_to_file()
        self.apply_filter()

    def update_status(self, task, new_status):
        task["status"] = new_status
        self.save_to_file()
        self.apply_filter()

    def delete_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)

        messagebox.showinfo("Delete task info", "Task deleted successfully.")

        self.save_to_file()
        self.apply_filter()

    # ========== Pagination ==========
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.apply_filter()
        else:
            messagebox.showinfo("Info", "No previous page available.")

    def next_page(self):
        max_page = (len(self.filtered_tasks) - 1) // self.page_size
        if self.current_page < max_page:
            self.current_page += 1
            self.apply_filter()
        else:
            messagebox.showinfo("Info", "No next page available.")

    # ========== Filtering ==========
    def apply_filter(self):
        """Filter tasks based on selected option and re-render."""
        filter_choice = self.filter_var.get()
        now = datetime.now().date()

        def about_to_expire(task):
            try:
                deadline_date = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
                return (deadline_date - now).days <= 3 and task["status"] != "Completed"
            except Exception:
                return False

        def _key(t):
            return (t["deadline"], t["subject"].lower())

        self.filtered_tasks = [t for t in sorted(self.tasks, key=_key) if (
            filter_choice == "All" or
            (filter_choice == "About to Expire" and about_to_expire(t)) or
            (filter_choice == "Not Started" and t["status"] == "Not Started") or
            (filter_choice == "In Progress" and t["status"] == "In Progress") or
            (filter_choice == "Completed" and t["status"] == "Completed")
        )]

        # delete old content
        for child in self.task_frame.winfo_children():
            child.destroy()

        # paging slices
        start = self.current_page * self.page_size
        end = start + self.page_size
        page_tasks = self.filtered_tasks[start:end]

        for i, task in enumerate(page_tasks, start=1):
            self._display_task(task, i + start)

        # update status display
        shown = len(page_tasks)
        total = len(self.filtered_tasks)
        max_page = (total - 1) // self.page_size + 1 if total > 0 else 1
        current_page_display = self.current_page + 1
        self.page_status.config(
            text=f"Page {current_page_display}/{max_page}   |   {shown} of {total}"
        )

        # update statistics message
        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["status"] == "Completed")
        about_to_expire_count = sum(1 for t in self.tasks if about_to_expire(t))
        self.stats_label.config(
            text=f"Total: {total_tasks}   |   Completed: {completed}   |   About to Expire: {about_to_expire_count}"
        )

    # ========== Rendering ==========
    def _display_task(self, task, index):
        frame = Frame(self.task_frame, bg="#ecf0f1", bd=1, relief="solid", padx=8, pady=6)
        frame.pack(fill="x", pady=4)

        top = Frame(frame, bg="#ecf0f1")
        top.pack(fill="x")

        Label(top, text=f"{index}. {task['subject']}", bg="#ecf0f1", anchor="w").pack(side="left", fill="x", expand=True)

        # if expired, display red color.
        try:
            deadline_date = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
            if deadline_date < datetime.now().date() and task["status"] != "Completed":
                deadline_color = "red"
            elif task["status"] == "Completed":
                deadline_color = "green"
            else:
                deadline_color = "black"
        except:
            deadline_color = "black"

        Label(top, text=f"Deadline: {task['deadline']}", bg="#ecf0f1", fg=deadline_color, anchor="e").pack(side="right")

        Label(frame, text=f"Status: {task['status']}", bg="#ecf0f1", anchor="w").pack(fill="x")
        if task["details"]:
            Label(frame, text=f"Details: {task['details']}", bg="#ecf0f1", anchor="w", wraplength=700, justify="left").pack(fill="x")

        btns = Frame(frame, bg="#ecf0f1")
        btns.pack(fill="x", pady=(4, 0))

        Button(btns, text="Edit", bg="#2980b9", fg="white", command=lambda: self.edit_task(task)).pack(side="left", padx=4)
        Button(btns, text="Mark In Progress", bg="#f39c12", fg="white", command=lambda: self.update_status(task, "In Progress")).pack(side="left", padx=4)
        Button(btns, text="Mark Completed", bg="#27ae60", fg="white", command=lambda: self.update_status(task, "Completed")).pack(side="left", padx=4)
        Button(btns, text="Delete", bg="#e74c3c", fg="white", command=lambda: self.delete_task(task)).pack(side="left", padx=4)

    def edit_task(self, task):
        self.edit_window = Toplevel(self)
        self.edit_window.title("Edit Homework")
        self.edit_window.geometry("400x250")
        self.edit_window.configure(bg="#f0f4f8")

        self.edit_window.transient(self)   # stay above parent
        self.edit_window.grab_set()        # block main window

        messagebox.showinfo("Edit Mode", "You are now editing a homework task.\n"
                                "Please finish editing or close this window before continuing.")

        Label(self.edit_window, text="Subject:", bg="#f0f4f8").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        subject_entry = Entry(self.edit_window, width=25)
        subject_entry.grid(row=0, column=1, padx=10, pady=5)
        subject_entry.insert(0, task["subject"])

        Label(self.edit_window, text="Deadline (YYYY-MM-DD):", bg="#f0f4f8").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        deadline_entry = DateEntry(self.edit_window, width=25, date_pattern="yyyy-mm-dd")
        deadline_entry.grid(row=1, column=1, padx=10, pady=5)
        deadline_entry.set_date(datetime.strptime(task["deadline"], "%Y-%m-%d"))

        Label(self.edit_window, text="Status:", bg="#f0f4f8").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        status_var = StringVar(value=task["status"])
        status_menu = OptionMenu(self.edit_window, status_var, "Not Started", "In Progress", "Completed")
        status_menu.config(width=12)
        status_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        Label(self.edit_window, text="Details:", bg="#f0f4f8").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        details_entry = Entry(self.edit_window, width=25)
        details_entry.grid(row=3, column=1, padx=10, pady=5)
        details_entry.insert(0, task["details"])

        def save_changes():
            try:
                deadline_date = datetime.strptime(deadline_entry.get().strip(), "%Y-%m-%d").date()
                if deadline_date < datetime.now().date():
                    messagebox.showwarning("Input Error", "Deadline cannot be earlier than today.")
                    return
            except ValueError:
                messagebox.showwarning("Input Error", "Deadline must be YYYY-MM-DD.")
                return

            task["subject"] = subject_entry.get().strip().capitalize()
            task["deadline"] = deadline_entry.get().strip()
            task["status"] = status_var.get()
            task["details"] = details_entry.get().strip()

            self.save_to_file()
            self.apply_filter()
            self.edit_window.destroy()

        Button(self.edit_window, text="Save", command=save_changes, bg="#27ae60", fg="white").grid(row=4, column=0, columnspan=2, pady=15)

    # ========== Resize abstract method ==========
    def update_layout(self):
        title_fs = max(12, int(self.base_font_size * 1.6 * self.scaling_factor))
        label_fs = max(10, int(self.base_font_size * 1.0 * self.scaling_factor))
        entry_fs = max(10, int(self.base_font_size * 1.0 * self.scaling_factor))
        btn_fs = max(10, int(self.base_font_size * 1.0 * self.scaling_factor))

        self.title_label.config(font=("Helvetica", title_fs, "bold"))
        self.title_label.pack_configure(pady=int(10 * self.scaling_factor))

        for lbl in (self.lbl_subject, self.lbl_deadline, self.lbl_status, self.lbl_details):
            lbl.config(font=("Helvetica", label_fs))

        self.subject_entry.config(font=("Helvetica", entry_fs))
        self.deadline_entry.config(font=("Helvetica", entry_fs))
        self.details_entry.config(font=("Helvetica", entry_fs))
        self.status_menu.config(font=("Helvetica", entry_fs))
        self.status_menu["menu"].config(font=("Helvetica", entry_fs))

        self.add_btn.config(font=("Helvetica", btn_fs), padx=int(10 * self.scaling_factor), pady=int(5 * self.scaling_factor))
        self.back_menu_btn.config(font=("Helvetica", btn_fs), padx=int(10 * self.scaling_factor), pady=int(5 * self.scaling_factor))
