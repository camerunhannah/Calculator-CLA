🚀 Advanced Python Calculator
This project develops a robust command-line calculator application built with Python. It features a wide range of arithmetic operations, a history management system with undo/redo capabilities, flexible configuration via environment variables, comprehensive logging, and auto-saving of calculations. The application leverages several design patterns to ensure a modular, maintainable, and scalable codebase, including Factory, Memento, and Observer patterns. It also boasts high test coverage and is set up for Continuous Integration with GitHub Actions.

✨ Features
Expanded Arithmetic Operations: Supports basic operations (addition, subtraction, multiplication, division) plus advanced functions like Power, Root, Modulus, Integer Division, Percentage Calculation, and Absolute Difference.

Factory Design Pattern: Manages the creation of different operation instances dynamically.

History Management (Undo/Redo): Utilizes the Memento Design Pattern to allow users to revert or re-apply past calculations.

Event-Driven Logging & Auto-Save: Implements the Observer Design Pattern with:

LoggingObserver: Logs each calculation to a configurable log file.

AutoSaveObserver: Automatically saves calculation history to a CSV file using pandas after each new calculation.

Flexible Configuration: Manages application settings (directories, history size, precision, input limits, encoding) via a .env file and python-dotenv.

Robust Error Handling: Employs custom exceptions (OperationError, ValidationError) for clear error messages and input validation.

Comprehensive Logging: Integrates Python's logging module to track events, warnings, and errors.

Command-Line Interface (REPL): A user-friendly Read-Eval-Print Loop for interactive use.

Data Persistence: Saves and loads calculation history to/from CSV files using pandas.

High Test Coverage: Achieves 90% test coverage or better using pytest and pytest-cov to ensure reliability.

Continuous Integration (CI): Configured with GitHub Actions to automatically run tests and check coverage on every push and pull request.

Color-Coded Outputs: Enhances readability and user experience in the command-line interface with distinct colors for prompts, results, errors, and informational messages using the colorama library.

📦 Project Setup
Follow these steps to get the calculator application up and running on your local machine.

🧩 1. Install Homebrew (macOS Only)
Skip this step if you're on Windows.

Homebrew is a package manager for macOS. You'll use it to easily install Git, Python, and other developer tools.

Install Homebrew:

Bash

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Verify Homebrew Installation:

Bash

brew --version
If you see a version number, you're good to go.

🧩 2. Install and Configure Git
Git is essential for version control and collaborating on projects.

Install Git
macOS (using Homebrew)

Bash

brew install git
Windows
Download and install Git for Windows. We recommend accepting the default options during installation.

Verify Git Installation:
Bash

git --version
Configure Git Globals
Set your name and email so Git correctly attributes your commits:

Bash

git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
Confirm your settings:

Bash

git config --list
Generate SSH Keys and Connect to GitHub
Important: Perform this step only once per machine. If you've already set up SSH for GitHub, you can skip this.

Generate a new SSH key:

Bash

ssh-keygen -t ed25519 -C "your_email@example.com"
(Press Enter at all prompts to accept default file locations and no passphrase.)

Start the SSH agent:

Bash

eval "$(ssh-agent -s)"
Add your SSH private key to the agent:

Bash

ssh-add ~/.ssh/id_ed25519
Copy your SSH public key:

Mac/Linux:

Bash

cat ~/.ssh/id_ed25519.pub | pbcopy
Windows (Git Bash):

Bash

cat ~/.ssh/id_ed25519.pub | clip
Add the key to your GitHub account:

Go to GitHub SSH Settings

Click the green "New SSH key" button.

Give it a descriptive title (e.g., "My Laptop").

Paste your copied public key into the "Key" field.

Click "Add SSH key".

Test the SSH connection:

Bash

ssh -T git@github.com
You should see a success message confirming your authentication.

🧩 3. Clone the Repository
Once Git and SSH are configured, clone the project repository:

Bash

git clone <your-repository-url>
cd <repository-directory> # Replace with your actual directory name
🛠️ 4. Install Python and Set Up Virtual Environment
This project requires Python 3.12.3 (matching the CI environment). Using a virtual environment is highly recommended to manage project dependencies separately.

Install Python
macOS (using Homebrew)

Bash

brew install python@3.12 # Installs Python 3.12 specifically
Windows
Download and install Python 3.12.3 for Windows. Ensure you check the box Add Python to PATH during setup.

Verify Python Installation:
Bash

python3 --version # Or 'python --version' depending on your PATH setup
Confirm it shows Python 3.12.3 or a similar 3.12.x version.

Create and Activate a Virtual Environment
Navigate to your project's root directory:

Bash

python3 -m venv venv
Activate the virtual environment:

Mac/Linux:

Bash

source venv/bin/activate
Windows (Command Prompt):

Bash

venv\Scripts\activate.bat
Windows (PowerShell):

PowerShell

.\venv\Scripts\Activate.ps1
You'll know it's active when (venv) appears at the start of your command line prompt.

Install Required Python Packages
With your virtual environment active, install all project dependencies:

Bash

pip install -r requirements.txt
⚙️ Configuration Setup
The calculator uses a .env file for managing configuration settings.

Create a .env file: In the root of your project directory, create a new file named .env.

Add Configuration Parameters: Populate your .env file with the following, adjusting values as needed. These values will override the application's internal defaults.

Code snippet

# .env - Calculator Configuration

