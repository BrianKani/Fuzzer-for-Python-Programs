def target_program(input_data):
    """
    Example target program for fuzzing.
    
    Parameters:
    - input_data: The input data to be provided to the target program.

    Returns:
    - The result of running the target program.
    """
    # Assume the input data is a string representing a numeric value
    try:
        divisor = int(input_data)
        result = 10 / divisor  # Bug: Division by zero when divisor is 0
        return result
    except ValueError:
        raise ValueError("Invalid input. Please provide a numeric value.")
    except ZeroDivisionError:
        raise ValueError("Bug detected: Division by zero!")

# Example of using the target program
if __name__ == "__main__":
    input_data = "0"  # Simulating the bug by providing 0 as input
    try:
        result = target_program(input_data)
        print(f"Result: {result}")
    except ValueError as e:
        print(f"Error: {e}")