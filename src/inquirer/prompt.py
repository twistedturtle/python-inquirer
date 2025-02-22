import inquirer.themes as themes
from inquirer.render.console import ConsoleRender

import signal, sys

def signal_handler(sig, frame):
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

def prompt(questions, render=None, answers=None, theme=themes.Default(), raise_keyboard_interrupt=False, raise_sigint=True, int_msg=True):
    render = render or ConsoleRender(theme=theme)
    answers = answers or {}

    try:
        for question in questions:
            answers[question.name] = render.render(question, answers)
        return answers
    except KeyboardInterrupt:
        if int_msg:
            print(render.terminal.clear_eol() + theme.Question.int_msg)
        if raise_keyboard_interrupt:
            raise
        if raise_sigint:
            signal.raise_signal(signal.SIGINT)

