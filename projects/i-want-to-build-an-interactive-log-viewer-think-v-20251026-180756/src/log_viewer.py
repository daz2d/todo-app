from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Sample log data
logs = [
    {"timestamp": "2023-10-01T12:00:00", "level": "INFO", "message": "User logged in", "username": "user1", "ip": "192.168.1.1"},
    {"timestamp": "2023-10-01T12:05:00", "level": "ERROR", "message": "Failed login attempt", "username": "user2", "ip": "192.168.1.2"},
    {"timestamp": "2023-10-02T14:00:00", "level": "WARNING", "message": "Disk space low", "username": "admin", "ip": "192.168.1.3"}
]

@app.route('/logs', methods=['GET'])
def get_logs():
    # Get query parameters for filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    level = request.args.get('level')
    keyword = request.args.get('keyword')

    filtered_logs = logs

    # Filter by date range
    if start_date:
        filtered_logs = [log for log in filtered_logs if datetime.fromisoformat(log['timestamp']) >= datetime.fromisoformat(start_date)]
    if end_date:
        filtered_logs = [log for log in filtered_logs if datetime.fromisoformat(log['timestamp']) <= datetime.fromisoformat(end_date)]

    # Filter by log level
    if level:
        filtered_logs = [log for log in filtered_logs if log['level'] == level]

    # Filter by keyword
    if keyword:
        filtered_logs = [log for log in filtered_logs if keyword in log['message']]

    return jsonify(filtered_logs)

if __name__ == '__main__':
    app.run(debug=True)