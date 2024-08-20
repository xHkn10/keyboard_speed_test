import os
import sys
import time
import tkinter as tk
from threading import Thread

import customtkinter as ctk
import numpy as np

random_ints = list()


class App(ctk.CTk):
    TIME_seconds = 60
    ROWS = 5
    COLS = 8

    root = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("Klavye Hiz Testi")
        self.geometry("1000x500")
        self.protocol("WM_DELETE_WINDOW", sys.exit)

        App.root = self

        score_board = ScoreBoard(self)
        words_frame = ctk.CTkFrame(self, width=700, height=400)
        Display(words_frame, MyWords.word_list)
        bar = EntryBar(self)

        words_frame.pack()
        bar.pack(pady=8)
        score_board.pack()
        Timer(self).pack()

        self.mainloop()

    def destroy(self):
        self.destroy()


class EntryBar(ctk.CTkEntry):
    cur_pos = 0

    def __init__(self, master):
        super().__init__(master, font=("Ink Free", 20), width=300, height=30)

        self.bind("<space>", self.space_pressed)
        self.bind("<Key>", self.word_color_configure)
        self.bind("<Key>", Timer.start_time)

    def space_pressed(self, event):

        if self.cur_pos == App.ROWS * App.COLS - 1:
            PopUpWindow()
            return

        user_ent = self.get().strip()

        self.delete(0, tk.END)
        global random_ints
        if user_ent == MyWords.word_list[random_ints[self.cur_pos]]:
            ScoreBoard.correct_answers += 1
        else:
            ScoreBoard.wrong_answers += 1

        Display.labels[self.cur_pos].configure(text_color="white")
        self.cur_pos += 1
        Display.labels[self.cur_pos].configure(text_color="green")

        ScoreBoard.update_score()

    def word_color_configure(self, event):
        global random_ints
        if event.char.isalpha():
            curr_entry = self.get().strip() + event.char
        else:
            if event.keysym == "BackSpace":
                curr_entry = self.get().strip()[0:-1]
            else:
                curr_entry = self.get().strip()
        if curr_entry == MyWords.word_list[random_ints[self.cur_pos]][:len(curr_entry)]:
            Display.labels[self.cur_pos].configure(text_color="green")
        else:
            Display.labels[self.cur_pos].configure(text_color="red")


class MyWords:
    with open("words_in_turkish.csv", "r", encoding="utf-8") as file:
        word_list = file.read().split(" ")


class Display:
    labels = list()

    def __init__(self, words_frame: ctk.CTkFrame, word_list: list):
        global random_ints
        random_ints = np.random.randint(0, len(MyWords.word_list) - 1, App.COLS * App.ROWS)
        for i in random_ints:
            word_label = ctk.CTkLabel(words_frame, text=word_list[i], width=100, height=50, bg_color="#212a38",
                                      font=("Ink Free", 30))
            self.labels.append(word_label)

        for i in range(App.ROWS):
            for j in range(App.COLS):
                self.labels[i * App.COLS + j].grid(row=i, column=j)

        self.labels[0].configure(text_color="green")


class ScoreBoard(ctk.CTkFrame):
    correct_answers = 0
    wrong_answers = 0
    correct_label = None
    wrong_label = None

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._instance = self
        ScoreBoard.correct_label = ctk.CTkLabel(self, text="Dogru Cevaplar: 0", font=("Ink Free", 50, "bold"),
                                                fg_color="green", bg_color="black")
        ScoreBoard.wrong_label = ctk.CTkLabel(self, text="Yanlis Cevaplar: 0", font=("Ink Free", 50, "bold"),
                                              fg_color="red", bg_color="black")
        self.correct_label.pack()
        self.wrong_label.pack()

    @classmethod
    def update_score(cls):
        cls.correct_label.configure(text=f"Dogru Cevaplar: {cls.correct_answers}")
        cls.wrong_label.configure(text=f"Yanlis Cevaplar: {cls.wrong_answers}")


class Timer(ctk.CTkLabel):
    remaining_time = None
    timer_obj = None

    def __init__(self, master, **kwargs):
        super().__init__(master, text=str(App.TIME_seconds), font=("Ink Free", 40), **kwargs)
        Timer.timer_obj = self
        self.pack(side="right")

    @classmethod
    def start_time(cls, event):
        if cls.remaining_time is None:
            cls.remaining_time = App.TIME_seconds
            time_thread = Thread(target=cls.thread_timer)
            time_thread.start()

    @classmethod
    def thread_timer(cls):
        while cls.remaining_time > 0:
            time.sleep(1)
            cls.remaining_time -= 1
            try:
                cls.timer_obj.configure(text=str(cls.remaining_time))
            except RuntimeError:
                sys.exit()
            if cls.remaining_time == 0:
                PopUpWindow()


class PopUpWindow(ctk.CTkToplevel):
    pop_obj = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PopUpWindow.pop_obj = self
        self.title("Süren BİTTİ!")
        self.geometry("300x200")
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        App.root.withdraw()

        pop_message = f"Dakika başı \n {int(ScoreBoard.correct_answers / ((App.TIME_seconds - Timer.remaining_time) / 60))} kelime!" if Timer.remaining_time is not None else "Dakika başı \n 0 kelime!"

        (ctk.CTkLabel(master=self, pady=20, font=("Ink Free", 40), text_color="blue", bg_color="transparent",
                      text=pop_message)
         .pack())
        ctk.CTkButton(master=self, font=("Ink Free", 20), text_color="black", bg_color="transparent", corner_radius=15,
                      text="Çıkış", command=exit_program).pack()
        ctk.CTkButton(master=self, font=("Ink Free", 20), text_color="black", bg_color="transparent", corner_radius=15,
                      text="Tekrar Dene", command=relaunch_program).pack()
        self.focus()


def relaunch_program():
    PopUpWindow.pop_obj.destroy()
    os.system("python KlavyeHizTesti.py")
    sys.exit()


def exit_program():
    sys.exit()


def main():
    App()


if __name__ == "__main__":
    main()
