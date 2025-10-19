# L-TEK Tester

A lightweight, responsive input visualizer for L-TEK dance pads on Windows. Designed for rhythm game enthusiasts and hardware tinkerers, this tool provides real-time feedback on arrow presses with a clean 3×3 panel layout and embedded logging.

## Motivation

<table>
  <tr>
    <th style="text-align:center;">Sad:</th>
    <th style="text-align:center;">Happy:</th>
  </tr>
  <tr>
    <td style="text-align:center;">
      <img src="SetUpUSBGameControllers.png" alt="Windows USB Controller Setup" width="400">
    </td>
    <td style="text-align:center;">
      <img src="L-TEK Tester.png" alt="L-TEK Tester GUI" width="400">
    </td>
  </tr>
</table>

## Features

- 🎯 Real-time arrow input visualization (Left, Right, Up, Down)
- 🖥️ Auto-snaps to the left half of your primary monitor
- 🧠 Intelligent device detection with error/warning logging
- 🐾 Handles multiple L-TEKs gracefully (logs warning if >1 detected)
- 🧩 Embedded log panel for device info and diagnostics
- 🎨 Subtle UI polish with corner panel shading and arrow glow

## Requirements

- Windows OS
- Python 3.x
- `pywinusb` for HID input
- `pywin32` for window positioning

Install dependencies via:

```
pip install pywinusb pywin32
```

## Usage

Simply run the script:

```
python L-TEK-Tester.py
```

The tool will:
1. Detect connected L-TEK pads
2. Open a GUI window with a 3×3 panel layout
3. Highlight arrows in cyan when pressed
4. Log device info and warnings in the center panel

## Notes

- Only one L-TEK pad is used for input; others are listed but ignored
- If no L-TEK is detected, the tool logs all other HID devices for debugging
- GUI layout adapts to screen size and maintains pixel-perfect arrow placement

## License

The Unlicense

---

Built by [Braxton Evans](https://github.com/Braxton-Evans) for rhythm game testing and pad diagnostics.
