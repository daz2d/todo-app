import subprocess
import unittest

class TestLogViewer(unittest.TestCase):
    def test_help_command(self):
        result = subprocess.run(['python', 'src/app.py', '--help'], capture_output=True, text=True)
        self.assertIn('usage:', result.stdout)

    def test_invalid_command(self):
        result = subprocess.run(['python', 'src/app.py', '--invalid'], capture_output=True, text=True)
        self.assertIn('error:', result.stderr)

    def test_log_path_specification(self):
        result = subprocess.run(['python', 'src/app.py', '--log-path', '/path/to/logfile'], capture_output=True, text=True)
        self.assertIn('Log file specified: /path/to/logfile', result.stdout)

if __name__ == '__main__':
    unittest.main()