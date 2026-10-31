import pyttsx3

engine = pyttsx3.init()
for idx, voice in enumerate(engine.getProperty('voices')):
    print(f"ID {idx}: {voice.id} - Nombre: {voice.name}")