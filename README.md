# Stock Price Viewer
## Project Overview

**Stock Price Viewer** is a web application designed to fetch and visualize historical stock prices from Yahoo Finance.
The application is developed **with the help of AI-assisted programming using Gemini-pro-2.5,** which helped streamline the coding process and improve efficiency.

Given the following **required fields:**

- Stock Ticker
- Start Date
- End Date

The app will:

- Retrieve historical stock prices for the specified date range from Yahoo Finance.
- Generate a plot of stock price versus date for easy visualization.
- Display the most recent stock price, covering up to the last 20 days.

## Project Structures
  ```
    1 /home/henryjia/Projects/flask_stock_plot/
    2 ├───.gcloudignore             # Specifies files to ignore when deploying to Google Cloud.
    3 ├───.gitignore                # Specifies intentionally untracked files that Git should ignore.
    4 ├───app.py                    # The main application file for your Flask project.
    5 ├───app.yaml                  # Configuration file for deploying your application to Google App Engine.
    6 ├───cloudbuild.yaml           # Configuration file for Google Cloud Build.
    7 ├───README.md                 # Provides general information about the project.
    8 ├───requirements.txt          # Lists the Python dependencies required by your project.
    9 ├───test_create.py            # Contains tests related to creation functionalities.
   10 ├───__pycache__/              # Directory where Python stores bytecode.
   11 ├───.git/                     # The Git repository directory.
   12 ├───.pytest_cache/            # Cache directory used by pytest.
   13 │   └───v/...                 # Subdirectory within the pytest cache.
   14 ├───instance/                 # Stores instance-specific configuration or data.
   15 ├───static/                   # Contains static files like CSS, JavaScript, and images.
   16 │   └───style.css             # A CSS stylesheet for your web application.
   17 ├───templates/                # Contains HTML template files.
   18 │   ├───error.html            # HTML template for displaying error messages.
   19 │   ├───index.html            # The main HTML template for your application's homepage.
   20 │   └───result.html           # HTML template for displaying results.
   21 ├───tests/                    # Directory containing unit tests and integration tests.
   22 │   ├───test_app.py           # Contains tests specifically for the main application logic.
   23 │   └───__pycache__/          # Python bytecode cache for the test files.
   24 └───venv/                     # A Python virtual environment.
   25     ├───bin/...               # Executables for the virtual environment.
   26     ├───include/...           # Header files for packages in the virtual environment.
   27     ├───lib/...               # Python libraries and packages in the virtual environment.
   28     └───share/...             # Shared data for packages in the virtual environment.
  ```

## Running the Application Locally
  1. Activate the virtual environment 
  ```
  source venv/bin/activate
  ```
  2. Install the required dependencies
  ```
  pip install -r requirements.txt
  ```
  3. Start the Flask application
  ```
  python app.py
  ```
  4. Open the app in your browser
  On your browser, go to [http://127.0.0.0:5000](http:/127/0/0/1:5000)
     The Stock Viewer GUI will appears and you can enter required data to get result.

## Unit Test in Local Enrionment
```
  pytest
```
 
## Deploment To GCP 
```
  git add .
  git commit -m 'new features'
  git push
```
  The git push will trigger CI/CD deployment.

## Running the Application on GCP
  Open the app in the broser: [https://flask-stock-plot.uc.r.appspot.com/](https://flask-stock-plot.uc.r.appspot.com/)
