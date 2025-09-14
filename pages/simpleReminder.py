import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time as dtime
import calendar
import os

DATA_FILE = "reminders.txt"
HISTORY_FILE = "history.txt"

# reminder classes
class NormalReminder:
    def __init__(self, dt: datetime, description: str, attribute: str):
        self.dt = dt
        self.description = description
        self.attribute = attribute
        self.id = f"N-{self.dt.timestamp()}-{abs(hash(description + attribute))}"

class RepeatReminder:
    def __init__(self, weekday: int, at_time: dtime, description: str, attribute: str = ""):
        self.weekday = weekday
        self.at_time = at_time
        self.description = description
        self.attribute = attribute
        self.id = f"R-{weekday}-{at_time.strftime('%H%M')}-{abs(hash(description + attribute))}"

# main frame
class SimpleReminder(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#6bf39d")
        self.controller = controller or self

        self.normal_reminders = []
        self.repeat_reminders = []
        self.history_reminders = []
        self.load_from_file()
        self.load_history()

        # layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title = tk.Label(self, text="Simple Reminder App", font=("Arial", 36, "bold"), bg="#6bf39d")
        title.grid(row=0, column=0, pady=0, sticky="n")

        content = tk.Frame(self, bg="#6bf39d")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)

        # left buttons
        left_frame = tk.Frame(content, bd=2, relief="ridge", bg="#6bf39d")
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        btn_style = {"font": ("Arial", 18, "bold"), "width": 20, "height": 3}

        tk.Button(left_frame, text="Add Reminder", bg="#3f3ce7", fg="white",
                  **btn_style, command=lambda: self.show_right("AddReminderPage")).grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        tk.Button(left_frame, text="Add Repeat Reminder", bg="#dce73c", fg="black",
                  **btn_style, command=lambda: self.show_right("AddRepeatPage")).grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        tk.Button(left_frame, text="View Reminders", bg="#3ce7d6", fg="black",
                  **btn_style, command=lambda: self.show_right("ViewReminderPage")).grid(row=2, column=0, sticky="nsew", padx=12, pady=12)
        tk.Button(left_frame, text="Back to Main Menu", bg="#de3ce7", fg="white",
                  **btn_style, command=lambda: getattr(self.controller, "show_main_menu", lambda: None)()).grid(row=3, column=0, sticky="nsew", padx=12, pady=12)

        # right container
        self.right_frame = tk.Frame(content, bd=2, relief="ridge", bg="#6bf39d")
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # pages
        self.right_pages = {}
        for Page in (AddReminderPage, AddRepeatPage, ViewReminderPage):
            frame = Page(self.right_frame, self)
            self.right_pages[Page.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_right("AddReminderPage")

        self.check_reminders()

    def show_right(self, name):
        frame = self.right_pages.get(name)
        if not frame:
            return
        if hasattr(frame, "show"):
            frame.show()
        frame.tkraise()

    # check reminders
    def check_reminders(self):
        now = datetime.now()
        due_normals = [r for r in self.normal_reminders if abs((r.dt - now).total_seconds()) < 6]
        for r in due_normals:
            self.show_popup(f"{r.attribute}: {r.description}")
            self.normal_reminders = [x for x in self.normal_reminders if x.id != r.id]
            self.add_to_history(f"[Normal] | {r.dt.strftime('%Y-%m-%d %H:%M')} | {r.attribute} | {r.description}")
            self.save_to_file()

        for r in self.repeat_reminders:
            if r.weekday == now.weekday():
                due_dt = datetime.combine(now.date(), r.at_time)
                if abs((due_dt - now).total_seconds()) < 6:
                    self.show_popup(f"{r.attribute}: {r.description}")

        self.after(5000, self.check_reminders)

    def show_popup(self, description):
        popup = tk.Toplevel(self)
        popup.title("Reminder")
        popup.geometry("420x160")
        tk.Label(popup, text=description, font=("Arial", 14, "bold"), wraplength=380, justify="center").pack(pady=15)
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=5)

    def save_to_file(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                for r in self.normal_reminders:
                    f.write(f"N|{r.dt.strftime('%Y-%m-%d %H:%M')}|{r.attribute}|{r.description}\n")
                for r in self.repeat_reminders:
                    f.write(f"R|{r.weekday}|{r.at_time.strftime('%H:%M')}|{r.attribute}|{r.description}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save reminders: {e}")

    def load_from_file(self):
        self.normal_reminders.clear()
        self.repeat_reminders.clear()
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if not parts:
                        continue
                    if parts[0] == "N" and len(parts) == 4:
                        dt = datetime.strptime(parts[1], "%Y-%m-%d %H:%M")
                        self.normal_reminders.append(NormalReminder(dt, parts[3], parts[2]))
                    elif parts[0] == "R" and len(parts) >= 4:
                        weekday = int(parts[1])
                        at_time = datetime.strptime(parts[2], "%H:%M").time()
                        if len(parts) == 5:
                            attr, desc = parts[3], parts[4]
                        else:
                            attr, desc = "", parts[3]
                        self.repeat_reminders.append(RepeatReminder(weekday, at_time, desc, attr))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reminders: {e}")

    def add_to_history(self, text):
        try:
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(text + "\n")
            self.load_history()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history: {e}")

    def load_history(self):
        self.history_reminders.clear()
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self.history_reminders = [line.strip() for line in f if line.strip()]

    def delete_history(self, text):
        self.history_reminders = [h for h in self.history_reminders if h != text]

        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                for h in self.history_reminders:
                    f.write(h + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update history file: {e}")
            
# add one-time reminder page
class AddReminderPage(tk.Frame):
    def __init__(self, parent, controller: SimpleReminder):
        super().__init__(parent, bg="#6bf39d")
        self.controller = controller

        self.selected_date = None
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        # rows 0..6
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)

        tk.Label(self, text="Add Reminder", font=("Arial", 36, "bold"), bg="#6bf39d").grid(row=0, column=0, pady=5, sticky="n")

        # nav
        nav_frame = tk.Frame(self, bg="#6bf39d")
        nav_frame.grid(row=1, column=0, sticky="ew")
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(1, weight=3)
        nav_frame.grid_columnconfigure(2, weight=1)

        big_font = ("Arial", 24, "bold")
        tk.Button(nav_frame, text="<", font=big_font, width=2, command=self.prev_month).grid(row=0, column=0, sticky="e")
        self.header = tk.Label(nav_frame, font=big_font, width=15, anchor="center", bg="#6bf39d")
        self.header.grid(row=0, column=1, sticky="n")
        tk.Button(nav_frame, text=">", font=big_font, width=2, command=self.next_month).grid(row=0, column=2, sticky="w")

        # calendar
        self.calendar_frame = tk.Frame(self, bd=2, relief="groove", bg="#6bf39d")
        self.calendar_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        # time
        time_frame = tk.Frame(self, bg="#6bf39d")
        time_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=5)
        time_frame.grid_columnconfigure(0, weight=1)
        time_frame.grid_columnconfigure(1, weight=1)

        tk.Label(time_frame, text="Time(HH:MM) :", font=("Arial", 14), bg="#6bf39d").grid(row=0, column=0, columnspan=2, pady=5)

        now = datetime.now()
        self.hour_var = tk.StringVar(value=now.strftime("%H"))
        self.minute_var = tk.StringVar(value=now.strftime("%M"))

        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(60)]

        self.hour_menu = ttk.Combobox(time_frame, textvariable=self.hour_var, values=hours, state="readonly", font=("Arial", 14), justify="center")
        self.hour_menu.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.minute_menu = ttk.Combobox(time_frame, textvariable=self.minute_var, values=minutes, state="readonly", font=("Arial", 14), justify="center")
        self.minute_menu.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # attribute
        attr_frame = tk.Frame(self, bg="#6bf39d")
        attr_frame.grid(row=4, column=0, padx=20, pady=5, sticky="nsew")
        tk.Label(attr_frame, text="Attribute:", font=("Arial", 14), bg="#6bf39d").pack()
        self.attr_var = tk.StringVar(value="Class")
        attributes = ["Class", "Tasks", "Appointments", "Important events", "Date"]
        self.attr_menu = ttk.Combobox(attr_frame, textvariable=self.attr_var, values=attributes, state="readonly", justify="center", font=("Arial", 14))
        self.attr_menu.pack(pady=5, ipadx=5, ipady=5)

        # description
        desc_frame = tk.Frame(self, bg="#6bf39d")
        desc_frame.grid(row=5, column=0, sticky="nsew", padx=20, pady=5)
        desc_frame.grid_columnconfigure(0, weight=1)
        tk.Label(desc_frame, text="Description:", font=("Arial", 14), bg="#6bf39d").grid(row=0, column=0, pady=5)
        self.desc_entry = tk.Entry(desc_frame, justify="left", font=("Arial", 14))
        self.desc_entry.grid(row=1, column=0, sticky="nsew", padx=50, pady=5)

        # save
        save_frame = tk.Frame(self, bg="#6bf39d")
        save_frame.grid(row=6, column=0, sticky="nsew", padx=20, pady=10)
        save_frame.grid_columnconfigure(0, weight=1)
        tk.Button(save_frame, text="Save", command=self.save, font=("Arial", 16, "bold"), bg="#3f3ce7", fg="white").grid(row=0, column=0, sticky="nsew", padx=100, pady=5)

        self.draw_calendar()

    def draw_calendar(self):
        for w in self.calendar_frame.winfo_children():
            w.destroy()

        for r in range(7):
            self.calendar_frame.grid_rowconfigure(r, weight=1)
        for c in range(7):
            self.calendar_frame.grid_columnconfigure(c, weight=1)

        self.header.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        for i, d in enumerate(days):
            lbl = tk.Label(self.calendar_frame, text=d, font=("Arial", 12, "bold"), bg="#6bf39d")
            lbl.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)

        month_days = calendar.monthcalendar(self.current_year, self.current_month)
        for r, week in enumerate(month_days, start=1):
            for c, day in enumerate(week):
                if day != 0:
                    bdate = datetime(self.current_year, self.current_month, day).date()
                    btn = tk.Button(self.calendar_frame, text=str(day), command=lambda d=day: self.pick_date(d))
                    # highlight today
                    if bdate == datetime.now().date():
                        btn.config(fg="blue", font=("Arial", 10, "bold"))
                    # highlight selected
                    if self.selected_date and bdate == self.selected_date.date():
                        btn.config(bg="#ffef8f")
                    btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                else:
                    tk.Label(self.calendar_frame, text=" ", bg="#6bf39d").grid(row=r, column=c, sticky="nsew")

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.draw_calendar()

    def pick_date(self, day):
        picked = datetime(self.current_year, self.current_month, day)
        if picked.date() < datetime.now().date():
            messagebox.showerror("Error", "Cannot select a past date")
            return
        self.selected_date = picked
        # refresh calendar to show selection
        self.draw_calendar()
        messagebox.showinfo("Selected", f"Date selected: {picked.strftime('%Y-%m-%d')}")

    def save(self):
        if not self.selected_date:
            messagebox.showerror("Error", "Please select a date first")
            return

        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            t = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
        except Exception:
            messagebox.showerror("Error", "Invalid time format!")
            return

        reminder_dt = datetime.combine(self.selected_date.date(), t)
        if reminder_dt < datetime.now():
            messagebox.showerror("Error", "Cannot save a past reminder")
            return

        attr = self.attr_var.get() or ""
        desc = self.desc_entry.get() or "-"
        r = NormalReminder(reminder_dt, desc, attr)
        self.controller.normal_reminders.append(r)
        self.controller.save_to_file()

        messagebox.showinfo("Success", "Reminder saved!")
        self.controller.show_right("ViewReminderPage")


