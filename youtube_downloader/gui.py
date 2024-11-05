from tkinter import *


def _get_temp_root():
    root = Tk()
    root.withdraw()
    root._temporary = True
    return root


class CustomDialog(Toplevel):
    def __init__(self, parent=_get_temp_root(), title='', message=''):
        super().__init__(parent)
        self.title(title)

        # Create a message label
        self.label = Label(self, text=message, padx=20, pady=20)
        self.label.pack()

        # Create the buttons
        self.button_frame = Frame(self)
        self.button_frame.pack(pady=(0, 20))

        self.button_video = Button(self.button_frame, text="Video", command=self.select_video, width=10)
        self.button_video.pack(side=LEFT, padx=10)

        self.button_audio = Button(self.button_frame, text="Audio", command=self.select_audio, width=10)
        self.button_audio.pack(side=LEFT, padx=10)

        # Center the dialog
        self.transient(parent)  # Keep dialog on top of the parent
        self.grab_set()         # Disable interaction with the parent until dialog is closed
        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle close button

        self.result = None  # Variable to store the result

    def select_video(self):
        self.result = "Video"
        self.destroy()  # Close the dialog

    def select_audio(self):
        self.result = "Audio"
        self.destroy()  # Close the dialog

    def on_close(self):
        self.result = None
        self.destroy()  # Close the dialog


def show_custom_dialog():
    dialog = CustomDialog("Select Option", "Please select an option:")
    # root.wait_window(dialog)  # Wait until the dialog is closed
    return dialog.result  # Return the result of the selection

show_custom_dialog()

# # Create the main application window
# root = tk.Tk()
# root.title("Custom Dialog Example")
#
# # Create a button to open the custom dialog
# open_dialog_button = tk.Button(root, text="Open Dialog", command=lambda: print(show_custom_dialog()))
# open_dialog_button.pack(pady=20)
#
# # Run the application
# root.mainloop()
