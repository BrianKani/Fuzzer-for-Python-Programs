from fuzzingbook import GreyboxFuzzer as gbf
from fuzzingbook import Coverage as cv
from fuzzingbook import MutationFuzzer as mf
import random

import subprocess
import sys

import traceback
import numpy as np
import time

from bug import entrypoint
from bug import get_initial_corpus

class MyCoverage(cv.Coverage):
    def __init__(self):
        self.executed_lines = set()
        self.covered_lines = set()
    def update(self, covered_lines):
        # Ensure the variable is properly defined
        if covered_lines is not None:
            # Update the covered lines based on the provided set
            self.covered_lines.update(covered_lines)


    def coverage(self): 
        coverage_data = {
            'lines': [1, 5, 10, 15],  
            'branches': {'block_1': True, 'block_2': False},  
            'functions': ['function_1', 'function_2']  
        }

        return {
            'lines': list(self.executed_lines),
            'branches': {},  
            'functions': []  
        }

    def trace_callback(self, frame, event, arg):
      
        if event == 'line':
            # Record the executed line number
            line_number = frame.f_lineno
            self.executed_lines.add(line_number)

        return self.trace_callback
    
class MyRunner:
    def __init__(self, target_function):
        self.target_function = target_function
        self._coverage = None  # Use _coverage as a private attribute

    def run_function(self, input_data):
        try:
            result = self.target_function(input_data)
            return result
        except Exception as e:
            return e

    def coverage(self):
        return self._coverage  # Use _coverage as a private attribute

    def run_with_coverage(self, input_data):
        self._coverage = self.calculate_coverage(input_data)
        return self.run_function(input_data)

    def calculate_coverage(self, input_data):
        self.covered_lines = set()

        sys.settrace(self.trace_callback)

        try:
            self.run_function(input_data)
        finally:
            sys.settrace(None)

        return {'lines': list(self.covered_lines)}

    def trace_callback(self, frame, event, arg):
        if event == 'line':
            line_number = frame.f_lineno
            self.covered_lines.add(line_number)
        return self.trace_callback

class MyFuzzer(gbf.CountingGreyboxFuzzer):
    def __init__(self, corpus, mutator, schedule, max_trials=1000):
        super().__init__(corpus, mutator, schedule)
        self.max_trials = max_trials
        self.corpus = corpus 
        self.coverage = MyCoverage()
        self.input_count = 0 

    def reset(self):
        self.current_iteration = 0  

    def update_coverage(self, coverage_data):
        # Ensure that covered_lines is defined
        covered_lines = set(coverage_data.get('lines', [])) if coverage_data else set()

        # Update your fuzzer's coverage information based on the covered lines
        self.coverage.update(covered_lines)

    def reset(self):
        self.current_iteration = 0

    def calculate_coverage(self, input_data):
        # Initialize self.covered_lines
        self.covered_lines = set()

        sys.settrace(self.trace_callback)

        try:
            # Run the target function with the input data
            self.run_function(input_data)
        finally:
            # Disable the trace
            sys.settrace(None)

        return {'lines': list(self.covered_lines)}


    def update_stats(self):
        # Increment the input count each time an input is generated
        self.input_count += 1
        print(f"Generated {self.input_count} inputs")

    def run(self, runner: MyRunner):
        for i in range(self.max_trials):
            self.reset()

            input_data = self.mutator.mutate(self.select_input())

            # Run the target program with the generated input
            result = runner.run_function(input_data)

            self.update_coverage(runner.coverage())

            if self.is_bug(result):
                self.handle_bug(input_data, result)

            self.update_stats()
            self.update_schedule()

    def update_schedule(self):
        # Increment the current iteration
        self.current_iteration += 1
        print(f"Updated schedule. Current iteration: {self.current_iteration}")
    

    def select_input(self):
        """
        Select an input from the corpus or generate a new one.
        """
        if not self.corpus:
            # If the corpus is empty, generate a new input
            return self.mutator.generate_input()
        else:
            # Select an input from the corpus
            return random.choice(self.corpus)

    def is_bug(self, result):
        if isinstance(result, Exception) and "bug_detected" in str(result):
            return True
        return False

    def handle_bug(self, input_data, result):
        """
        Handle the bug found during fuzzing.
        You can customize this method to log the bug, save the input, or perform any other actions.
        """
        bug_message = str(result)
        with open("bugs.log", "a") as log_file:
            log_file.write(f"Bug found: {bug_message}\n")
        # Save the input that triggered the bug
        with open(f"bug_input_{self.total_inputs}.txt", "w") as input_file:
            input_file.write(str(input_data))


if __name__ == "__main__":
    seed_inputs = get_initial_corpus()

    my_coverage = MyCoverage()
    my_runner = MyRunner(entrypoint)
    my_fuzzer = MyFuzzer(seed_inputs, gbf.Mutator(), gbf.AFLFastSchedule(5))

    my_fuzzer.runs(my_runner, trials=999999999)


def trace_callback(self, frame, event, arg):
    if event == 'line':
        line_number = frame.f_lineno
        self.covered_lines.add(line_number)

    return self.trace_callback
