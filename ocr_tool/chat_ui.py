import tkinter as tk
from tkinter import font
import time
import pyperclip
import threading
import sys

class ChatUI:
    def __init__(self):
        self.root = tk.Tk()
        self.width = 400
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x_pos = self.screen_width  # Start off-screen (right)
        
        # Window Setup
        self.root.geometry(f"{self.width}x{self.screen_height}+{self.x_pos}+0")
        self.root.overrideredirect(True) # Frameless
        self.root.configure(bg="#1E1E1E")
        self.root.attributes("-topmost", True)
        
        # Design Constants
        self.BG_COLOR = "#1E1E1E"
        self.CHAT_BG = "#2D2D2D"
        self.USER_BUBBLE_COLOR = "#005c4b" # WhatsApp-ish dark green or similar
        self.TEXT_COLOR = "#EAEAEA"
        self.INPUT_BG = "#404040"
        
        # Fonts
        self.font_msg = font.Font(family="Segoe UI", size=11)
        self.font_bold = font.Font(family="Segoe UI", size=11, weight="bold")
        
        # UI Elements
        self._setup_ui()
        
        # State
        self.is_open = False
        
        # Bindings
        self.root.bind("<Escape>", lambda e: self.close())
        
        # Start Animation logic
        self.root.after(100, self.animate_open)
        
        # Load Clipboard Content as first message
        self.root.after(600, self._load_clipboard_msg)

    def _setup_ui(self):
        # 1. Header
        header_frame = tk.Frame(self.root, bg="#252526", height=50)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="Assistant", bg="#252526", fg="white", font=("Segoe UI", 12, "bold"))
        title.pack(side="left", padx=15, pady=10)
        
        close_btn = tk.Button(header_frame, text="✕", bg="#252526", fg="white", bd=0, 
                              command=self.close, cursor="hand2", font=("Arial", 12))
        close_btn.pack(side="right", padx=10)

        # 2. Chat History (Canvas + Scrollbar)
        self.chat_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        self.chat_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.canvas = tk.Canvas(self.chat_frame, bg=self.BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.BG_COLOR)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.width)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # 3. Input Area
        input_frame = tk.Frame(self.root, bg=self.CHAT_BG, height=60)
        input_frame.pack(fill="x", side="bottom")
        
        self.entry = tk.Entry(input_frame, bg=self.INPUT_BG, fg="white", font=self.font_msg, bd=0, insertbackground="white")
        self.entry.pack(side="left", fill="both", expand=True, padx=10, pady=15)
        self.entry.bind("<Return>", self._send_message)
        
        send_btn = tk.Button(input_frame, text="➤", bg=self.CHAT_BG, fg="#007acc", bd=0, font=("Arial", 16),
                             cursor="hand2", command=self._send_message)
        send_btn.pack(side="right", padx=10)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def animate_open(self):
        target_x = self.screen_width - self.width
        step = 40  # Speed
        
        if self.x_pos > target_x:
            self.x_pos -= step
            if self.x_pos < target_x: self.x_pos = target_x
            self.root.geometry(f"{self.width}x{self.screen_height}+{self.x_pos}+0")
            self.root.after(10, self.animate_open)
        else:
            self.is_open = True
            self.entry.focus()

    def close(self):
        # Animate close logic if needed, for now just exit
        self.root.quit()

    def add_message(self, text, is_user=True):
        """
        Adds a message bubble to the scrollable frame.
        """
        # Outer container for the bubble (row)
        msg_container = tk.Frame(self.scrollable_frame, bg=self.BG_COLOR)
        msg_container.pack(fill="x", pady=5, padx=10)
        
        # Constraints for max width
        max_width = int(self.width * 0.75)
        
        # Bubble styling
        bubble_color = self.USER_BUBBLE_COLOR if is_user else self.CHAT_BG
        anchor = "e" if is_user else "w" # East (right) for user, West (left) for AI
        justify = "left"
        
        # Inner Frame for the bubble itself
        bubble = tk.Frame(msg_container, bg=self.BG_COLOR)
        bubble.pack(anchor=anchor)
        
        # The Label inside
        lbl = tk.Label(bubble, text=text, bg=bubble_color, fg=self.TEXT_COLOR, 
                       font=self.font_msg, wraplength=max_width, justify=justify,
                       padx=10, pady=8)
        lbl.pack()
        
        # Add a tiny corner radius effect (hacky with images or canvas, but for Tkinter basic Label is square)
        # We can just rely on color for now.
        
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.root.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _load_clipboard_msg(self):
        try:
            text = pyperclip.paste()
            if text and text.strip():
                self.add_message(text.strip(), is_user=True)
                # Simulate AI response placeholder
                self.root.after(1000, lambda: self.add_message("This is a placeholder response from the AI.", is_user=False))
        except Exception as e:
            print(f"Clipboard error: {e}")

    def _send_message(self, event=None):
        msg = self.entry.get()
        if msg.strip():
            self.add_message(msg, is_user=True)
            self.entry.delete(0, tk.END)
            self._scroll_to_bottom()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ChatUI()
    app.run()
