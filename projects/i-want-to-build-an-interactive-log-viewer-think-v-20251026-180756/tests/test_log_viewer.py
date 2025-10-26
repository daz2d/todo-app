import subprocess
import unittest

class TestLogViewer(unittest.TestCase):
    def test_help_command(self):
        result = subprocess.run(['python', 'src/main.py', '--help'], capture_output=True, text=True)
        self.assertIn('usage:', result.stdout)

    def test_invalid_command(self):
        result = subprocess.run(['python', 'src/main.py', '--invalid'], capture_output=True, text=True)
        self.assertIn('error:', result.stderr)

    def test_log_path_specification(self):
        result = subprocess.run(['python', 'src/main.py', '--log-path', '/path/to/logfile'], capture_output=True, text=True)
        self.assertIn('Specified log file: /path/to/logfile', result.stdout)

    def test_no_log_path(self):
        result = subprocess.run(['python', 'src/main.py'], capture_output=True, text=True)
        self.assertIn('No log file specified.', result.stdout)

if __name__ == '__main__':
    unittest.main()