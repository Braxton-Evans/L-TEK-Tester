import tkinter as tk
import win32gui
import win32con
import win32api
from pywinusb import hid

# Main GUI and canvas settings:
pad_gui = tk.Tk()
pad_gui.title("L-TEK Tester")
canvas = tk.Canvas(pad_gui, bg="#000")  # Black background for max contrast
canvas.pack(fill=tk.BOTH, expand=True)

# Helper method to default the Tester to the LHS of the monitor
def snap_left(width, height):
    hwnd = win32gui.GetForegroundWindow()
    win32gui.MoveWindow(hwnd, -6, 0, width + 14, height + 8, True)

# Initial position of tool - left half of main monitor
left, top, right, bottom = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))['Work']
usable_width = right - left
usable_height = bottom - top
window_w = usable_width // 2
window_h = usable_height
pad_gui.geometry(f"{window_w}x{window_h}+0+0")
pad_gui.update_idletasks()
pad_gui.update()
snap_left(window_w, window_h)

# Textbox & methods for logging (positioned during resize):
log_text = tk.Text(
    canvas,
    bg="#111",
    fg="white",
    font=("Consolas", 10),
    wrap=tk.WORD,
    borderwidth=0,        # Removes 3D border
    highlightthickness=0  # Removes focus highlight ring
)
log_text.config(state=tk.DISABLED)
log_text.tag_config("error", foreground="red")
log_text_id = None
def log(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + "\n")
    log_text.config(state=tk.DISABLED)
def logErr(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + "\n", "error")
    log_text.config(state=tk.DISABLED)

# Create arrow shapes with dummy coords - they'll be positioned later
arrows = {}
# Bitmask mapping: byte[1]
ARROW_BITS = {
    0: "Left",
    1: "Right",
    2: "Up",
    3: "Down"
}
for name in ARROW_BITS.values():
    arrows[name] = canvas.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, outline="white", width=3)

# Main resizing method
def resize(event):
    # Get the new dimensions
    w, h = event.width, event.height
    panel_w, panel_h = w // 3, h // 3

    # Redraw the basic 3x3 dance panels
    canvas.delete("panels")
    for row in range(3):
        for col in range(3):
            x1 = col * panel_w
            y1 = row * panel_h
            x2 = x1 + panel_w
            y2 = y1 + panel_h
            # Determine if this is a corner panel
            is_corner = (row in (0, 2) and col in (0, 2))
            if is_corner:
                canvas.create_rectangle(x1, y1, x2, y2, outline="#444", fill="#111", width=2, tags="panels")
            else:
                canvas.create_rectangle(x1, y1, x2, y2, outline="#444", width=2, tags="panels")

    # Position the log_text widget in the center panel
    global log_text_id
    # Calculate center panel bounds
    panel_w, panel_h = w // 3, h // 3
    center_x = w // 2 - 1
    center_y = h // 2 - 1
    panel_x1 = panel_w
    panel_y1 = panel_h
    panel_x2 = panel_x1 + panel_w
    panel_y2 = panel_y1 + panel_h
    panel_width = panel_x2 - panel_x1 - 2
    panel_height = panel_y2 - panel_y1 - 2
    # Create or update the embedded log window
    if log_text_id:
        canvas.coords(log_text_id, center_x, center_y)
        canvas.itemconfig(log_text_id, width=panel_width, height=panel_height)
    else:
        log_text_id = canvas.create_window(center_x, center_y, window=log_text, width=panel_width, height=panel_height)

    # Define the positions of each arrow to be redrawn (the center of each panel)
    positions = {
        "Left": (panel_w//2, h//2),
        "Right": (w - panel_w//2, h//2),
        "Up": (w//2, panel_h//2),
        "Down": (w//2, h - panel_h//2)
    }

    # Redraw each arrow in each position
    for name, (cx, cy) in positions.items():
        half_w = panel_w * 0.45
        half_h = panel_h * 0.45
        if name == "Left":
            vertices = [
                cx - half_w, cy,            # Tip (left center)
                cx + half_w, cy - half_h,   # Top right corner
                cx + half_w * 0.5, cy,      # Right center notch
                cx + half_w, cy + half_h    # Bottom right corner
            ]
        elif name == "Right":
            vertices = [
                cx + half_w, cy,            # Tip (right center)
                cx - half_w, cy - half_h,   # Top left corner
                cx - half_w * 0.5, cy,      # Left center notch
                cx - half_w, cy + half_h    # Bottom left corner
            ]
        elif name == "Up":
            vertices = [
                cx, cy - half_h,            # Tip (top center)
                cx + half_w, cy + half_h,   # Bottom right corner
                cx, cy + half_h * 0.5,      # Bottom center notch
                cx - half_w, cy + half_h    # Bottom left corner
            ]
        elif name == "Down":
            vertices = [
                cx, cy + half_h,            # Tip (bottom center)
                cx + half_w, cy - half_h,   # Top right corner
                cx, cy - half_h * 0.5,      # Top center notch
                cx - half_w, cy - half_h    # Top left corner
            ]
        canvas.coords(arrows[name], *vertices) # * is the unpacking operator

# Bind "resize" method to canvas "<Configure>" event
canvas.bind("<Configure>", resize)

# Helper method for handling the input from the L-TEK pad:
prev_inputs = None
def handle_input(inputs):
    global prev_inputs
    if inputs == prev_inputs:
        return
    prev_inputs = inputs
    byte = inputs[1] # We only care about the middle byte of inputs: <#, byte, #>
    for bit, name in ARROW_BITS.items():
        color = "cyan" if byte & (1 << bit) else "#111"
        canvas.itemconfig(arrows[name], fill=color)

# Search the current "HID" devices for any "L-TEK"(s)
lteks = []
groupedDevices = {}
for d in hid.HidDeviceFilter().get_devices():
    key = (d.vendor_id, d.product_id, getattr(d, 'serial_number', None))
    if "L-TEK" in d.product_name.upper():
        lteks.append(d)
    elif key not in groupedDevices:
        groupedDevices[key] = {
            "name": d.product_name,
            "vendor_id": hex(d.vendor_id),
            "product_id": hex(d.product_id),
            "serial": getattr(d, 'serial_number', None),
            "count": 1
        }
    else:
        groupedDevices[key]["count"] += 1

# Handle L-TEK detection
if len(lteks) == 0:
    logErr("No L-TEK detected.\n")
    log("Devices detected:\n")
    for dev in groupedDevices.values():
        log(f" - {dev['count']} x {dev['name']}:")
        log(f"   VendorID: {dev['vendor_id']}, ProductID: {dev['product_id']}")
        if dev["serial"]:
            log(f"   Serial: {dev['serial']}")
elif len(lteks) > 1:
    logErr(f"Warning: {len(lteks)} L-TEK pads detected.\nOnly one will be used.\n")

# Proceed with first L-TEK if available
if lteks:
    device = lteks[0]
    device.open()
    device.set_raw_data_handler(handle_input)

# Start the Tester
pad_gui.mainloop()