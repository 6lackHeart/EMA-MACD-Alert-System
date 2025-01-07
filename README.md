# EMA-MACD-Alert-System
A Python-based trading signal bot that analyzes stock data using EMA, MACD, and support/resistance levels. Sends email alerts and includes a scheduled task system with hotkey-triggered state resets.

## 1. Project Purpose
This project showcases Python programming skills, including:

Retrieving historical stock data programmatically.
Performing technical analysis with indicators like EMA, MACD, and support/resistance levels.
Automating tasks such as sending email alerts and scheduling analysis.
Note: This project is a learning exercise and is not intended for real-world trading or financial advice. The trading logic included is a rough draft and needs further refinement. Use at your own risk.

## 2. Description
The Trading Signal Bot retrieves historical stock data and generates rough trading signals based on simple EMA, MACD, and support/resistance logic. It also demonstrates programmatic emailing, scheduling, and data manipulation.

## 3. Features
EMA and MACD Analysis: Calculates basic signals using 20 EMA, 50 EMA, and MACD indicators.
Support and Resistance Levels: Detects potential levels based on swing highs and lows.
Email Alerts: Sends notifications for buy/sell opportunities.
Hotkey Listener: Resets signal states manually with a Ctrl+Z hotkey.
Automated Scheduling: Executes analysis tasks at predefined times using schedule.

## 4. Requirements
Python 3.x
Libraries: yfinance, schedule, keyboard, smtplib, pandas, json
A Gmail account with an app password enabled for email alerts.

## 5. Setup Instructions
Clone the repository:
bash
Copy code
git clone https://github.com/yourusername/trading-signal-bot.git
Install dependencies:
bash
Copy code
pip install yfinance schedule keyboard
Update email credentials in the script: Replace the placeholders in the script with your Gmail credentials.
python
Copy code
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'
EMAIL_RECIPIENT = 'recipient_email@gmail.com'
Run the script:
bash
Copy code
python trading_signal_analyzer.py

## 6. Usage
The bot fetches stock data and checks for basic trading signals based on:
Moving Average Crossovers (20 EMA & 50 EMA).
MACD & Signal line comparison.
Proximity to detected support and resistance levels.
Use Ctrl+Z to reset all signal states during execution.
Scheduled tasks automatically execute during market hours as defined in the script.

## 7. Disclaimer
This project is purely educational and does not provide financial advice.
The trading logic and strategies implemented are basic and require further refinement.
Use at your own risk. The developer is not responsible for any financial losses incurred.

## 8. License
This project is licensed under the MIT License.
