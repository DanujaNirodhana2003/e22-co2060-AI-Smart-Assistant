import tkinter as tk
import multiprocessing
import queue
from tkinter import font

def round_rectangle(canvas, x1, y1, x2, y2, radius=30, **kwargs):
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)

def _launch_chat_window(msg_queue):
    # --- CONFIG ---
    BG_COLOR = "#050010"       
    ACCENT_COLOR = "#28C8FF"   
    INPUT_BG = "#151020"       
    TEXT_COLOR = "#E0E0E0"     
    TRANSPARENT_KEY = "#000001" 
    
    FONT_MAIN = ("Segoe UI", 10)
    FONT_BOLD = ("Segoe UI", 10, "bold")
    FONT_MONO = ("Consolas", 10)

    root = tk.Tk()
    root.title("AI Assistant")
    
    # Window Setup
    root.overrideredirect(True)
    root.configure(bg=TRANSPARENT_KEY)
    root.attributes("-transparentcolor", TRANSPARENT_KEY)
    root.attributes("-alpha", 0.70) 
    
    # --- SIZE ADJUSTMENT ---
    w, h = 400, 1000 
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{sw-w-20}+{sh-h-50}")

    root.withdraw() 

    # --- MAIN CANVAS ---
    canvas = tk.Canvas(root, bg=TRANSPARENT_KEY, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Draw Background Shape
    round_rectangle(canvas, 2, 2, w-2, h-2, radius=30, 
                    fill=BG_COLOR, outline=ACCENT_COLOR, width=1)

    # Content Container
    content_frame = tk.Frame(root, bg=BG_COLOR)
    content_frame.place(x=20, y=20, width=w-40, height=h-40)

    # --- LAYOUT ---
    
    # 1. HEADER
    header = tk.Frame(content_frame, bg=BG_COLOR)
    header.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
    
    tk.Label(header, text="AI CHAT", bg=BG_COLOR, fg=ACCENT_COLOR, font=FONT_BOLD).pack(side=tk.LEFT)
    tk.Button(header, text="✕", command=lambda: root.withdraw(), bg=BG_COLOR, fg="#666", bd=0, font=("Arial", 12)).pack(side=tk.RIGHT)

    # 2. INPUT AREA (Rounded)
    input_container = tk.Frame(content_frame, bg=BG_COLOR)
    input_container.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 5))

    tk.Label(input_container, text="TYPE MESSAGE:", bg=BG_COLOR, fg="#666", font=("Segoe UI", 7, "bold")).pack(anchor="w", padx=5)

    input_height = 50
    input_canvas = tk.Canvas(input_container, bg=BG_COLOR, height=input_height, highlightthickness=0)
    input_canvas.pack(fill=tk.X, pady=(2, 0))

    # Draw the rounded "pill"
    box_width = w - 50 
    round_rectangle(input_canvas, 2, 2, box_width, input_height-2, radius=20, fill=INPUT_BG, outline=ACCENT_COLOR)

    # --- INPUT WIDGETS ---
    
    # [UPDATED] Send Button
    # We place this FIRST so we can calculate the text box width relative to it
    send_btn = tk.Button(input_canvas, text="➤", 
                         bg=INPUT_BG, fg=ACCENT_COLOR, 
                         activebackground=INPUT_BG, activeforeground="white",
                         bd=0, font=("Arial", 14), cursor="hand2")
    
    # Place button on the far right inside the pill
    send_btn.place(x=box_width-45, y=5, width=40, height=40)

    # [UPDATED] Input Text Box
    # Width is reduced by ~50px to make room for the button
    input_box = tk.Text(input_canvas, height=2, bg=INPUT_BG, fg="white", font=FONT_MAIN,
                        bd=0, highlightthickness=0, insertbackground="white")
    input_box.place(x=15, y=10, width=box_width-60, height=input_height-20)

    # 3. CHAT HISTORY
    history_box = tk.Text(content_frame, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_MAIN,
                          bd=0, highlightthickness=0, state="disabled", wrap=tk.WORD)
    history_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    history_box.tag_config("user_msg", justify='right', foreground="white", rmargin=5)
    history_box.tag_config("system_msg", justify='left', foreground=ACCENT_COLOR, lmargin1=5)
    history_box.tag_config("timestamp", foreground="#666666", font=("Consolas", 8), justify='center')

    # --- LOGIC ---

    def add_message(text, sender="system"):
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M")
        
        history_box.config(state="normal")
        history_box.insert(tk.END, f"\n{ts}\n", "timestamp")
        
        if sender == "user":
            history_box.insert(tk.END, f"{text}\n", "user_msg")
        else:
            history_box.insert(tk.END, f"{text}\n", "system_msg")
            
        history_box.see(tk.END)
        history_box.config(state="disabled")

    def send_user_message(event=None):
        text = input_box.get("1.0", tk.END).strip()
        if text:
            add_message(text, sender="user")
            input_box.delete("1.0", tk.END)
        return "break"

    # Bind Enter Key
    input_box.bind("<Return>", send_user_message)
    
    # Bind the Send Button
    send_btn.config(command=send_user_message)

    def check_queue():
        try:
            while True:
                text = msg_queue.get_nowait()
                if text:
                    root.deiconify()
                    root.attributes("-topmost", True)
                    
                    add_message(f"Captured:\n{text}", sender="system")
                    
                    root.lift()
                    input_box.focus_set()

                    root.after(1000, lambda: root.attributes("-topmost", False))
        except queue.Empty:
            pass
        root.after(100, check_queue)

    root.after(100, check_queue)
    root.mainloop()

def start_chat_process():
    msg_queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=_launch_chat_window, args=(msg_queue,), daemon=True)
    p.start()
    return msg_queue, p