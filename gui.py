"""
Main GUI for the Advanced Port Scanner and Wireless Attack Tool
Author: morningstarxcdcode
Description: Provides a graphical interface for users to perform port scans
and wireless attacks.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import socket
import queue

# Import scanning backend functions
from scanner.port_scanner import run_scan
from wireless.wireless_attacks import run_attack
from utils.chatbot import Chatbot
from utils import ar_visualization


class AnimatedProgressBar(tk.Canvas):
    def __init__(self, parent: tk.Widget, width: int = 700, height: int = 25,
                 max_value: int = 100, **kwargs):
        """
        Initialize the animated progress bar.

        :param parent: The parent widget.
        :param width: The width of the progress bar.
        :param height: The height of the progress bar.
        :param max_value: The maximum value of the progress bar.
        """
        super().__init__(parent, width=width, height=height,
                         bg="#000000", **kwargs)
        self.width = width
        self.height = height
        self.max_value = max_value
        self.progress = 0
        self.rect = self.create_rectangle(0, 0, 0, height, fill="#00FF00")
        self.text = self.create_text(width // 2, height // 2, text="0%",
                                     fill="#00FF00",
                                     font=("Consolas", 12, "bold"))

    def update_progress(self, value: int) -> None:
        """Update the progress bar with the current value."""
        self.progress = value
        fill_width = int(self.width * (self.progress / self.max_value))
        self.coords(self.rect, 0, 0, fill_width, self.height)
        self.itemconfig(
            self.text,
            text=f"{int((self.progress / self.max_value) * 100)}%"
        )
        self.update()


def get_local_ip() -> str:
    """Retrieve the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_default_port_range() -> str:
    """Return the default port range for scanning."""
    return "1-1000"


# Initialize chatbot instance
chatbot = Chatbot()


def run_port_scan(port_target_entry_widget, port_range_entry_widget,
                    port_scan_button_widget, port_output_text_widget,
                    port_progress_bar_widget, port_elapsed_label_widget) -> None:
    """Initiate the port scan based on user input."""
    target = port_target_entry_widget.get().strip()
    port_range = port_range_entry_widget.get().strip()
    if not target:
        messagebox.showerror("Input Error",
                             "Please enter a target IP address.")
        return
    if not port_range:
        port_range = get_default_port_range()
    port_scan_button_widget.config(state=tk.DISABLED)
    port_output_text_widget.config(state=tk.NORMAL)
    port_output_text_widget.delete(1.0, tk.END)
    port_progress_bar_widget.update_progress(0)
    port_elapsed_label_widget.config(text="Elapsed Time: 0.0s")
    start_time = time.time()

    port_scan_done = threading.Event()

    def update_elapsed() -> None:
        """Update the elapsed time label during the scan."""
        while not port_scan_done.is_set():
            elapsed = time.time() - start_time
            port_elapsed_label_widget.config(text=f"Elapsed Time: {elapsed:.1f}s")
            time.sleep(0.1)

    def scan() -> None:
        """Perform the port scan using the scanning backend."""
        try:
            # Use "ai" mode to enable AI-driven predictive scanning
            for progress, line in run_scan(target, "ai"): # target is from outer scope
                port_output_text_widget.insert(tk.END, line + "\n")
                port_output_text_widget.see(tk.END)
                port_progress_bar_widget.update_progress(progress)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred during the scan: {str(e)}"
            )
        finally:
            port_scan_done.set()
            elapsed = time.time() - start_time
            port_output_text_widget.insert(
                tk.END,
                f"\nScan completed in {elapsed:.2f} seconds.\n"
            )
            port_scan_button_widget.config(state=tk.NORMAL)
            port_progress_bar_widget.update_progress(100)
            port_output_text_widget.config(state=tk.DISABLED)

    threading.Thread(target=update_elapsed, daemon=True).start()
    threading.Thread(target=scan, daemon=True).start()


