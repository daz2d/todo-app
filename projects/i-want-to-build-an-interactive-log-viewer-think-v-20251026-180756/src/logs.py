class LogEntry:
    def __init__(self, timestamp, level, message):
        self.timestamp = timestamp
        self.level = level
        self.message = message

class LogManager:
    def __init__(self):
        self.logs = []
        self.current_index = -1

    def add_log(self, log_entry):
        self.logs.append(log_entry)

    def get_next_log(self):
        if self.current_index + 1 < len(self.logs):
            self.current_index += 1
            return self.logs[self.current_index]
        return None

    def get_prev_log(self):
        if self.current_index - 1 >= 0:
            self.current_index -= 1
            return self.logs[self.current_index]
        return None

    def search_logs(self, query):
        return [log for log in self.logs if query in log.message]
