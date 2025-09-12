import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time as dtime
import calendar
import os

DATA_FILE = "reminders.txt"

# reminder_list
class NormalReminder:
    def __init__(self, dt: datetime, description: str):
        self.dt = dt
        self.description = description
        self.id = f"N-{self.dt.timestamp()}-{hash(description)}"

class RepeatReminder:
    def __init__(self, weekday: int, at_time: dtime, description: str):
        self.weekday = weekday
        self.at_time = at_time
        self.description = description
        self.id = f"R-{weekday}-{at_time.strftime('%H%M')}-{hash(description)}"

# main function
class SimpleReminder(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller or self

        self.normal_reminders = []
        self.repeat_reminders = []
        self.load_from_file()

        # =========== 主布局：左右两栏 =============
        # 改成 grid，让左右都能拉伸
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 左边栏固定宽度
        left_frame = tk.Frame(self, width=220, bd=2, relief="ridge")
        left_frame.grid(row=0, column=0, sticky="ns")
        left_frame.grid_propagate(False)

        tk.Label(left_frame, text="Simple Reminder App", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Button(left_frame, text="Add Reminder",
                  command=lambda: self.show_right("AddReminderPage")).pack(pady=10, fill="x")
        tk.Button(left_frame, text="Add Repeat Reminder",
                  command=lambda: self.show_right("AddRepeatPage")).pack(pady=10, fill="x")
        tk.Button(left_frame, text="View Reminders",
                  command=lambda: self.show_right("ViewReminderPage")).pack(pady=10, fill="x")
        tk.Button(left_frame, text="Back to Main Menu",
                  command=lambda: self.controller.show_main_menu()).pack(pady=10, fill="x")

        # 右边可扩展区域
        self.right_frame = tk.Frame(self, bd=2, relief="ridge")
        self.right_frame.grid(row=0, column=1, sticky="nsew")   # 关键：sticky 全方向
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # 右侧页面
        self.right_pages = {}
        for F in (AddReminderPage, AddRepeatPage, ViewReminderPage):
            frame = F(self.right_frame, self)
            self.right_pages[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_right("AddReminderPage")
        
        self.check_reminders()

    def show_right(self, name):
        frame = self.right_pages[name]
        if hasattr(frame, "show"):  # call show() if page has it
            frame.show()
        frame.tkraise()

    # check reminders
    def check_reminders(self):
        now = datetime.now()

        # one time reminders
        due_normals = [r for r in self.normal_reminders if abs((r.dt - now).total_seconds()) < 6]
        for r in due_normals:
            self.show_popup(r.description)
            self.normal_reminders = [x for x in self.normal_reminders if x.id != r.id]
            self.save_to_file()

        # repeat reminders
        for r in self.repeat_reminders:
            if r.weekday == now.weekday():
                if abs((datetime.combine(now.date(), r.at_time) - now).total_seconds()) < 6:
                    self.show_popup(r.description)

        self.after(5000, self.check_reminders)

    def show_popup(self, description):
        popup = tk.Toplevel(self)
        popup.title("Reminder")
        popup.geometry("280x120")
        tk.Label(popup, text=description, font=("Arial", 12, "bold")).pack(pady=15)
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=5)

    #  save file to reminders_txt
    def save_to_file(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            for r in self.normal_reminders:
                f.write(f"N|{r.dt.strftime('%Y-%m-%d %H:%M')}|{r.description}\n")
            for r in self.repeat_reminders:
                f.write(f"R|{r.weekday}|{r.at_time.strftime('%H:%M')}|{r.description}\n")

    def load_from_file(self):
        self.normal_reminders.clear() #clear reminders
        self.repeat_reminders.clear()

        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if not parts:
                    continue
                if parts[0] == "N" and len(parts) == 3:
                    dt = datetime.strptime(parts[1], "%Y-%m-%d %H:%M")
                    self.normal_reminders.append(NormalReminder(dt, parts[2]))
                elif parts[0] == "R" and len(parts) == 4:
                    weekday = int(parts[1])
                    at_time = datetime.strptime(parts[2], "%H:%M").time()
                    self.repeat_reminders.append(RepeatReminder(weekday, at_time, parts[3]))

# add one time reminder function
class AddReminderPage(tk.Frame):
    def __init__(self, parent, controller: SimpleReminder):
        super().__init__(parent)
        self.controller = controller

        self.selected_date = None
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        tk.Label(self, text="Add Reminder", font=("Arial", 14, "bold")).pack(pady=10)

        # calendar
        self.header = tk.Label(self, font=("Arial", 12, "bold"))
        self.header.pack()

        nav = tk.Frame(self)
        nav.pack()
        tk.Button(nav, text="<", command=self.prev_month).pack(side="left")
        tk.Button(nav, text=">", command=self.next_month).pack(side="left")

        self.calendar_frame = tk.Frame(self)
        self.calendar_frame.pack()

        self.time_frame = tk.Frame(self)
        self.time_frame.pack(pady=10)

        tk.Label(self.time_frame, text="Time (HH:MM):").pack()
        self.time_entry = tk.Entry(self.time_frame)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.time_entry.pack(pady=5)

        tk.Label(self.time_frame, text="Description:").pack()
        self.desc_entry = tk.Entry(self.time_frame, width=30)
        self.desc_entry.pack(pady=5)

        tk.Button(self, text="Save", command=self.save).pack(pady=10)

        self.draw_calendar()

    # define the calender
    def draw_calendar(self):
        for w in self.calendar_frame.winfo_children():
            w.destroy()

        self.header.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        for i, d in enumerate(days):
            tk.Label(self.calendar_frame, text=d, width=5).grid(row=0, column=i)

        month_days = calendar.monthcalendar(self.current_year, self.current_month)
        for r, week in enumerate(month_days, start=1):
            for c, day in enumerate(week):
                if day != 0:
                    b = tk.Button(self.calendar_frame, text=str(day),
                                  command=lambda d=day: self.pick_date(d))
                    if datetime(self.current_year, self.current_month, day).date() == datetime.now().date():
                        b.config(fg="blue")
                    b.grid(row=r, column=c, padx=2, pady=2)

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
        messagebox.showinfo("Selected", f"Date selected: {picked.strftime('%Y-%m-%d')}")

    def save(self):
        if not self.selected_date:
            messagebox.showerror("Error", "Please select a date first")
            return

        try:
            time_str = self.time_entry.get()
            t = datetime.strptime(time_str, "%H:%M").time()
        except Exception:
            messagebox.showerror("Error", "Invalid time format!")
            return

        reminder_dt = datetime.combine(self.selected_date.date(), t)
        if reminder_dt < datetime.now():
            messagebox.showerror("Error", "Cannot save a past reminder")
            return

        desc = self.desc_entry.get() or "-"
        r = NormalReminder(reminder_dt, desc)
        self.controller.normal_reminders.append(r)
        self.controller.save_to_file()

        messagebox.showinfo("Success", "Reminder saved!")
        self.controller.show_right("ViewReminderPage")

# add repeat reminder function
class AddRepeatPage(tk.Frame):
    def __init__(self, parent, controller: SimpleReminder):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Add Repeat Reminder", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Time (HH:MM):").pack()
        self.time_entry = tk.Entry(self)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.time_entry.pack(pady=5)

        tk.Label(self, text="Description:").pack()
        self.desc_entry = tk.Entry(self, width=30)
        self.desc_entry.pack(pady=5)

        tk.Label(self, text="Day of Week:").pack()
        self.day_var = tk.StringVar(value="Monday")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.day_menu = ttk.Combobox(self, textvariable=self.day_var, values=days, state="readonly")
        self.day_menu.pack(pady=5)

        tk.Button(self, text="Save", command=self.save).pack(pady=10)

    def save(self):
        try:
            time_str = self.time_entry.get()
            t = datetime.strptime(time_str, "%H:%M").time()
        except Exception:
            messagebox.showerror("Error", "Invalid time format!")
            return

        desc = self.desc_entry.get() or "-"
        weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(self.day_var.get())

        r = RepeatReminder(weekday, t, desc)
        self.controller.repeat_reminders.append(r)
        self.controller.save_to_file()

        messagebox.showinfo("Success", "Repeat reminder added!")
        self.controller.show_right("ViewReminderPage")

# view reminder function
class ViewReminderPage(tk.Frame):
    def __init__(self, parent, controller: SimpleReminder):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="View Reminders", font=("Arial", 14, "bold")).pack(pady=10)

        self.list_frame = tk.Frame(self)
        self.list_frame.pack(fill="both", expand=True)

    def show(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        # show one time reminders
        for r in sorted(self.controller.normal_reminders, key=lambda x: x.dt):
            f = tk.Frame(self.list_frame, bd=1, relief="solid", pady=2)
            f.pack(fill="x", padx=5, pady=2)
            tk.Label(f, text=f"[Normal] | {r.dt.strftime('%Y-%m-%d %H:%M')} | {r.description}").pack(side="left", padx=5)
            tk.Button(f, text="X", command=lambda rid=r.id: self.delete("normal", rid)).pack(side="right")

        # show repeat reminders
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for r in sorted(self.controller.repeat_reminders, key=lambda x: (x.weekday, x.at_time)):
            f = tk.Frame(self.list_frame, bd=1, relief="solid", pady=2)
            f.pack(fill="x", padx=5, pady=2)
            tk.Label(f, text=f"[Repeat] | {days[r.weekday]} | {r.at_time.strftime('%H:%M')} | {r.description}").pack(side="left", padx=5)
            tk.Button(f, text="X", command=lambda rid=r.id: self.delete("repeat", rid)).pack(side="right")

    # delete function
    def delete(self, mode, rid):
        if mode == "normal":
            self.controller.normal_reminders = [r for r in self.controller.normal_reminders if r.id != rid]
        else:
            self.controller.repeat_reminders = [r for r in self.controller.repeat_reminders if r.id != rid]

        self.controller.save_to_file()
        self.show()