# add repeat reminder page
class AddRepeatPage(tk.Frame):
    def __init__(self, parent, controller: SimpleReminder):
        super().__init__(parent, bg="#6bf39d")
        self.controller = controller

        tk.Label(
            self, text="Add Repeat Reminder", font=("Arial", 36, "bold"), bg="#6bf39d"
        ).pack(pady=10)

        # Time
        time_frame = tk.Frame(self, bg="#6bf39d")
        time_frame.pack(pady=10, fill="x", padx=20)
        time_frame.grid_columnconfigure(0, weight=1)
        time_frame.grid_columnconfigure(1, weight=1)

        tk.Label(time_frame, text="Time (HH:MM) :", font=("Arial", 14), bg="#6bf39d").grid(
            row=0, column=0, columnspan=2, pady=5
        )
        now = datetime.now()
        self.hour_var = tk.StringVar(value=now.strftime("%H"))
        self.minute_var = tk.StringVar(value=now.strftime("%M"))

        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(60)]

        self.hour_menu = ttk.Combobox(
            time_frame, textvariable=self.hour_var, values=hours,
            state="readonly", font=("Arial", 14), justify="center"
        )
        self.hour_menu.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.minute_menu = ttk.Combobox(
            time_frame, textvariable=self.minute_var, values=minutes,
            state="readonly", font=("Arial", 14), justify="center"
        )
        self.minute_menu.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # Attribute
        attr_frame = tk.Frame(self, bg="#6bf39d")
        attr_frame.pack(pady=10, fill="x", padx=20)
        tk.Label(attr_frame, text="Attribute:", font=("Arial", 14), bg="#6bf39d").pack()
        self.attr_var = tk.StringVar(value="Class")
        attributes = ["Class", "Tasks", "Appointments", "Important events", "Date"]
        self.attr_menu = ttk.Combobox(
            attr_frame, textvariable=self.attr_var, values=attributes,
            state="readonly", justify="center", font=("Arial", 14)
        )
        self.attr_menu.pack(pady=5, ipadx=5, ipady=5)

        # Description
        desc_frame = tk.Frame(self, bg="#6bf39d")
        desc_frame.pack(pady=10, fill="x", padx=20)
        tk.Label(desc_frame, text="Description:", font=("Arial", 14), bg="#6bf39d").pack()
        self.desc_entry = tk.Entry(desc_frame, justify="left", font=("Arial", 14))
        self.desc_entry.pack(fill="x", padx=50, pady=5)

        # Day of Week
        day_frame = tk.Frame(self, bg="#6bf39d")
        day_frame.pack(pady=10, fill="x", padx=20)
        tk.Label(day_frame, text="Day of Week:", font=("Arial", 14), bg="#6bf39d").pack()
        self.day_var = tk.StringVar(value="Monday")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.day_menu = ttk.Combobox(
            day_frame, textvariable=self.day_var, values=days,
            state="readonly", font=("Arial", 14), justify="center"
        )
        self.day_menu.pack(pady=5, ipadx=5, ipady=5)

        # Save Button
        tk.Button(
            self, text="Save", command=self.save,
            font=("Arial", 16, "bold"), bg="#3f3ce7", fg="white"
        ).pack(pady=20, ipadx=10, ipady=5)

    def save(self):
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            t = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
        except Exception:
            messagebox.showerror("Error", "Invalid time format!")
            return

        desc = self.desc_entry.get() or "-"
        weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(
            self.day_var.get()
        )
        attr = self.attr_var.get() or ""

        # Pass attribute and description separately (fixed)
        r = RepeatReminder(weekday, t, desc, attr)
        self.controller.repeat_reminders.append(r)
        self.controller.save_to_file()

        messagebox.showinfo("Success", "Repeat reminder added!")
        self.controller.show_right("ViewReminderPage")

