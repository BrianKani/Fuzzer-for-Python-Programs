from fuzzingbook import GreyboxFuzzer as gbf
from fuzzingbook import Coverage as cv
import random
import sys
from bug import entrypoint, get_initial_corpus

class MyCoverage(cv.Coverage):
    def __init__(self):
        super().__init__()
        self.executed_lines = set()

    def update(self, covered_lines):
        if covered_lines is not None:
            self.executed_lines.update(covered_lines)

    def coverage(self):
        return {
            'lines': list(self.executed_lines),
            'branches': {},
            'functions': []
        }

    def trace_callback(self, frame, event, arg):
        if event == 'line':
            line_number = frame.f_lineno
            self.executed_lines.add(line_number)

        return self.trace_callback

class MyRunner:
    def __init__(self, target_function):
        self.target_function = target_function
        self._coverage = None

    def run_function(self, input_data):
        try:
            result = self.target_function(input_data)
            return result
        except Exception as e:
            return e

    def coverage(self):
        return self._coverage

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
        covered_lines = set(coverage_data.get('lines', [])) if coverage_data else set()
        self.coverage.update(covered_lines)

    def calculate_coverage(self, input_data):
        self.covered_lines = set()

        sys.settrace(self.trace_callback)

        try:
            self.run_function(input_data)
        finally:
            sys.settrace(None)

        return {'lines': list(self.covered_lines)}

    def update_stats(self):
        self.input_count += 1
        print(f"Generated {self.input_count} inputs")

    def run(self, runner: MyRunner):
        for i in range(self.max_trials):
            self.reset()

            input_data = self.mutator.mutate(self.select_input())

            result = runner.run_function(input_data)

            self.update_coverage(runner.coverage())

            if self.is_bug(result):
                self.handle_bug(input_data, result)

            self.update_stats()
            self.update_schedule()

    def update_schedule(self):
        self.current_iteration += 1
        print(f"Updated schedule. Current iteration: {self.current_iteration}")

    def select_input(self):
        if not self.corpus:
            return self.mutator.generate_input()
        else:
            return random.choice(self.corpus)

    def is_bug(self, result):
        if isinstance(result, Exception) and "bug_detected" in str(result):
            return True
        return False

    def handle_bug(self, input_data, result):
        bug_message = str(result)
        with open("bugs.log", "a") as log_file:
            log_file.write(f"Bug found: {bug_message}\n")
        with open(f"bug_input_{self.input_count}.txt", "w") as input_file:
            input_file.write(str(input_data))

# Trace callback method outside the classes
def trace_callback(self, frame, event, arg):
    if event == 'line':
        line_number = frame.f_lineno
        self.covered_lines.add(line_number)

    return self.trace_callback

# Include the corrected trace_callback method in MyCoverage and MyRunner classes
MyCoverage.trace_callback = trace_callback
MyRunner.trace_callback = trace_callback

if __name__ == "__main__":
    # Ensure you have a diverse initial corpus for fuzzing
    initial_corpus = get_initial_corpus()

    # Fuzz the entrypoint function using the fuzzer
    my_coverage = MyCoverage()
    my_runner = MyRunner(entrypoint)
    my_fuzzer = MyFuzzer(initial_corpus, gbf.Mutator(), gbf.AFLFastSchedule(5))

    my_fuzzer.runs(my_runner, trials=999999999)