from interpreter_r1 import interpret

def run_sea_trial():
    test_input = "stabilize luminous threads in the chamber"
    result = interpret(test_input)

    print("INPUT:", test_input)
    print("INTERPRETED:", result)

if __name__ == "__main__":
    run_sea_trial()
