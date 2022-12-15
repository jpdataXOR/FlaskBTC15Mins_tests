from ccxt import kraken
from datetime import datetime, timedelta
from flask import Flask, render_template
import pytz
import requests

# Create a Flask app
app = Flask(__name__)


@app.route('/')
def index():
  # Create a Kraken client
  client = kraken()

  # Set the timeframe to 15 minutes
  timeframe = '15m'

  # Get the OHLC data for BTC
  ohlcv = client.fetch_ohlcv('BTC/USD', limit=200, timeframe=timeframe)
  #ohlcv = ohlcv[::-1]
  #print(ohlcv);
  #print(ohlc_to_heiken_ashi(ohlcv))
  trendChanges = detect_trend_change(ohlc_to_heiken_ashi(ohlcv),
                                     num_prev_candles=3)
  trendChanges = trendChanges[::-1]

  # Calculate the percentage change and "Up/Down" value for each candle

  return render_template('index.html', trendChanges=trendChanges)


###########################################


def ohlc_to_heiken_ashi(ohlc_array):
  # Initialize the Heiken Ashi array with the same shape as the OHLC array
  heiken_ashi_array = (ohlc_array)

  # Set the open price for the first candle in the Heiken Ashi array

  # Set the timestamp, open, high, low, and close prices, and volume data for each subsequent candle in the Heiken Ashi array
  for i in range(1, len(ohlc_array)):

    heiken_ashi_array[0][1] = (ohlc_array[i - 1][1] + ohlc_array[i - 1][4]) / 2

    heiken_ashi_array[i][4] = (ohlc_array[i][1] + ohlc_array[i][2] +
                               ohlc_array[i][3] + ohlc_array[i][4]) / 4

  # Return the Heiken Ashi array
  return heiken_ashi_array


def detect_trend_change(ohlc_array, num_prev_candles=2):
  # Initialize the trend variable with the value of the first candle's close price
  trendPrint = []
  trend = ohlc_array[0][4]

  # Get the time zone for AEST
  timezone = pytz.timezone("Australia/Sydney")

  # Iterate over the candles in the OHLC array
  for i in range(1, len(ohlc_array)):
    # Check if the current candle's close price is higher than the average of the previous num_prev_candles candles' close prices
   
    if ohlc_array[i][4] > sum(
      [ohlc_array[i - j][4]
       for j in range(1, num_prev_candles + 1)]) / num_prev_candles:
      # If the current candle's close price is higher than the average of the previous num_prev_candles candles' close prices,
      # check if the current trend is a downtrend
      if trend < 0:
        # If the current trend is a downtrend, print a message indicating that the trend has changed
        timestamp = ohlc_array[i][0]
        time = datetime.fromtimestamp(timestamp / 1000, tz=timezone)
        print(f"Trend changed at {time} to an uptrend")
        trendPrint.append(f"Trend changed at {time} to an uptrend")
        if i == len(ohlc_array) - 1:
          trendPrint.append("IFTTT")
          send_ifttt_alert(f"Trend changed at {time} to an uptrend")

      # Set the trend to an uptrend
      trend = 1
    # If the current candle's close price is lower than the average of the previous num_prev_candles candles' close prices,
    # check if the current trend is an uptrend
    elif ohlc_array[i][4] < sum(
      [ohlc_array[i - j][4]
       for j in range(1, num_prev_candles + 1)]) / num_prev_candles:
      if trend > 0:
        # If the current trend is an uptrend, print a message indicating that the trend has changed
        timestamp = ohlc_array[i][0]
        time = datetime.fromtimestamp(timestamp / 1000, tz=timezone)
        print(f"Trend changed at {time} to a downtrend")
        trendPrint.append(f"Trend changed at {time} to a downtrend")
        if i == len(ohlc_array) - 1:
          trendPrint.append("IFTTT")
          send_ifttt_alert(f"Trend changed at {time} to a downtrend")

      # Set the trend to a downtrend
      trend = -1
    # Check if the current candle is the last candle in the array

  return trendPrint


def is_timestamp_in_quadrant(variableTimestamp):
  # Get the current timestamp
  current_timestamp = datetime.now()

  # Get the current time quadrant (15 minutes)
  # For example, if the current time is 9:05, the time quadrant will be 9:00
  current_quadrant = current_timestamp.replace(
    minute=0, second=0,
    microsecond=0) + timedelta(minutes=15 * (current_timestamp.minute // 15))

  # Calculate the start and end of the 15-minute range
  start = current_quadrant - timedelta(minutes=7.5)
  end = current_quadrant + timedelta(minutes=7.5)

  print(str_to_datetime(start))
  print(str_to_datetime(end))

  # Check if the variable timestamp is within the 15-minute range
  if str_to_datetime(start) <= variableTimestamp <= str_to_datetime(end):
    return True
  else:
    return False


def str_to_datetime(value):
  # Use the strptime() method to parse the string and convert it to a datetime object
  return datetime.timestamp(value) * 1000


def send_ifttt_alert(message):
  # Set the IFTTT webhook URL
  ifttt_webhook_url = "https://maker.ifttt.com/trigger/{event}/with/key/{key}"

  # Set the event name and your IFTTT key
  event_name = "REPLIT_WEBHOOK"
  ifttt_key = "Z8c3ce6FYDdpqcBWVwJy4"

  # Format the webhook URL with the event name and IFTTT key
  url = ifttt_webhook_url.format(event=event_name, key=ifttt_key)

  # Set the payload for the IFTTT alert
  payload = {"value1": message}

  # Send the IFTTT alert
  #requests.post(url, json=payload)


######################################
app.run(host='0.0.0.0', port=81)
########################################
