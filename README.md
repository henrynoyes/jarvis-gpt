# JARVIS-GPT

<div align='center'>

<img src='media/jarvis_logo.png' height='200'> <img src='media/stark.gif' height=200>

</div>


## Description

JARVIS-GPT is a personal project with the aim of replicating the functionality of Just A Rather Very Intelligent System (J.A.R.V.I.S.) from the Iron Man movies. With recent advancements in deep learning and natural language processing, technologies that were often portrayed as futuristic in Hollywood movies (think JARVIS from Iron Man, C-3PO from Star Wars, etc.) are becoming a reality. Inspired by [Boston Dynamic's integration of ChatGPT on their Spot robot](https://bostondynamics.com/blog/robots-that-can-chat/), I designed a framework that uses high-level API calls to emulate the capabilites of the fictional JARVIS system.

In addition to the conversational abilities of OpenAI's GPT models, JARVIS-GPT takes advantage of [function calling](https://platform.openai.com/docs/guides/function-calling) to perform other actions such as,
- Accessing the current date and time
- Accessing the current weather conditions at any location
- Accessing the daily weather forecast up to 8 days in the future at any location
- Reading, writing, and deleting notes organized by date and time 

And perhaps it is just a glorified DIY Alexa... but at least, in my opinion, it looks and sounds cool in the process :D


## Hardware

The main hardware consists of a Raspberry Pi 4B with a [Respeaker 4-mic Array Hat](https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/) for audio detection. These components are stored in a 3D-printed enclosure mounted on the ceiling, with openings for the LEDs. The GPIO port on the hat is connected to an external push button for activation. The audio is output through the 3.5mm jack to an amplifier that is connected to two wall-mounted speakers.


## Software

Main Packages:
- [SpeechRecognition](https://github.com/Uberi/speech_recognition#readme)
- [OpenAI](https://platform.openai.com/docs/introduction)
- [ElevenLabs](https://github.com/elevenlabs/elevenlabs-python)
- [PyOWM](https://pyowm.readthedocs.io/en/latest/) for [OpenWeatherMap](https://openweathermap.org/api)

Each time JARVIS is activated, [featurized_stream.py](https://github.com/henrynoyes/jarvis-gpt/tree/master/featurized_stream.py) listens for speech, translates the speech to text, queries GPT with the text, performs any necessary function calling, and finally converts the text response to speech in a custom JARVIS voice. The framework was designed to be as simple as possible in the hopes that others can easily interpret the code and make their own modifications if desired.

To ensure privacy, all personal information such as API keys are stored locally in environment variables and accessed using [os](https://docs.python.org/3/library/os.html). See [OpenAI's API Key Guide](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) for instructions on how to set environment variables on Linux/Windows/MacOS. Here is a list of all custom environment variables:

- OPENAI_API_KEY - Used for all queries to GPT models. Find it [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-api-key)
- ELEVEN_API_KEY - Used for all TTS. Find it [here](https://elevenlabs.io/docs/api-reference/text-to-speech#authentication)
- OWM_API_KEY - Used for the `get_current_weather` and `get_future_weather` functions. Find it [here](https://openweathermap.org/appid#signup)
- JARVIS_LOCATION - Used as the default location for the `get_current_weather` and `get_future_weather` functions. In the form `'city,state,US'` for US cities and `'city,country'` for elsewhere. Ex: `'Phoenix,AZ,US'` or `'London,GB'`
- JARVIS_VOICEID - Used for all TTS. Find the list of voices [here](https://github.com/elevenlabs/elevenlabs-python/blob/main/API.md#voices-1).


## Future Developments

- Add option for always on + wake word (activate with "Hey JARVIS ...")
- Connect to light display and have JARVIS turn on/turn off/change colors
- Allow multiple exchanges with historical context, more like ChatGPT (ex: "Read me my notes from yesterday" $\rightarrow$ "Delete the second one")
- Replace startup mp3 with custom message detailing date, time, and weather
- Replace local notetaking functionality with a cloud-based application that can be accessed from other devices (mobile/PC)
