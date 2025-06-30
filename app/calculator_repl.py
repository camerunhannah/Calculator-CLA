# app/calculator_repl.py

import sys
from decimal import Decimal
import logging
from colorama import Fore, Style, init # ADDED THIS LINE
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

        print(Fore.GREEN + "Calculator started. Type 'help' for commands." + Style.RESET_ALL)

        while True:
            try:
                # Prompt the user for a command (Cyan)
                command = input(Fore.CYAN + "\nEnter command: " + Style.RESET_ALL).lower().strip()

                if not command: # Handle empty input gracefully (Yellow)
                    print(Fore.YELLOW + "No command entered. Type 'help' for available commands." + Style.RESET_ALL)
                    continue

                if command == 'help':
                    # Display available commands, including new ones (Bright Yellow/Help section)
                    print(Style.BRIGHT + "\nAvailable commands:" + Style.RESET_ALL)
                    print(Fore.WHITE + "  add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff - Perform calculations" + Style.RESET_ALL)
                    print(Fore.WHITE + "  history - Show calculation history" + Style.RESET_ALL)
                    print(Fore.WHITE + "  clear - Clear calculation history" + Style.RESET_ALL)
                    print(Fore.WHITE + "  undo - Undo the last calculation" + Style.RESET_ALL)
                    print(Fore.WHITE + "  redo - Redo the last undone calculation" + Style.RESET_ALL)
                    print(Fore.WHITE + "  save - Save calculation history to file" + Style.RESET_ALL)
                    print(Fore.WHITE + "  load - Load calculation history from file" + Style.RESET_ALL)
                    print(Fore.WHITE + "  help - Display this help message" + Style.RESET_ALL)
                    print(Fore.WHITE + "  exit - Exit the application" + Style.RESET_ALL)
                    continue

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully." + Style.RESET_ALL)
                    except OperationError as e: # Catch specific OperationError (Red Warning)
                        print(Fore.YELLOW + f"Warning: Could not save history: {e}" + Style.RESET_ALL)
                    except Exception as e: # Catch any other unexpected error during save (Red Warning)
                        logging.error(f"Unexpected error during history save on exit: {e}", exc_info=True)
                        print(Fore.YELLOW + f"Warning: Could not save history: {e}" + Style.RESET_ALL)
                    print(Fore.GREEN + "Goodbye!" + Style.RESET_ALL)
                    break

                if command == 'history':
                    # Display calculation history (Bright Yellow header, White entries)
                    history = calc.show_history()
                    if not history:
                        print(Fore.YELLOW + "No calculations in history." + Style.RESET_ALL)
                    else:
                        print(Style.BRIGHT + "\nCalculation History:" + Style.RESET_ALL)
                        for i, entry in enumerate(history, 1):
                            print(Fore.WHITE + f"{i}. {entry}" + Style.RESET_ALL)
                    continue

                if command == 'clear':
                    # Clear calculation history (Yellow)
                    calc.clear_history()
                    print(Fore.YELLOW + "History cleared." + Style.RESET_ALL)
                    continue

                if command == 'undo':
                    # Undo the last calculation (Yellow/Info)
                    if calc.undo():
                        print(Fore.YELLOW + "Operation undone." + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Nothing to undo." + Style.RESET_ALL)
                    continue

                if command == 'redo':
                    # Redo the last undone calculation (Yellow/Info)
                    if calc.redo():
                        print(Fore.YELLOW + "Operation redone." + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Nothing to redo." + Style.RESET_ALL)
                    continue

                if command == 'save':
                    # Save calculation history to file (Green/Red for success/failure)
                    try:
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully." + Style.RESET_ALL)
                    except OperationError as e:
                        print(Fore.RED + f"Error saving history: {e}" + Style.RESET_ALL)
                    except Exception as e:
                        logging.error(f"Unexpected error during manual history save: {e}", exc_info=True)
                        print(Fore.RED + f"Error saving history: {e}" + Style.RESET_ALL)
                    continue

                if command == 'load':
                    # Load calculation history from file (Green/Red for success/failure)
                    try:
                        calc.load_history()
                        print(Fore.GREEN + "History loaded successfully." + Style.RESET_ALL)
                    except OperationError as e:
                        print(Fore.RED + f"Error loading history: {e}" + Style.RESET_ALL)
                    except Exception as e:
                        logging.error(f"Unexpected error during history load: {e}", exc_info=True)
                        print(Fore.RED + f"Error loading history: {e}" + Style.RESET_ALL)
                    continue

                # --- Handle all arithmetic commands ---
                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root',
                               'modulus', 'int_divide', 'percent', 'abs_diff']:
                    try:
                        # Prompts for numbers (Cyan)
                        print(Fore.CYAN + "\nEnter numbers (or 'cancel' to abort):" + Style.RESET_ALL)
                        a = input(Fore.CYAN + "First number: " + Style.RESET_ALL).strip()
                        if a.lower() == 'cancel':
                            print(Fore.YELLOW + "Operation cancelled." + Style.RESET_ALL)
                            continue
                        b = input(Fore.CYAN + "Second number: " + Style.RESET_ALL).strip()
                        if b.lower() == 'cancel':
                            print(Fore.YELLOW + "Operation cancelled." + Style.RESET_ALL)
                            continue

                        calc.set_operation(command) 
                        result = calc.perform_operation(a, b)

                        # Display result (Green + Bright style)
                        if calc.history:
                            formatted_result = calc.history[-1].format_result(calc.config.precision)
                            print(Fore.GREEN + Style.BRIGHT + f"\nResult: {formatted_result}" + Style.RESET_ALL)
                        else:
                             print(Fore.GREEN + Style.BRIGHT + f"\nResult: {result}" + Style.RESET_ALL) # pragma: no cover


                    except (ValidationError, OperationError) as e: # Specific errors (Red)
                        print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                    except Exception as e: # Unexpected errors (Red)
                        logging.error(f"Unexpected error during command '{command}': {e}", exc_info=True)
                        print(Fore.RED + f"Unexpected error: {e}" + Style.RESET_ALL)
                    continue 

                # Handle unknown commands (Yellow)
                print(Fore.YELLOW + f"Unknown command: '{command}'. Type 'help' for available commands." + Style.RESET_ALL)

            except KeyboardInterrupt: # Ctrl+C (Yellow)
                print(Fore.YELLOW + "\nOperation cancelled. Type 'exit' to quit the calculator." + Style.RESET_ALL)
                continue
            except EOFError: # Ctrl+D (Yellow/Green for save/exit)
                print(Fore.YELLOW + "\nInput terminated. Exiting..." + Style.RESET_ALL)
                try:
                    if calc: 
                        calc.save_history()
                        print(Fore.GREEN + "History saved successfully." + Style.RESET_ALL)
                except OperationError as e: # pragma: no cover
                    print(Fore.YELLOW + f"Warning: Could not save history on exit: {e}" + Style.RESET_ALL) # pragma: no cover
                except Exception as e: # pragma: no cover
                    logging.error(f"Unexpected error during history save on EOF: {e}", exc_info=True) # pragma: no cover
                    print(Fore.YELLOW + f"Warning: Could not save history on exit: {e}" + Style.RESET_ALL) # pragma: no cover
                print(Fore.GREEN + "Goodbye!" + Style.RESET_ALL)
                break
            except Exception as e: # Outer unhandled errors (Red)
                logging.error(f"An unhandled error occurred in REPL loop: {e}", exc_info=True)
                print(Fore.RED + f"An unhandled error occurred: {e}" + Style.RESET_ALL)
                print(Fore.RED + "Exiting due to unhandled error." + Style.RESET_ALL)
                break 

    except Exception as e: # Fatal initialization errors (Red)
        logging.error(f"Fatal error in calculator REPL during initialization: {e}", exc_info=True)
        print(Fore.RED + f"Fatal error: {e}. Exiting." + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    calculator_repl()