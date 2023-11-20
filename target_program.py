# target_program.py

def target_program(input_data):
    """
    Example target program for fuzzing.
    
    Parameters:
    - input_data: The input data to be provided to the target program.

    Returns:
    - The result of running the target program.
    """
    if "bug" in input_data:
        raise ValueError("Bug detected!")
    return len(input_data)

# Example of using the target program
if __name__ == "__main__":
    input_data = "hello"
    try:
        result = target_program(input_data)
        print(f"Result: {result}")
    except ValueError as e:
        print(f"Error: {e}")

