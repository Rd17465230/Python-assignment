# Student Assistant App

A desktop application to help students manage their academic life.  
Built with **Python** and **Tkinter**, it provides tools for tracking homework, setting reminders, and calculating GPA/CGPA.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **GPA & CGPA Calculator**  
  Enter course grades and credits to compute GPA and cumulative CGPA.  
  Displays a Matplotlib chart for academic progress.  
  Data is stored in `gpa_data.json` and auto-loaded at startup.

- **Homework Planner**  
  Manage assignments with deadlines and track their completion status.

- **Simple Reminder System**  
  One-time or repeating reminders with pop-up notifications.

- **User Authentication**  
  A simple login page to access the application.

- **Responsive UI**  
  Adapts to different window sizes for a smooth user experience.

## 🛠 Tech Stack

- **GUI**: [Tkinter](https://docs.python.org/3/library/tkinter.html)
- **Image Handling**: [Pillow](https://pypi.org/project/Pillow/)
- **Date Handling**: [tkcalendar](https://pypi.org/project/tkcalendar/)
- **Charts**: [Matplotlib](https://matplotlib.org/)
- **Data Storage**: JSON (`gpa_data.json`) and text files

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2.  **Install dependencies**:
    Make sure you have Python installed. Then, install the required libraries using pip:

    ```bash
    pip install -r requirements.txt
    ```

3. **Assets**
    Ensure a photo/ directory exists with the required icon images
    (e.g. home.png, gpa.png, reminder.png, planner.png, etc.).

## Usage

To run the application, execute the `main.py` file:

```bash
python main.py
```

The application will start with the login page.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## FAQ

**Q: What version of Python do I need?**  
A: Python 3.8 or higher is required.