def run_wireless_attack(wireless_target_entry_widget,
                        wireless_attack_button_widget,
                        wireless_output_text_widget,
                        wireless_progress_bar_widget,
                        wireless_elapsed_label_widget) -> None:
    """Initiate the wireless attack based on user input."""
    target = wireless_target_entry_widget.get().strip()
    if not target:
        messagebox.showerror("Input Error",
                             "Please enter a target IP address.")
        return
    wireless_attack_button_widget.config(state=tk.DISABLED)
    wireless_output_text_widget.config(state=tk.NORMAL)
    wireless_output_text_widget.delete(1.0, tk.END)
    wireless_progress_bar_widget.update_progress(0)
    wireless_elapsed_label_widget.config(text="Elapsed Time: 0.0s")
    start_time = time.time()

    log_queue = queue.Queue()  # This can remain local

    wireless_attack_done = threading.Event()

    def log_handler() -> None:
        """Handle logging output during the wireless attack."""
        while True:
            try:
                msg = log_queue.get(timeout=0.1)
                wireless_output_text_widget.insert(tk.END, msg + "\n")
                wireless_output_text_widget.see(tk.END)
            except queue.Empty:
                if wireless_attack_done.is_set():
                    break

    def update_elapsed() -> None:
        """Update the elapsed time label during the wireless attack."""
        while not wireless_attack_done.is_set():
            elapsed = time.time() - start_time
            wireless_elapsed_label_widget.config(
                text=f"Elapsed Time: {elapsed:.1f}s"
            )
            time.sleep(0.1)

    def attack() -> None:
        """Perform the wireless attack using the wireless attacks module."""
        class QueueLogger: # This can remain local
            def info(self, msg: str) -> None:
                log_queue.put(msg)
        logger = QueueLogger()
        try:
            run_attack(target) # target is from outer scope
            logger.info("Wireless attack finished")
        except Exception as e:
            logger.info(f"Error: {e}")
        finally:
            wireless_attack_done.set()
            elapsed = time.time() - start_time
            log_queue.put(
                f"\nWireless attack completed in {elapsed:.2f} seconds."
            )
            wireless_attack_button_widget.config(state=tk.NORMAL)
            wireless_progress_bar_widget.update_progress(100)
            wireless_output_text_widget.config(state=tk.DISABLED)

    threading.Thread(target=log_handler, daemon=True).start()
    threading.Thread(target=update_elapsed, daemon=True).start()
    threading.Thread(target=attack, daemon=True).start()


# Chatbot interaction functions and UI


def process_chat_input(chatbot_input_widget, chatbot_output_widget) -> None:
    user_input = chatbot_input_widget.get().strip()
    if not user_input:
        return
    response = chatbot.process_input(user_input) # chatbot is global
    chatbot_output_widget.config(state=tk.NORMAL)
    chatbot_output_widget.insert(tk.END, f"> {user_input}\n{response}\n\n")
    chatbot_output_widget.see(tk.END)
    chatbot_output_widget.config(state=tk.DISABLED)
    chatbot_input_widget.delete(0, tk.END)


def start_ar_visualization() -> None:
    """Start the AR network visualization."""
    # For now, just show a message box as placeholder
    messagebox.showinfo("AR Visualization",
                        "Starting AR network visualization (placeholder).")
    # In a native app, this would launch ARKit-based visualization
    # Here we call the placeholder function
    ar_visualization.start_ar_visualization(None)


# Additional UI/UX polish: add hover effects and tooltips for buttons


def on_enter(event):
    event.widget.config(bg="#006600")


def on_leave(event):
    event.widget.config(bg="#004400")


def schedule_scan(target, port_range, time_interval):
    """Schedule a scan to run at regular intervals."""
    print(f"Scheduling scan for {target} every {time_interval} seconds.")
    # Implement scheduling logic here
    return


def view_scan_history():
    """Display the scan history from logs."""
    print("Displaying scan history...")
    # Implement history viewing logic here
    return


