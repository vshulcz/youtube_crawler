# YouTubeCrawler

YouTubeCrawler is a fast, efficient, and user-friendly tool for collecting data from YouTube channels. It provides a Graphical User Interface (GUI) built with tkinter and uses its own database to store and manage the gathered data. This project leverages only the requests library, ensuring faster performance than the free YouTube API.

## About
YouTubeCrawler is optimized for speed, allowing you to gather data from YouTube channels quickly with a GUI, that makes it easy to interact with and manage your collected data. The tool utilizes its own database to store and organize data, making it convenient for various data-related tasks. YouTubeCrawler offers various tools to interact with the data you've collected for your specific needs.

## Usage
### YouTube Crawler
Open the "YouTube Crawler" tab in the application.
In the first input field, enter the channel name (from the YouTube channel URL, using "@").
In the second input field, specify how many videos you want to parse from the channel.
In the third input field, set the number of comments to collect for each video.
Click the "Run Crawling" button and wait for the progress bar to fill up.
After the crawling is complete, you can interact with the data using the built-in tools or for other purposes.

### SQLViewer
Open the "SQLViewer" tab in the application.
Choose the table you want to view from the dropdown menu.
Click the "Show the table" button to display the table's contents.
You can also sort the table by clicking on a column header and adjust column widths right in the application.

### DataBaseExecutor
Open the "DataBaseExecutor" tab in the application.
Enter any SQL query in the input field.
Click the "Execute a request" button to execute the query and receive the results.

### DataBaseSearcher
Open the "DataBaseSearcher" tab in the application.
Choose the parameter for your search:
For "User," search for users with the specified name.
For "Date," input a date in the format "YYYY-MM-DD" to retrieve comments starting from that date.
For "Channel," find all channels with the provided name.
For "Word," display comments containing the entered word.
For "Min messages," retrieve all users with a message count exceeding the specified value (integer input required).

## Installation
1. Ensure you have the tkinter installed. On mac os, you should run in the terminal:
 ```sh
 brew install python-tk
 ```
2. Clone this repository to your local machine with:
 ```sh
 git clone 
 ```
3. Navigate to the Repository Directory:
 ```sh
 cd YouTubeCrawler
 ```
4. Set up a Virtual Environment (Optional but Recommended):
 ```sh
 python -m venv venv
 ```
   Activate the virtual environment:\
   **On macOS and Linux:**
 ```sh
 source venv/bin/activate
 ```
5. Install Required Packages:
 ```sh
 pip install -r requirements.txt
 ```
6. Run the Application:
 ```sh
 python main.py
 ```
This will launch the application, and you can start using its features via the GUI. Use the GUI to start crawling YouTube channels, managing your collected data, and executing SQL queries.

## Contributions
Contributions to YouTubeCrawler are welcome. If you have ideas for improvements or new features, please open an issue or submit a pull request.