# Base Directories (paths are relative to your project root by default)
# CALCULATOR_BASE_DIR=./          # Optional: Uncomment and set if your project root isn't the default
CALCULATOR_LOG_DIR=logs           # Directory for log files (relative to base_dir)
CALCULATOR_LOG_FILE=calculator.log # Name of the log file
CALCULATOR_HISTORY_DIR=history    # Directory for history files (relative to base_dir)
CALCULATOR_HISTORY_FILE=calculator_history.csv # Name of the history CSV file

# History Settings
CALCULATOR_MAX_HISTORY_SIZE=1000  # Maximum number of calculation history entries
CALCULATOR_AUTO_SAVE=true         # Whether to automatically save history after each calculation (true/false, 1/0, yes/no, on/off)

# Calculation Settings
CALCULATOR_PRECISION=10           # Number of decimal places for calculation results
CALCULATOR_MAX_INPUT_VALUE=1000000000000000000 # Max allowed input value (e.g., 1e18 for 10^18)
CALCULATOR_DEFAULT_ENCODING=utf-8 # Default encoding for file operations (e.g., 'utf-8')
Note: If a parameter is not set in .env, the application will use its internal default value.

🚀 Running the Application
Ensure your virtual environment is active before running.

Using the Command-Line Interface (REPL)
To start the interactive calculator REPL:

Bash

python main.py
Supported Commands:
Once the calculator starts, you can type commands at the prompt:

add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff: Perform calculations. You'll be prompted for two numerical inputs after entering the command.

Example:

Enter command: add
Enter first number: 5
Enter second number: 3
Result: 8
history: Display all calculations stored in the current session's history.

clear: Erase all entries from the calculation history.

undo: Revert the last performed calculation.

redo: Re-apply the last undone calculation.

save: Manually save the current calculation history to the configured CSV file.

load: Load calculation history from the configured CSV file, replacing the current session's history.

help: Display a list of all available commands and their descriptions.

exit: Gracefully close the calculator application.

✅ Running Tests and Checking Coverage
You can run the unit tests and generate a coverage report to ensure code quality and identify untested areas.

Activate your virtual environment (if not already active).

Run pytest with coverage:

Bash

pytest --cov=app --cov-fail-under=90
--cov=app: Specifies that coverage should be collected for the app directory.

--cov-fail-under=90: Ensures the test run will fail if the total coverage percentage falls below 90%.

View the detailed coverage report: After the test run, an HTML report is generated.

Bash

# (Optional) Generate HTML report if not done automatically
# pytest --cov=app --cov-report=html

# Open the HTML report in your browser
# For Mac/Linux:
open htmlcov/index.html
# For Windows:
start htmlcov\index.html
This report provides a line-by-line breakdown of code coverage.

🔗 Continuous Integration (CI) with GitHub Actions
This project is configured with GitHub Actions to automate testing and coverage checks on every code push and pull request to the main branch.

The CI workflow is defined in .github/workflows/python-app.yml.

It ensures that tests are run in a consistent environment (ubuntu-latest with Python 3.12.3) and verifies that the 90% coverage threshold is maintained.

You can view the status of your CI runs under the "Actions" tab in your GitHub repository. Green checkmarks mean everything passed!

📋 Notes & Best Practices
Explicit Imports: Remember that Python requires explicit imports for modules (import os, import logging, from app.exceptions import OperationError, etc.). Linters like Pylance will help you catch missing imports.

Consistent Naming: Within the application and tests, command names like "add" or "power" are used for operations passed to the Calculator and stored in history. The __str__ method of the operation classes provides more descriptive names like "Addition" for display.

Decimal Precision: The application uses Python's Decimal type for accurate floating-point arithmetic, which is crucial for financial or precise calculations. The CALCULATOR_PRECISION setting in .env controls the display precision.

Error Handling: Custom exceptions (OperationError, ValidationError, ConfigurationError) provide clear and specific error messages.

Modular Design: The codebase is organized into distinct modules and classes (e.g., Calculation, Calculator, Operation, OperationFactory, CalculatorConfig, HistoryObserver) following principles like the Single Responsibility Principle and Dependency Inversion.

Color-Coded Output: The command-line interface uses colors (powered by colorama) to enhance readability, distinguish prompts, results, and various types of messages, making the user experience more intuitive and engaging.

🔥 Useful Commands Cheat Sheet
Action

Command

Install Homebrew (Mac)

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Install Git

brew install git or Git for Windows installer

Configure Git Global Username

git config --global user.name "Your Name"

Configure Git Global Email

git config --global user.email "you@example.com"

Clone Repository

git clone <repo-url>

Create Virtual Environment

python3 -m venv venv

Activate Virtual Environment (Mac/Linux)

source venv/bin/activate

Activate Virtual Environment (Windows)

venv\Scripts\activate.bat

Install Python Packages

pip install -r requirements.txt

Start Calculator REPL

python main.py

Run Tests (locally)

pytest --cov=app --cov-fail-under=90

Open Coverage Report

open htmlcov/index.html (Mac/Linux) / start htmlcov\index.html (Windows)

Push Code to GitHub

git add . && git commit -m "message" && git push


Export to Sheets
📎 Quick Links
Homebrew

Git Downloads

Python Downloads

GitHub SSH Setup Guide

Pytest Documentation

Pytest-Cov Documentation

Python-dotenv Documentation

Pandas Documentation

