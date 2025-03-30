import re
import os
import time
import json
import nltk
import openai
import spacy
import ebooklib  # Import the full ebooklib package.
from ebooklib import epub
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from openai.error import RateLimitError

# Download NLTK's tokenizer if not already present.
nltk.download('punkt')

# Load spaCy's English model.
nlp = spacy.load("en_core_web_sm")

# Set your OpenAI API key.
openai.api_key = "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"  # Replace with your actual API key.

### FUNCTIONS FOR TEXT PROCESSING ###

def clean_paragraph(paragraph):
    """
    Cleans an individual paragraph: normalizes line breaks, removes stray newlines inside quotes,
    and collapses extra whitespace.
    """
    paragraph = re.sub(r'\r\n?', '\n', paragraph)
    paragraph = re.sub(r'([“"])\s*\n\s*', r'\1', paragraph)
    paragraph = re.sub(r'\s*\n\s*([”"])', r'\1', paragraph)
    paragraph = re.sub(r'\s+', ' ', paragraph).strip()
    return paragraph

def split_into_paragraphs(text):
    """
    Splits the raw text into paragraphs using two or more newlines as delimiters.
    """
    return re.split(r'\n\s*\n+', text)

def extract_dialogue_segments(paragraph):
    """
    Extracts all dialogue segments (text between quotes) from a paragraph.
    Returns a list of dialogue strings.
    """
    return re.findall(r'[“"](.+?)[”"]', paragraph)

def get_speaker_for_paragraph(paragraph, previous_paragraph=None, max_retries=5):
    """
    Uses GPT to determine the speaker for the dialogue in the given paragraph.
    Optionally prepends the previous paragraph (if available) to enrich context.
    The prompt instructs GPT to output only the speaker's full name exactly as it appears in the text.
    If it cannot be determined, it should output "Unknown".
    """
    context = ""
    if previous_paragraph:
        context = clean_paragraph(previous_paragraph) + " "
    context += clean_paragraph(paragraph)
    
    prompt = f"""You are a literary assistant specializing in dialogue attribution.
Read the following context from a novel. All dialogue in the following paragraph is spoken by the same character.
Using the context (which may include narrative, reporting verbs, and character descriptions), determine the speaker's full name as it appears in the text.
Output only the speaker's full name with no additional commentary. If you cannot determine the speaker, output "Unknown".

Context: {context}"""
    
    retries = 0
    wait_time = 60
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that extracts speaker attributions from dialogue."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=50
            )
            speaker = response.choices[0].message.content.strip()
            speaker = speaker.strip(' "\n')
            return speaker
        except RateLimitError:
            retries += 1
            print(f"Rate limit reached. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(wait_time)
            wait_time *= 2
    return "Unknown"

def process_text(text):
    """
    Processes the entire text:
      1. Splits the text into paragraphs.
      2. Cleans each paragraph.
      3. For each paragraph that contains dialogue, uses the previous paragraph (if available)
         plus the current paragraph as context to determine the speaker.
      4. Extracts each dialogue segment and outputs it on its own line with the determined speaker.
    Returns a string with one line per dialogue in the format:
        Speaker: "Dialogue"
    """
    paragraphs = split_into_paragraphs(text)
    results = []
    for idx, para in enumerate(paragraphs):
        clean_para = clean_paragraph(para)
        dialogues = extract_dialogue_segments(clean_para)
        if dialogues:
            prev_para = paragraphs[idx-1] if idx > 0 else None
            speaker = get_speaker_for_paragraph(clean_para, previous_paragraph=prev_para)
            for dialogue in dialogues:
                results.append(f"{speaker}: \"{dialogue}\"")
    return "\n".join(results)

### FUNCTIONS FOR EPUB CHAPTER EXTRACTION ###

def extract_chapters(epub_path, output_dir):
    """
    Extracts chapters from the given EPUB file. Saves each chapter as a separate text file
    in a folder named after the book (based on metadata or filename).
    Returns a tuple (book_folder, chapter_files) where chapter_files is a list of paths.
    """
    book = epub.read_epub(epub_path)
    
    metadata = book.get_metadata('DC', 'title')
    if metadata and len(metadata) > 0:
        base_title = metadata[0][0]
    else:
        base_title = os.path.splitext(os.path.basename(epub_path))[0]
    
    # Clean title for folder name.
    base_title = "".join(c for c in base_title if c.isalnum() or c in " _-").rstrip()
    
    book_folder = os.path.join(output_dir, base_title)
    os.makedirs(book_folder, exist_ok=True)
    
    chapter_num = 1
    chapter_files = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content()
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text(separator="\n")
            # Save chapter as a text file.
            chapter_filename = os.path.join(book_folder, f"{base_title}_Chapter_{chapter_num}.txt")
            with open(chapter_filename, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Saved {chapter_filename}")
            chapter_files.append(chapter_filename)
            chapter_num += 1
    return book_folder, chapter_files

### MAIN EXECUTION ###

if __name__ == "__main__":
    # Set the path to your EPUB file and the output directory.
    epub_path = "books/player-one.epub"  # Replace with the path to your EPUB file.
    output_dir = "BookText"       # Folder where chapter text files will be saved.
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract chapters from the EPUB.
    book_folder, chapter_files = extract_chapters(epub_path, output_dir)
    
    # Process each chapter: extract dialogue segments and assign speakers.
    for chapter_file in chapter_files:
        with open(chapter_file, "r", encoding="utf-8") as f:
            chapter_text = f.read()
        dialogue_output = process_text(chapter_text)
        output_filename = chapter_file.replace(".txt", "_dialogue.txt")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(dialogue_output)
        print(f"Processed dialogue saved to {output_filename}")
