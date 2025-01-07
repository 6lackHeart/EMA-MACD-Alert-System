import yfinance as yf
import json
import schedule
import time as t
import signal
import sys
import os
import keyboard
import threading  # For hotkey listening
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

ticker_symbols = ["AMD", "NVDA", "MSFT", "META", "NFLX", "TSLA", "AMZN", "AAPL", "COST"]
EMAIL_ADDRESS = ''  # Replace with your gmail
EMAIL_PASSWORD = ''  # Replace with your gmail app password
EMAIL_RECIPIENT = ''  # Replace with the recipient's email

# Graceful shutdown
def signal_handler(sig, frame):
    print("\nGracefully shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# File for signal states
STATE_FILE = "signal_states.json"

# Initialize state file if it doesn't exist
if not os.path.exists(STATE_FILE):
    initial_state = {ticker: {"call": False, "put": False} for ticker in ticker_symbols}
    with open(STATE_FILE, "w") as f:
        json.dump(initial_state, f, indent=4)

# Helper functions
def read_signal_states():
    """Read signal states from the file."""
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def write_signal_states(states):
    """Write updated signal states to the file."""
    with open(STATE_FILE, "w") as f:
        json.dump(states, f, indent=4)

def reset_signal_states():
    """Reset all signals to False in the state file."""
    print("Resetting all signal states...")
    initial_state = {ticker: {"call": False, "put": False} for ticker in ticker_symbols}
    write_signal_states(initial_state)
    print("Signal states reset successfully.")

def hotkey_listener():
    """Threaded hotkey listener for Ctrl+Z."""
    while True:
        if keyboard.is_pressed('ctrl+z'):
            reset_signal_states()
            t.sleep(1)  # Prevent multiple resets on a single press

def send_email(subject, message):
    """Send an email with the given subject and message."""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        server.send_message(msg)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def calculate_ema(data, span):
    """Calculate Exponential Moving Average."""
    return data.ewm(span=span, adjust=False).mean()

def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calculate MACD and signal line."""
    macd = data.ewm(span=fast, adjust=False).mean() - data.ewm(span=slow, adjust=False).mean()
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calculate_swing_highs_lows(data, window=5):
    """
    Identify swing highs and swing lows by looking for local peaks and troughs.
    """
    highs = data['High']
    lows = data['Low']
    swing_highs = []
    swing_lows = []

    for i in range(window, len(data) - window):
        if highs[i] == max(highs[i - window:i + window + 1]):
            swing_highs.append(highs[i])
        if lows[i] == min(lows[i - window:i + window + 1]):
            swing_lows.append(lows[i])

    return sorted(set(swing_highs + swing_lows))

def find_nearest_level(levels, price):
    """
    Find the nearest support and resistance levels to the current price.
    """
    lower = max([lvl for lvl in levels if lvl <= price], default=None)
    higher = min([lvl for lvl in levels if lvl > price], default=None)
    return lower, higher

# Trading logic for each ticker
def fetch_and_analyze():
    states = read_signal_states()  # Read current signal states
    email_body = ""  # Accumulate email content here
    for symbol in states.keys():
        try:
            # Fetch historical data
            rolling_data = yf.download(symbol, period="1y", interval="1d")
            current_data = yf.download(symbol, period="7d", interval="1h")

            # Calculate support and resistance levels
            support_resistance = calculate_swing_highs_lows(rolling_data)

            # Calculate EMA and MACD on current data
            current_data['20_EMA'] = calculate_ema(current_data['Close'], span=20)
            current_data['50_EMA'] = calculate_ema(current_data['Close'], span=50)
            current_data['MACD'], current_data['Signal'] = calculate_macd(current_data['Close'])

            # Current price and nearest support/resistance
            current_price = current_data['Close'].iloc[-1]
            lower_level, higher_level = find_nearest_level(support_resistance, current_price)

            # Signal Logic
            call_buy_signal = False
            call_sell_signal = False
            put_buy_signal = False
            put_sell_signal = False

            if not states[symbol]["call"] and not states[symbol]["put"] and current_price > current_data['20_EMA'].iloc[-1] and current_data['MACD'].iloc[-1] > current_data['Signal'].iloc[-1]:
                call_buy_signal = True
                states[symbol]["call"] = True

            elif states[symbol]["call"] and current_price < current_data['50_EMA'].iloc[-1]:
                call_sell_signal = True
                states[symbol]["call"] = False

            elif not states[symbol]["put"] and current_price < current_data['20_EMA'].iloc[-1] and current_data['MACD'].iloc[-1] < current_data['Signal'].iloc[-1]:
                put_buy_signal = True
                states[symbol]["put"] = True

            elif states[symbol]["put"] and current_price > current_data['50_EMA'].iloc[-1]:
                put_sell_signal = True
                states[symbol]["put"] = False

            # Add formatted data for the email
            email_body += (
                f"Ticker: {symbol}\n"
                f"Current Price: {current_price:.2f}\n"
                f"Nearest Support: {lower_level}, Nearest Resistance: {higher_level}\n"
                f"50 EMA: {current_data['50_EMA'].iloc[-1]:.2f}\n"
                f"20 EMA: {current_data['20_EMA'].iloc[-1]:.2f}\n"
                f"MACD: {current_data['MACD'].iloc[-1]:.2f}, Signal: {current_data['Signal'].iloc[-1]:.2f}\n"
                f"Call Buy Signal: {call_buy_signal}, Call Sell Signal: {call_sell_signal}\n"
                f"Put Buy Signal: {put_buy_signal}, Put Sell Signal: {put_sell_signal}\n"
                f"{'-' * 50}\n"
            )

        except Exception as e:
            email_body += f"Error processing {symbol}: {e}\n{'-' * 50}\n"

    write_signal_states(states)  # Save updated states to file
    send_email("Trading Analysis Report", email_body)

# Schedule tasks
def schedule_tasks():
    print("Scheduling tasks...")
    schedule.every().monday.at("06:31").do(fetch_and_analyze)
    schedule.every().monday.at("10:31").do(fetch_and_analyze)
    schedule.every().tuesday.at("06:31").do(fetch_and_analyze)
    schedule.every().tuesday.at("10:31").do(fetch_and_analyze)
    schedule.every().wednesday.at("06:31").do(fetch_and_analyze)
    schedule.every().wednesday.at("10:31").do(fetch_and_analyze)
    schedule.every().thursday.at("06:31").do(fetch_and_analyze)
    schedule.every().thursday.at("10:31").do(fetch_and_analyze)
    schedule.every().friday.at("06:31").do(fetch_and_analyze)
    schedule.every().friday.at("10:31").do(fetch_and_analyze)

if __name__ == "__main__":
    threading.Thread(target=hotkey_listener, daemon=True).start()
    schedule_tasks()
    print("Running... Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        t.sleep(1)
