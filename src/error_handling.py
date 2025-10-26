import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

class ValidationError(Exception):
    """Raised when validation fails"""
    pass

class DatabaseError(Exception):
    """Raised when database operation fails"""
    pass

def handle_error(error_type, message):
    """
    Handle errors by displaying informative error messages.

    Args:
        error_type (str): Type of error (e.g., "ValidationError", "DatabaseError")
        message (str): Error message to display
    """
    logging.error(f"{error_type}: {message}")
    raise error_type(message)

def validate_input(data):
    # Simple validation example - replace with actual validation logic
    if not data:
        handle_error(ValidationError, "Invalid input: cannot be empty")
    return data

def execute_database_query(query):
    # Simulate database query execution - replace with actual implementation
    import random
    if random.random() < 0.5:
        raise DatabaseError("Database query failed")
    return query

# Example usage:
try:
    validate_input(None)
except ValidationError as e:
    print(f"Validation error: {e}")
else:
    print("Input is valid")

try:
    execute_database_query("SELECT * FROM users")
except DatabaseError as e:
    print(f"Database error: {e}")