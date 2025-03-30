import spacy
import re

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def extract_dialogue(text):
    doc = nlp(text)
    dialogues = []
    
    # Regex to find quoted dialogue
    quote_pattern = r"[“\"'](.*?)[”\"']"
    sentences = list(doc.sents)  # Split text into sentences
    
    for i, sent in enumerate(sentences):
        sent_text = sent.text.strip()

        # Check if sentence contains dialogue
        matches = re.findall(quote_pattern, sent_text)
        if matches:
            speaker = None

            # Look for a speaker in the sentence (e.g., "said Frodo")
            for token in sent:
                if token.dep_ == "nsubj" and token.ent_type_ == "PERSON":
                    speaker = token.text
                    break
            
            # If no speaker in the same sentence, check the previous one
            if not speaker and i > 0:
                prev_sent = sentences[i - 1].text
                for token in nlp(prev_sent):
                    if token.dep_ == "nsubj" and token.ent_type_ == "PERSON":
                        speaker = token.text
                        break

            dialogues.append((matches[0], speaker or "Unknown"))

    return dialogues

# Test with sample text
text = """
‘Come!’ the Elves called to the hobbits. ‘Come! Now is the time for speech and merriment!’
Pippin sat up and rubbed his eyes. He shivered. ‘There is a fire in the hall, and food for hungry guests,’ said an Elf standing before him.
‘This is poor fare,’ they said to the hobbits; ‘for we are lodging in the greenwood far from our halls.’
‘It seems to me good enough for a birthday-party,’ said Frodo.
"""

# Extract dialogue
dialogues = extract_dialogue(text)

# Print results
for line, speaker in dialogues:
    print(f"{speaker}: \"{line}\"")
