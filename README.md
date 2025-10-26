# Error Handling System

This module provides a centralized error handling mechanism that captures exceptions and provides user-friendly error messages.

## Installation

No installation required - simply import the `error_handling` module in your application code.

## Usage

To handle errors, use the `handle_error` function to display informative error messages and raise the corresponding exception type. For example:

```python
try:
    # Code that may raise an error
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Running Tests

To run the unit tests, execute the following command in your terminal:

```bash
python -m unittest tests/test_error_handling.py
```

## Contributing

Pull requests are welcome! Please submit a pull request with any changes or updates to this module.

## License

This project is licensed under the MIT License. See LICENSE for details.