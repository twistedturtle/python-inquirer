import inspect
import signal
import sys
from typing import Optional
from typing import Union

import inquirer
from inquirer.questions import Question
from inquirer.render.console import ConsoleRender as CR
from inquirer.themes import Default


# This is in case raise_sigint is True but the
# signal isn't handled in the parent software
# parent handler will override
def signal_handler(sig, frame):
    sys.exit(1)


signal.signal(signal.SIGINT, signal_handler)


def prompt(
    questions: Optional[Union[Question, list[Question]]] = None,
    render: Union[CR, type[CR]] = CR,
    answers: Optional[dict] = None,
    theme: Union[Default, type[Default]] = Default(),
    raise_keyboard_interrupt: bool = False,
    raise_sigint: Optional[bool] = None,
    int_msg: bool = True,
    message: str = "Do you want to continue?",
    **kwargs
):
    answers = answers or {}

    if inspect.isclass(theme):
        theme = theme()

    if inspect.isclass(render):
        render = render(theme=theme)

    single = False
    if questions is None:
        single = True
        questions = [inquirer.Confirm("confirm", message=message, **kwargs)]

    if not isinstance(questions, list):
        single = True
        questions = [questions]

    try:
        for question in questions:
            answers[question.name] = render.render(question, answers)
        if single:
            return answers[question.name]
        return answers
    except KeyboardInterrupt:
        if int_msg:
            print("\033[K" + theme.Question.int_msg)
        if raise_sigint:
            signal.raise_signal(signal.SIGINT)
        if raise_keyboard_interrupt:
            raise

