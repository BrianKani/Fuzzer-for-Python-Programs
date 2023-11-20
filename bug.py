def get_initial_corpus():
    return ["0", "fuzz", "42", "-1"]

i = 0

def entrypoint(s):
    global i
    i += 1
    if i > 100:
        exit(219)

    # Call the target_program with the input
    try:
        result = target_program(s)
        print(f"Result: {result}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure you have a diverse initial corpus for fuzzing
    initial_corpus = get_initial_corpus()

    # Fuzz the entrypoint function
    for input_str in initial_corpus:
        entrypoint(input_str)