def run_gui():
    """Launch the GUI for the Advanced Port Scanner."""
    root = tk.Tk()
    root.title("Advanced Port Scanner and Wireless Attack Tool")
    root.geometry("800x600")

    # Create and pack the widgets
    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # Port Scan Tab
    port_scan_tab = ttk.Frame(tab_control)
    tab_control.add(port_scan_tab, text="Port Scan")

    tk.Label(port_scan_tab, text="Target IP:", fg="#00FF00", bg="#000000",
             font=("Consolas", 12, "bold")).grid(row=0, column=0, padx=5,
                                                 pady=5, sticky="e")
    port_target_entry = tk.Entry(port_scan_tab, width=40,
                                 font=("Consolas", 12, "bold"),
                                 fg="#00FF00", bg="#000000",
                                 insertbackground="#00FF00")
    port_target_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(port_scan_tab, text="Port Range:", fg="#00FF00", bg="#000000",
             font=("Consolas", 12, "bold")).grid(row=1, column=0, padx=5,
                                                 pady=5, sticky="e")
    port_range_entry = tk.Entry(port_scan_tab, width=40,
                                font=("Consolas", 12, "bold"),
                                fg="#00FF00", bg="#000000",
                                insertbackground="#00FF00")
    port_range_entry.grid(row=1, column=1, padx=5, pady=5)
    port_range_entry.insert(0, get_default_port_range())

    port_scan_button = tk.Button(port_scan_tab, text="Start Scan",
                                 command=lambda: run_port_scan(
                                     port_target_entry, port_range_entry,
                                     port_scan_button, port_output_text,
                                     port_progress_bar, port_elapsed_label
                                 ), bg="#004400",
                                 fg="#00FF00",
                                 font=("Consolas", 14, "bold"))
    port_scan_button.grid(row=2, column=0, columnspan=2, pady=10)

    port_progress_bar = AnimatedProgressBar(port_scan_tab,
                                            width=700, height=25)
    port_progress_bar.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    port_elapsed_label = tk.Label(port_scan_tab, text="Elapsed Time: 0.0s",
                                  fg="#00FF00", bg="#000000",
                                  font=("Consolas", 12, "bold"))
    port_elapsed_label.grid(row=4, column=0, columnspan=2, pady=5)

    port_output_text = tk.Text(port_scan_tab, height=20, width=90,
                               fg="#00FF00", bg="#000000",
                               font=("Consolas", 11, "bold"),
                               insertbackground="#00FF00")
    port_output_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
    port_output_text.config(state=tk.DISABLED)

    # Wireless Attack Tab
    wireless_tab = ttk.Frame(tab_control)
    tab_control.add(wireless_tab, text="Wireless Attack")

    tk.Label(wireless_tab, text="Target IP:", fg="#00FF00", bg="#000000",
             font=("Consolas", 12, "bold")).grid(row=0, column=0, padx=5,
                                                 pady=5, sticky="e")
    wireless_target_entry = tk.Entry(wireless_tab, width=40,
                                     font=("Consolas", 12, "bold"),
                                     fg="#00FF00", bg="#000000",
                                     insertbackground="#00FF00")
    wireless_target_entry.grid(row=0, column=1, padx=5, pady=5)

    wireless_attack_button = tk.Button(wireless_tab,
                                       text="Start Wireless Attack",
                                       command=lambda: run_wireless_attack(
                                           wireless_target_entry,
                                           wireless_attack_button,
                                           wireless_output_text,
                                           wireless_progress_bar,
                                           wireless_elapsed_label
                                       ),
                                       bg="#004400", fg="#00FF00",
                                       font=("Consolas", 14, "bold"))
    wireless_attack_button.grid(row=1, column=0, columnspan=2, pady=10)

    wireless_progress_bar = AnimatedProgressBar(wireless_tab, width=700,
                                                height=25)
    wireless_progress_bar.grid(row=2, column=0, columnspan=2, padx=5,
                               pady=5)

    wireless_elapsed_label = tk.Label(wireless_tab, text="Elapsed Time: 0.0s",
                                      fg="#00FF00", bg="#000000",
                                      font=("Consolas", 12, "bold"))
    wireless_elapsed_label.grid(row=3, column=0, columnspan=2, pady=5)

    wireless_output_text = tk.Text(wireless_tab, height=20, width=90,
                                   fg="#00FF00", bg="#000000",
                                   font=("Consolas", 11, "bold"),
                                   insertbackground="#00FF00")
    wireless_output_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
    wireless_output_text.config(state=tk.DISABLED)

    # Chatbot Tab
    chatbot_tab = ttk.Frame(tab_control)
    tab_control.add(chatbot_tab, text="Chatbot")

    chatbot_output = tk.Text(chatbot_tab, height=20, width=90, fg="#00FF00",
                             bg="#000000", font=("Consolas", 11, "bold"),
                             insertbackground="#00FF00")
    chatbot_output.grid(row=0, column=0, padx=5, pady=5)

    chatbot_input = tk.Entry(chatbot_tab, width=90,
                             font=("Consolas", 12, "bold"),
                             fg="#00FF00", bg="#000000",
                             insertbackground="#00FF00")
    chatbot_input.grid(row=1, column=0, padx=5, pady=5)
    chatbot_input.bind("<Return>", lambda event: process_chat_input(
        chatbot_input, chatbot_output
    ))

    # AR Visualization Tab
    ar_tab = ttk.Frame(tab_control)
    tab_control.add(ar_tab, text="AR Visualization")

    ar_label = tk.Label(ar_tab, text="AR Network Visualization Placeholder",
                        fg="#00FF00", bg="#000000",
                        font=("Consolas", 14, "bold"))
    ar_label.pack(padx=10, pady=10)

    ar_start_button = tk.Button(ar_tab, text="Start AR Visualization",
                                command=start_ar_visualization,
                                bg="#004400", fg="#00FF00",
                                font=("Consolas", 14, "bold"))
    ar_start_button.pack(pady=10)

    # Additional UI/UX polish: add hover effects and tooltips for buttons
    for btn in [port_scan_button, wireless_attack_button, ar_start_button]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # Auto-fill local IP in target fields
    local_ip = get_local_ip()
    port_target_entry.insert(0, local_ip)
    wireless_target_entry.insert(0, local_ip)

    root.mainloop()
