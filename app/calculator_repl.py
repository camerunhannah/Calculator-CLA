# app/calculator_repl.py

import sys
from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory # Keep OperationFactory import for test patching purposes
from app.calculator_config import CalculatorConfig

def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    calc = None # Initialize calc outside try block for broader scope

    try:
        # Initialize the CalculatorConfig
        config = CalculatorConfig()
        # Initialize the Calculator instance with the config
        calc = Calculator(config)

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        if config.auto_save: # Conditionally add AutoSaveObserver based on config
            calc.add_observer(AutoSaveObserver(calc)) # Pass 'calc' instance, not 'config'

        print("Calculator started. Type 'help' for commands.")

        while True:
            try:
                # Prompt the user for a command
                command = input("\nEnter command: ").lower().strip()

                if not command: # Handle empty input gracefully
                    print("No command entered. Type 'help' for available commands.")
                    continue

                if command == 'help':
                    # Display available commands, including new ones
                    print("\nAvailable commands:")
                    print("  add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff - Perform calculations")
                    print("  history - Show calculation history")
                    print("  clear - Clear calculation history")
                    print("  undo - Undo the last calculation")
                    print("  redo - Redo the last undone calculation")
                    print("  save - Save calculation history to file")
                    print("  load - Load calculation history from file")
                    print("  help - Display this help message")
                    print("  exit - Exit the calculator")
                    continue

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print("History saved successfully.")
                    except OperationError as e: # Catch specific OperationError from save_history
                        print(f"Warning: Could not save history: {e}")
                    except Exception as e: # Catch any other unexpected error during save
                        logging.error(f"Unexpected error during history save on exit: {e}", exc_info=True)
                        print(f"Warning: Could not save history: {e}")
                    print("Goodbye!")
                    break

                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print("No calculations in history.")
                    else:
                        print("\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print("History cleared.")
                    continue

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print("Operation undone.")
                    else:
                        print("Nothing to undo.")
                    continue

                if command == 'redo':
                    # Redo the last undone calculation

                    if calc.redo():
                        print("Operation redone.")
                    else:
                        print("Nothing to redo.")
                    continue

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print("History saved successfully.")
                    except OperationError as e:
                        print(f"Error saving history: {e}")
                    except Exception as e:
                        logging.error(f"Unexpected error during manual history save: {e}", exc_info=True)
                        print(f"Error saving history: {e}")
                    continue

                if command == 'load':
                    # Load calculation history from file
                    try:
                        calc.load_history()
                        print("History loaded successfully.")
                    except OperationError as e:
                        print(f"Error loading history: {e}")
                    except Exception as e:
                        logging.error(f"Unexpected error during history load: {e}", exc_info=True)
                        print(f"Error loading history: {e}")
                    continue

                # --- Handle all arithmetic commands ---
                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root',
                               'modulus', 'int_divide', 'percent', 'abs_diff']:
                    # Perform the specified arithmetic operation
                    try:
                        print("\nEnter numbers (or 'cancel' to abort):")
                        a = input("First number: ").strip()
                        if a.lower() == 'cancel':
                            print("Operation cancelled.")
                            continue
                        b = input("Second number: ").strip()
                        if b.lower() == 'cancel':
                            print("Operation cancelled.")
                            continue

                        # Pass the command string directly to set_operation
                        # The Calculator class will now use OperationFactory internally
                        calc.set_operation(command) 

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Format the result using the Calculator's configured precision
                        # Access the last calculation from history for proper formatting
                        if calc.history:
                            formatted_result = calc.history[-1].format_result(calc.config.precision)
                            print(f"\nResult: {formatted_result}")
                        else:
                             print(f"\nResult: {result}") # pragma: no cover


                    except (ValidationError, OperationError) as e:
                        print(f"Error: {e}")
                    except Exception as e: # This block is now fully re-enabled for production use
                        logging.error(f"Unexpected error during command '{command}': {e}", exc_info=True)
                        print(f"Unexpected error: {e}")
                    continue # Ensure this continue is outside the inner except blocks


                # Handle unknown commands if none of the above matched
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print("\nOperation cancelled. Type 'exit' to quit the calculator.")
                continue
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print("\nInput terminated. Exiting...")
                try:
                    # Attempt to save history before exiting on EOF
                    if calc: # Ensure calc is defined before trying to save
                        calc.save_history()
                        print("History saved successfully.")
                except OperationError as e: # pragma: no cover
                    print(f"Warning: Could not save history on exit: {e}") # pragma: no cover
                except Exception as e: # pragma: no cover
                    logging.error(f"Unexpected error during history save on EOF: {e}", exc_info=True) # pragma: no cover
                    print(f"Warning: Could not save history on exit: {e}") # pragma: no cover
                print("Goodbye!")
                break
            except Exception as e: # This is the outer, general loop exception handler, now re-enabled
                # Handle any other unhandled unexpected exceptions in the REPL loop
                logging.error(f"An unhandled error occurred in REPL loop: {e}", exc_info=True)
                print(f"An unhandled error occurred: {e}")
                print("Exiting due to unhandled error.")
                break 

    except Exception as e:
        # Handle fatal errors during initial setup/calculator initialization
        logging.error(f"Fatal error in calculator REPL during initialization: {e}", exc_info=True)
        print(f"Fatal error: {e}. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    calculator_repl()