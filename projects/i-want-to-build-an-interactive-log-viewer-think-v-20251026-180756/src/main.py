import argparse
import sys

class LogViewer:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Interactive Log Viewer')
        self.parser.add_argument('--log-path', type=str, help='Path to the log file')
        self.args = self.parser.parse_args()

    def run(self):
        if self.args.log_path:
            print(f'Specified log file: {self.args.log_path}')
        else:
            print('No log file specified. Use --log-path to specify a log file.')

        print(self.parser.format_help())

if __name__ == '__main__':
    viewer = LogViewer()
    viewer.run()