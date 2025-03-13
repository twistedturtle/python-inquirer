import inquirer.themes as themes
from inquirer.render.console import ConsoleRender


import signal
import sys
import inspect


def signal_handler(sig, frame):
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)


def prompt(
    questions,
    render=ConsoleRender,
    answers={},
    theme=themes.Default(),
    raise_keyboard_interrupt=False,
    raise_sigint=False,
    int_msg=True,
):
    if inspect.isclass(theme):
        theme = theme()

    if inspect.isclass(render):
        render = render(theme=theme)

    try:
        for question in questions:
            answers[question.name] = render.render(question, answers)
        return answers
    except KeyboardInterrupt:
        if int_msg:
            print("\033[K" + theme.Question.int_msg)
        if raise_keyboard_interrupt:
            raise
        if raise_sigint:
            signal.raise_signal(signal.SIGINT)
