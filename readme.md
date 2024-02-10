Ensure the following files are in your working directory:
dash_app.py
all_spaceships_auto_pricing.py
requirements.txt
ship_lookup.csv
spaceships.csv
chromedriver_win32 (and the exe file contained)

Create your virtual environment (only need to do this once):
In the terminal, type "py -m venv spaceships"

Activate your virtual environment (need to do this each time you open VS Code and want to run the program):
In the terminal, type "spaceships\Scripts\activate.bat"

Install required packages (only need to do this once):
In the terminal, type "py -m pip install -r requirements.txt

To run the Dashboard:
In the terminal, type "spaceships\Scripts\activate.bat"
Open dash_app.py
Click the play button in the top right corner.
The terminal will ask if you want LTI (x) or 10 year (y) insurance.
The program will then scrape all the info from Star Hangar (you'll see "Checking 1 of 120 - renegade" etc)
When that's run through twice (unsure why), open a browser and go to http://127.0.0.1:8050/ (this shouldn't change but if it does, but if it does, check the terminal output for "Dash is running on...")
YOU MUST LOGIN
Now you can view the graph of price difference to the top, automatically change the prices for those within $X of the top, or individually change prices using the dropdown function.
Once you've finished a session, you'll need to kill the program and restart to see the changes in the graph. To do this, either click anywhere in the terminal and press CTRL-C or kill the open terminal(s) using the trash icons on the right. You can then press the play button again and see updates.

Very occasionally, the whole thing might crash / become unresponsive (connection errors etc). If this happens, you need to kill the background Python executable in Task Manager.