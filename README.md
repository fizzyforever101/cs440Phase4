
# CS 4400 Phase 4

## Overview

This GUI is designed to allow a user to interact with the business_supply database. It uses PyQt5 for the graphical user interface (GUI) and Python for the backend logic.

## Technologies Used

- **Python3**: Programming language used for the backend logic.
- **PyQt5**: GUI framework used for building the interface.
- **pip**: Python package manager used for managing dependencies.

## Work Distribution

- Sabina Sokol: GUI design and code
- Aishi Tyagi: Phase 3 Debuggging

## Setup Instructions

### Prerequisites

Ensure that Python 3 and pip are installed on your machine. You can check by running the following commands:

```bash
python3 --version
pip --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

You should also already have SQL Workbench with the business_supply database available on your computer.

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone <repository_url>
cd <project_directory>
```

### 2. Create a Virtual Environment (Recommended)

It’s recommended to use a virtual environment to avoid conflicts with system-wide packages:

```bash
python3 -m venv venv
```

Activate the virtual environment:

- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 3. Install the Required Dependencies

Install the required Python packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

If you want to force reinstall the dependencies (if already installed), run:

```bash
pip install --force-reinstall -r requirements.txt
```
### 4. Load the SQL Script in the SQL Workbench

Go to File > Open SQL Script and select cs4400_phase3_stored_procedures_3.sql. Once loaded, click the lightning bolt in the top of the workbench to run the file.

### 5. Run the Application

Once the dependencies are installed, you can run the application with:

```bash
python3 5done.py
```

### 6. Deactivate Virtual Environment (Optional)

When you're done, deactivate the virtual environment:

```bash
deactivate
```
