# Pandora Calibration Data Management System

## Overview

This repository contains a Flask-based web application for managing calibration data files for Pandora instruments. The system allows for processing calibration files, querying data, and retrieving file contents through a RESTful API.

## Features

- Process and store calibration files
- Query calibration data based on specific keys
- Retrieve full content of calibration files
- Health check endpoint
- List all calibration files in the system

## Postman API Collection

- File Name - `LuftBlick.postman_collection.json`

## Tech Stack

- Python 3.11
- Flask
- SQLAlchemy
- SQLite
- Docker

## File Structure

```
.
├── Dockerfile
├── README.md
├── app.py
├── calibration_files
│   └── Pandora101s1_CF_v12d20230620.txt
├── docker-compose.yml
├── instance
│   └── calibration.db
├── models.py
├── requirements.in
└── requirements.txt
```

## Setup and Installation

### Using Docker

1. Clone the repository:
   ```
   git clone https://github.com/akshatjain-beam/luftblick.git
   cd luftblick
   ```

2. Build and Run the Docker image:
   ```
   docker-compose up --build
   ```

The application will be accessible at `http://localhost:5001`.

### Manual Setup

1. Clone the repository:
   ```
   git clone https://github.com/akshatjain-beam/luftblick.git
   cd luftblick
   ```

2. Create a virtual environment and activate it:
   ```
   python3.11 -m venv venv && source venv/bin/activate
   ```
3. Upgarde the pip
   ```
   pip install --upgrade pip
   ```

4. If want to use the `requirements.in` file for populating the `requirements.txt` file(optional):
   - `pip install pip-tools`
   - `pip-compile --resolver=backtracking requirements.in`

5. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

6. Run the application:
   ```
   python app.py
   ```

The application will be accessible at `http://localhost:5001`.

## API Endpoints

1. **Process Files**
   - URL: `/api/process_files`
   - Method: POST
   - Description: Processes calibration files in the `calibration_files` directory and saves the data in the database.

2. **Query Calibration Data**
   - URL: `/api/query`
   - Method: GET
   - Description: Queries calibration data based on provided keys.

3. **Health Check**
   - URL: `/api/health`
   - Method: GET
   - Description: Checks the health status of the application.

4. **Get File Content**
   - URL: `/api/get_content`
   - Method: GET
   - Parameters: `filename`
   - Description: Retrieves the content of a specific calibration file.

5. **List Calibration Files**
   - URL: `/api/calibration_files`
   - Method: GET
   - Description: Lists all calibration files in the system.

----

## Importing a JSON File into Postman

This guide will help you import a JSON file into Postman, enabling you to load collections, environments, or data files.

## Prerequisites

- Ensure you have [Postman](https://www.postman.com/downloads/) installed on your computer.

## Steps

1. **Open Postman**

   Launch the Postman application on your computer.

2. **Go to the Import Page**

   - Click on the `Import` button located at the top left corner of the Postman interface.
   - Alternatively, you can use the shortcut `Ctrl + O` (Windows/Linux) or `Cmd + O` (Mac) to open the import dialog.

3. **Select Import Method**

   - In the import dialog, choose the `File` tab.

4. **Upload Your JSON File**

   - Drag and drop your JSON file into the import window, or click `Choose Files` to browse and select the file from your computer.
   - In our case, the file is present at `LuftBlick.postman_collection.json` in `luftblick` folder.

5. **Import the File**

   - Once your file is selected, click the `Import` button to start the import process.

6. **Verify Import**

   - After importing, check the `Collections` tab (or `Environments`, if applicable) to ensure your data has been correctly loaded.
