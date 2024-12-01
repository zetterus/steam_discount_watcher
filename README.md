Steam Discount Watcher is a tool designed to help you keep track of discounts on Steam games. It comes in two versions: a console application and a web application.

# Console Version

The console version of Steam Discount Watcher allows you to monitor discounts directly from your terminal. It includes a scheduling feature that lets you run the application at specified intervals to check for new discounts automatically.

## Features

- Monitor Steam game discounts from the command line.
- Schedule the application to run at regular intervals.
- Receive notifications about new discounts.

## Installation

To install the console version, follow these steps:

1. Clone the repository:

  ```
  git clone https://github.com/zetterus/steam_discount_watcher.git
  ```

2. Navigate to the project directory:

  ```
  cd steam_discount_watcher
  ```

3. Install the required dependencies:

  ```
  pip install -r requirements.txt
  ```

## Usage

To run the console version, use the following command from your project directory:

  ```
  python main.py
  ```

# Web Version

The web version of Steam Discount Watcher is available at [https://steamwatcher.streamlit.app/](https://steamwatcher.streamlit.app/). This version does not include the scheduling feature but offers user authentication and the ability to save settings for authenticated users.

## Features

- Monitor Steam game discounts through a web interface.
- Track game discounts by genre.
- Track game discounts by user SteamID64.
- User authentication to save and manage your settings.
