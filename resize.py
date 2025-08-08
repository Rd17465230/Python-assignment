from tkinter import *
from abc import ABC, abstractmethod

class Resize(ABC):
    def __init__(self):
        self.base_font_size = 10
        self.base_width = 800
        self.scaling_factor = 1.0
        self.resize_id = None  # 用于防抖
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event=None):
        if self.resize_id is not None:
            self.after_cancel(self.resize_id)
        self.resize_id = self.after(100, self._debounced_resize)

    def _debounced_resize(self):
        new_width = self.winfo_width()
        if new_width > 0:
            self.scaling_factor = max(0.5, new_width / self.base_width)
            self.update_layout()
        self.resize_id = None

    @abstractmethod
    def update_layout(self):
        pass