# view reminders page
class ViewReminderPage(tk.Frame):
    def __init__(self, parent, controller: SimpleReminder):
        super().__init__(parent, bg="#6bf39d")
        self.controller = controller
        self.list_frame = tk.Frame(self, bg="#6bf39d")
        self.list_frame.pack(fill="both", expand=True)

    def show(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        # Active reminders
        tk.Label(self.list_frame, text="View Reminders", font=("Arial", 18, "bold"), bg="#6bf39d").pack(pady=10)
        for r in sorted(self.controller.normal_reminders, key=lambda x: x.dt):
            f = tk.Frame(self.list_frame, bd=1, relief="solid", pady=4, bg="#6bf39d")
            f.pack(fill="x", padx=5, pady=4)
            text = f"[Normal] | {r.dt.strftime('%Y-%m-%d %H:%M')} | {r.attribute} | {r.description}"
            tk.Label(f, text=text, anchor="w", font=("Arial", 15), bg="#6bf39d").pack(side="left", padx=6, expand=True, fill="x")
            tk.Button(f, text="X", command=lambda rid=r.id, t=text: self.delete("normal", rid, t)).pack(side="right", padx=6)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for r in sorted(self.controller.repeat_reminders, key=lambda x: (x.weekday, x.at_time)):
            f = tk.Frame(self.list_frame, bd=1, relief="solid", pady=4, bg="#6bf39d")
            f.pack(fill="x", padx=5, pady=4)
            text = f"[Repeat] | {days[r.weekday]} {r.at_time.strftime('%H:%M')} | {r.attribute} | {r.description}"
            tk.Label(f, text=text, anchor="w", font=("Arial", 15), bg="#6bf39d").pack(side="left", padx=6, expand=True, fill="x")
            tk.Button(f, text="X", command=lambda rid=r.id, t=text: self.delete("repeat", rid, t)).pack(side="right", padx=6)

        # History reminders
        if self.controller.history_reminders:
            tk.Label(self.list_frame, text="History Reminders", font=("Arial", 18, "bold"), bg="#6bf39d").pack(pady=10)
            for text in self.controller.history_reminders:
                f = tk.Frame(self.list_frame, bd=1, relief="solid", pady=4, bg="#6bf39d")
                f.pack(fill="x", padx=5, pady=4)
                tk.Label(f, text=text, anchor="w", font=("Arial", 15), bg="#6bf39d").pack(side="left", padx=6, expand=True, fill="x")
                tk.Button(f, text="X", command=lambda t=text: self.delete_history(t)).pack(side="right", padx=6)

    def delete(self, typ, rid, text):
        if typ == "normal":
            self.controller.normal_reminders = [r for r in self.controller.normal_reminders if r.id != rid]
        else:
            self.controller.repeat_reminders = [r for r in self.controller.repeat_reminders if r.id != rid]
            self.controller.save_to_file()
            self.controller.add_to_history(text)
            self.show()

    def delete_history(self, text):
        self.controller.delete_history(text)
        self.show()