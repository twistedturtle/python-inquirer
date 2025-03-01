from blessed import Terminal

import inquirer


# Should be odd number as there is always one question selected
MAX_OPTIONS_DISPLAYED_AT_ONCE = 13
half_options = int((MAX_OPTIONS_DISPLAYED_AT_ONCE - 1) / 2)


class BaseConsoleRender:
    title_inline = False

    def __init__(self, question, theme=None, terminal=None, show_default=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        self.terminal = terminal or Terminal()
        self.answers = {}
        self.theme = theme
        self.show_default = show_default

    def _get_option(self, question_option, theme_option, default):
        if question_option:
            var = question_option
        elif theme_option:
            var = theme_option
        else:
            var = default
        return var

    def other_input(self):
        other = inquirer.text(self.question.message, autocomplete=self.question.autocomplete)
        return other

    def get_question(self):
        msg = self.get_header()

        if self.question.default and self.show_default:
            default_value = " ({color}{default}{normal})".format(
                default=self.question.default, color=self.theme.Question.default_color, normal=self.terminal.normal
            )
            msg += default_value

        t = self.terminal
        tq = self.theme.Question
        if self.theme.Question.prefix != None:
            msg_template = (
                f"{self.question._preamble}{tq.prefix}{t.normal}{msg}"
            )
        else:
            msg_template = (
                f"{self.question._preamble}{tq.brackets_color}[{tq.mark_color}?{tq.brackets_color}]{t.normal} {msg}"
            )

        return msg_template

    def get_escaped_current_value(self):
        ''' ensure any user input with { or } will not cause a formatting error '''
        return str(self.get_current_value()).replace("{", "{{").replace("}", "}}")

    def get_header(self):
        return self.question.message

    def get_hint(self):
        return ""

    def get_current_value(self):
        return ""

    def get_option_lines(self):
        return []

    def get_options(self):
        return []

    def process_input(self, pressed):
        raise NotImplementedError("Abstract")

    def handle_validation_error(self, error):
        if error.reason:
            return error.reason

        ret = f'"{error.value}" is not a valid {self.question.name}.'
        try:
            ret.format()
            return ret
        except (ValueError, KeyError):
            return f"Entered value is not a valid {self.question.name}."
