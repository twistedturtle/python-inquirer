import inquirer.themes as themes
from inquirer.render.console import ConsoleRender

import signal

def prompt(questions, render=None, answers=None, theme=themes.Default(), raise_keyboard_interrupt=False, raise_sigint=True):
    render = render or ConsoleRender(theme=theme)
    answers = answers or {}

    try:
        for question in questions:
            answers[question.name] = render.render(question, answers)
        return answers
    except KeyboardInterrupt:
        if raise_keyboard_interrupt:
            raise
        if raise_sigint:
            signal.raise_signal(signal.SIGINT)
        print("")
        print("Cancelled by user")
        print("")
