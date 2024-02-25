from submain import MorningJarvis, Notifetcher
import json

jv = MorningJarvis()
nf = Notifetcher()

dt = json.dumps(jv.get_current_datetime())

forecast = json.dumps(jv.get_future_weather(0))

notifs = json.dumps(nf.fetch())

text = f'Generate a natural good morning message from this data: {dt} {forecast} {notifs}.  Round measurements to the nearest integer. \
            Please include the high and low temperatures for the day, the feels like temperature for the day, and the weather status. \
            Please include the wind speed and gust speed. \
            Please exclude the humidity, pressure, visibility distance, and viewpoint. \
            Please ensure that instead of abbreviating "miles per hour" as "mph", use the full phrase "miles per hour". \
            Please ensure that temperatures are represented using the word "degrees" instead of the degree symbol (°). \
            Please include a summary of the notifications in a natural format. \
            Please mention the total number of notifications. \
            End the message with some words of motivation.'

jv.run(text)