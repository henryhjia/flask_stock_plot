  This is a project to retrieve a stock price.  Required field: Stock Ticket, Start Date, End Date.  It will retrieve the historic stock price
  from yahoo finance for the date range. Then it will plot the stock price vs date.  It will also print out the most recent stock price up to 20 days.

  Here is the directory structures:
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

  To run locally:
  1. $ source venv/bin/activate
  2. $ python app.py
  3. On your browser, go to http://127.0.0.0:5000
     The Stock Viewer GUI will appears and you can enter required data to get result.

  To test locally:
  $ pytest

  After unit test passed, to deploy:
  $ git add .
  $ git commit -m 'new features'
  $ git push

  To run in the GCP:
  https://flask-stock-plot.uc.r.appspot.com/
