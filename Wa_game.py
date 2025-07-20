import streamlit as st
import random
from typing import List


# =======================
# Wordle Logic
# =======================
class WordleGame:
    def __init__(self, word_list: List[str]):
        self.word_list = word_list
        self.target = random.choice(self.word_list)
        self.max_attempts = 6
        self.attempts = []
        self.status = "IN_PROGRESS"

    def guess(self, word: str):
        if self.status != "IN_PROGRESS":
            return

        word = word.lower()
        feedback = self.get_feedback(word)
        self.attempts.append((word, feedback))

        if word == self.target:
            self.status = "WON"
        elif len(self.attempts) >= self.max_attempts:
            self.status = "LOST"

    def get_feedback(self, guess: str) -> List[str]:
        feedback = ["gray"] * 5
        target_chars = list(self.target)
        guess_chars = list(guess)

        # First pass - green
        for i in range(5):
            if guess_chars[i] == target_chars[i]:
                feedback[i] = "green"
                target_chars[i] = None

        # Second pass - yellow
        for i in range(5):
            if feedback[i] == "gray" and guess_chars[i] in target_chars:
                feedback[i] = "yellow"
                target_chars[target_chars.index(guess_chars[i])] = None

        return feedback


# =======================
# Utilities
# =======================
@st.cache_data
def load_words():
    with open("words.txt", "r") as f:
        return [line.strip() for line in f if len(line.strip()) == 5]


def display_attempts(attempts):
    for word, feedback in attempts:
        cols = st.columns(5)
        for i, letter in enumerate(word):
            bg_color = {"green": "#6aaa64", "yellow": "#c9b458", "gray": "#787c7e"}[feedback[i]]
            cols[i].markdown(
                f"<div style='background-color:{bg_color}; color:white; padding:10px; text-align:center; border-radius:5px; font-weight:bold'>{letter.upper()}</div>",
                unsafe_allow_html=True,
            )


# =======================
# Streamlit App
# =======================
def main():
    st.set_page_config(page_title="Wordle Game", page_icon="🟩")
    st.title("🟩 Wordle Clone in Streamlit")

    word_list = load_words()

    if "game" not in st.session_state:
        st.session_state.game = WordleGame(word_list)

    game: WordleGame = st.session_state.game

    if game.status == "WON":
        st.success(f"🎉 You guessed the word: {game.target.upper()}!")
    elif game.status == "LOST":
        st.error(f"😢 You lost! The word was: {game.target.upper()}")
    else:
        st.info(f"Attempt {len(game.attempts)+1} of {game.max_attempts}")

    display_attempts(game.attempts)

    if game.status == "IN_PROGRESS":
        with st.form("guess_form", clear_on_submit=True):
            guess = st.text_input("Enter your 5-letter guess").strip().lower()
            submitted = st.form_submit_button("Submit")
            if submitted:
                if len(guess) != 5 or guess not in word_list:
                    st.warning("Invalid guess. Make sure it's a valid 5-letter word.")
                else:
                    game.guess(guess)

    if st.button("🔄 Restart Game"):
        st.session_state.game = WordleGame(word_list)
        st.experimental_rerun()


if __name__ == "__main__":
    main()
