from elevenlabs import voices, generate

voices = voices()
# audio = generate(text="Hello there!", voice=voices[0])
for voice in voices.voices:
    if voice.labels['accent'] == 'british':
        print(voice.name)
print(len(voices.voices))