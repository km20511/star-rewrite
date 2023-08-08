# https://realpython.com/python-eval-function/#minimizing-the-security-issues-of-eval
class Test:
    def test1(self):
        return self
    def test2(self):
        return self

GLOBAL_INSTANCE = Test()

ALLOWED_NAMES = {
    "test": GLOBAL_INSTANCE,
    "test1": GLOBAL_INSTANCE.test1
}

def parse_input(text: str):
    code = compile(text, "<string>", "eval")
    print(f"debug: {code.co_names}")
    for name in code.co_names:
        if name not in ALLOWED_NAMES:
            raise NameError(f"The name {name} is not defined or is not allowed.")
    return eval(code, {"__builtins__": {}}, ALLOWED_NAMES)

def main():
    """Main loop: Read and evaluate user's input."""
    while True:
        # Read user's input
        try:
            expression = input("> ")
        except (KeyboardInterrupt, EOFError):
            raise SystemExit()

        if expression.lower() in {"quit", "exit"}:
            raise SystemExit()

        # Evaluate the expression and handle errors
        try:
            result = parse_input(expression)
        except SyntaxError:
            # If the user enters an invalid expression
            print("Invalid input expression syntax")
            continue
        except (NameError, ValueError) as err:
            # If the user tries to use a name that isn't allowed
            # or an invalid value for a given math function
            print(err)
            continue

        # Print the result if no error occurs
        print(f"The result is: {result}")

if __name__ == "__main__":
    main()