# AI-Powered Audiobook Generator

This is a work-in-progress Python application that converts ePub novels into AI-narrated audiobooks.

## Features
- Parses `.epub` files and extracts text content
- Uses **Natural Language Processing (NLP)** to detect dialogue and identify speakers
- Assigns unique AI-generated voices to characters and a narrator
- GUI built with **Tkinter** for easy use
- Text-to-speech powered by `pyttsx3` (offline TTS engine)

## Built With
- Python
- EbookLib
- NLTK
- pyttsx3
- Tkinter
- Regex / JSON

## Current Status
This project is still in development. 

Current Status:
- Converts epub into folder of txt files separated by chapter
- Identifies dialogue and attributes it accordingly by speaker
- Outputs the new chaptername_dialogue.txt

Future goals include:
- Better speaker attribution using character context
- Integration with more realistic AI voices (e.g. ElevenLabs or TTS APIs)
- Full audiobook export with chapter support
