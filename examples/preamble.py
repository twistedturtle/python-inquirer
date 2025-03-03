from pprint import pprint


# sys.path.append(os.path.realpath("."))
import inquirer  # noqa


questions = [
    inquirer.List(
        "size",
        preamble="This will be shown before the question\n\n",
        message="What size do you need?",
        choices=["Jumbo", "Large", "Standard", "Medium", "Small", "Micro"],
    ),
]

answers = inquirer.prompt(questions)

pprint(answers)
