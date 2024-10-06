from tkinter import *
import tkinter as tk
from tkinter import scrolledtext as st
from passage import random_passage

MAIN_BG = "#fec89a"
FRAME_BG = "#f8edeb"
TEXT_AREA_BG = "#d8e2dc"
PASSAGE_TEXT_COLOR = "#8d99ae"
INPUT_AREA_BG = "#f8edeb"
TITLE_COLOR = "#03045E"
BUTTON_BG = "#006d77"
LOGO_FONT = ("Faster One", 25)
DEFAULT_TIME = 60  # sec

PASSAGE = random_passage
EXCLUDED_KEYS = ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Caps_Lock', 'Space', 'BackSpace']


class GUI:
    def __init__(self):
        self.cpm = 0
        self.wpm = 0
        self.duration = DEFAULT_TIME

        self.root = tk.Tk()
        self.root.geometry("1000x600")
        self.root.configure(background=MAIN_BG)
        self.root.title("Typing Speed Test")

        # Main title widget
        self.label = Label(self.root, text="Typing Speed Test",
                           font=LOGO_FONT,
                           background=MAIN_BG,
                           foreground=TITLE_COLOR,
                           pady=40)
        self.label.pack()

        # Frame widget to hold cpm and wpm horizontally
        self.frame = Frame(self.root, background=FRAME_BG)
        self.frame.pack()

        self.cpm_label = Label(self.frame, text="CPM :", background=FRAME_BG)
        self.cpm_label.pack(side=LEFT, padx=10)

        self.cpm_value = Label(self.frame, text=self.cpm, background="white", width=5)
        self.cpm_value.pack(side=LEFT)

        self.wpm_label = Label(self.frame, text="WPM :", background=FRAME_BG)
        self.wpm_label.pack(side=LEFT, padx=10)

        self.wpm_value = Label(self.frame, text=self.wpm, background="white", width=5)
        self.wpm_value.pack(side=LEFT)

        # Frame widget to hold time counter
        self.time_frame = Frame(self.root, background=FRAME_BG)
        self.time_frame.pack(pady=15)

        self.time_label = Label(self.time_frame, text="Time Remaining :", background=FRAME_BG)
        self.time_label.pack(side=LEFT, padx=20)

        self.remaining_time = Label(self.time_frame, text=f"{self.duration} sec", background="white", width=8)
        self.remaining_time.pack(side=LEFT)

        # Text widget for Passage
        self.passage = st.ScrolledText(self.root,
                                       height=3,
                                       width=40,
                                       font=("Montserrat", 25),
                                       background=TEXT_AREA_BG,
                                       foreground=PASSAGE_TEXT_COLOR,
                                       pady=20,
                                       padx=20)
        self.passage.insert('1.0', PASSAGE)
        self.passage.configure(state='disabled')
        self.passage.pack(pady=30)

        # Title for typing area
        self.sub_label = Label(self.root, text="Type the words below",
                               font=("Montserrat", 12),
                               background=MAIN_BG,
                               foreground=TITLE_COLOR,
                               pady=3)
        self.sub_label.pack()

        self.typed_word = StringVar()
        self.typed_word.set("")

        # Input text
        self.entry = Entry(self.root, font=("Montserrat", 25), textvariable=self.typed_word, background=INPUT_AREA_BG,
                           justify="center")
        self.entry.pack(pady=10)

        #  Message widget to be shown for Result
        self.message = Text(self.root,
                            height=3,
                            width=58,
                            font=("Montserrat", 11, "normal"),
                            background=MAIN_BG,
                            foreground="#272b36",
                            pady=20,
                            padx=20,
                            borderwidth=0)

        self.restart_button = Button(self.root,
                                     text="Try Again",
                                     font=("Montserrat", 14, "normal"),
                                     background=BUTTON_BG,
                                     foreground="white",
                                     width=15)

        self.content_index = 0  # Index to get the character from passage
        self.start_pos = 1.0
        self.line_number = 1  # Line number in the Passage
        self.col_number = 0  # Column number in the Passage
        self.timer()  # Call timer function to start countdown
        self.right_typed_char = True  # Check if a character is typed correctly
        self.total_passage_words = len(PASSAGE.split(" "))

    def on_key_release(self, event):
        if event.keysym in EXCLUDED_KEYS:
            return
        char_list = list(self.entry.get())  # Convert typed word into chars list
        if len(char_list) >= 1:
            char = char_list[-1]
        else:
            return
        self.update_test_text(char)

    def update_test_text(self, input_char):

        start_index = f"{self.line_number}.{self.col_number}"  # Current character index
        end_index = f"{self.line_number}.{self.col_number + 1}"  # Next character index

        # Remove any previous tags for character
        self.remove_all_tags_in_range(start=start_index, end=end_index)

        content = self.passage.get(1.0, "end")
        try:
            if content[self.content_index] == input_char:
                self.right_typed_char = True
                self.add_tag(tag_name="typed", start=start_index, end=end_index, color="#386641")
                if input_char != " ":
                    self.cpm += 1
            else:
                self.right_typed_char = False
                self.add_tag(tag_name="wrong_typed", start=start_index, end=end_index, color="#9a031e")

            self.incrementer()
        except IndexError:
            self.calculate_wpm()
            self.show_score()
            return

    def incrementer(self):
        self.content_index += 1
        self.col_number = self.content_index

        line = self.passage.get(f"{self.line_number}.0", f"{self.line_number}.end")
        if self.col_number > len(line):
            self.line_number += 1
            self.scroll_one_line(unit=1)

    def on_space_press(self, event):
        self.typed_word.set("")
        # Get the total length of the passage
        passage_length = len(PASSAGE)

        if self.content_index >= passage_length - 1:
            # If the space is pressed after the last index, show the result
            self.calculate_wpm()
            self.show_score()
            return
        self.incrementer()
        return "break"

    def on_backspace_press(self, event):
        self.content_index -= 1

        if self.col_number == 0 and self.line_number > 1:
            self.line_number -= 1
            line = self.passage.get(f"{self.line_number}.0", f"{self.line_number}.end")
            self.col_number = len(line)
            self.scroll_one_line(unit=-1)  # scroll up one line
        else:
            self.col_number = self.content_index

        self.remove_all_tags_in_range(start=f"{self.line_number}.{self.col_number}",
                                      end=f"{self.line_number}.{self.col_number + 1}")

        if self.right_typed_char:
            self.cpm -= 1

        return

    def add_tag(self, tag_name, start, end, color):
        self.passage.tag_add(tag_name, start, end)
        self.passage.tag_config(tag_name, foreground=color)

    def remove_all_tags_in_range(self, start, end):
        tags = self.passage.tag_names(start)

        for tag in tags:
            self.passage.tag_remove(tag, start, end)

    def scroll_one_line(self, unit):
        # Enable the text widget temporarily to allow scrolling
        self.passage.configure(state='normal')

        # Scroll by 1 line
        self.passage.yview_scroll(unit, 'units')

        # Disable the text widget again
        self.passage.configure(state='disabled')

    def timer(self):
        if self.duration > 0:
            self.duration -= 1
            self.remaining_time.configure(text=f"{self.duration} sec")
            self.root.after(1000, self.timer)
        elif self.duration == 0:
            self.calculate_wpm()
            self.show_score()
            return

    def show_score(self):
        self.passage.pack_forget()
        self.sub_label.pack_forget()
        self.entry.pack_forget()
        self.time_frame.pack_forget()

        self.label.configure(text="Typing Speed Test\nResult")

        self.config_cpm_wpm(font_size=25)

        self.message.insert(1.0, f"You achieved a CPM of '{self.cpm}' and a WPM of '{self.wpm}'. "
                                 f"With more practice, you can improve even further. After all, practice makes "
                                 f"perfect! Ready to try again?")
        self.message.configure(state='disabled')
        self.message.pack()

        self.restart_button.pack()

        return

    def restart(self):
        self.message.pack_forget()
        self.restart_button.pack_forget()

        self.duration = DEFAULT_TIME
        self.timer()
        self.label.configure(text="Typing Speed Test")
        self.config_cpm_wpm(9)
        self.time_frame.pack()
        self.passage.pack(pady=30)
        self.sub_label.pack()
        self.entry.delete(0, tk.END)
        self.entry.pack()

    def config_cpm_wpm(self, font_size):
        self.cpm_label.configure(font=("Montserrat", font_size))

        self.cpm_value.configure(text=self.cpm, font=("Montserrat", font_size))

        self.wpm_label.configure(font=("Montserrat", font_size))

        self.wpm_value.configure(text=self.wpm, font=("Montserrat", font_size))
        if font_size > 20:
            self.frame.pack(pady=30)
        else:
            self.frame.pack(pady=15)

    def calculate_wpm(self):
        time_in_sec = 60 - self.duration
        time_in_min = time_in_sec/60

        if time_in_min == 0:
            self.wpm = 0
        else:
            self.wpm = round((self.cpm / 5) / time_in_min, 1)