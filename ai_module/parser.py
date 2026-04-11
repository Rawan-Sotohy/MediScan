import re
from typing import List, Dict


FREQUENCY_PATTERNS = {
    "once daily":        ["once daily", "once a day", "1 time", "od", "q24h"],
    "twice daily":       ["twice daily", "twice a day", "2 times", "bid", "bd", "q12h"],
    "three times daily": ["three times", "3 times", "tid", "tds", "q8h"],
    "four times daily":  ["four times", "4 times", "qid", "q6h"],
    "every morning":     ["every morning", "in the morning", "morning"],
    "every night":       ["every night", "at night", "bedtime", "nocte"],
}

DOSAGE_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*(mg|mcg|ml|g|iu|units?)', re.IGNORECASE
)

DURATION_PATTERN = re.compile(
    r'(\d+)\s*(day|days|week|weeks|month|months)', re.IGNORECASE
)


def extract_frequency(text: str) -> str:
    text_lower = text.lower()
    for standard_freq, variants in FREQUENCY_PATTERNS.items():
        for variant in variants:
            if variant in text_lower:
                return standard_freq
    return "as directed"


def extract_dosage(text: str) -> str:
    match = DOSAGE_PATTERN.search(text)
    if match:
        return match.group(0)
    return "see prescription"


def extract_duration(text: str) -> str:
    match = DURATION_PATTERN.search(text)
    if match:
        number = match.group(1)
        unit = match.group(2).lower()
        if not unit.endswith('s'):
            unit += 's'
        return f"{number} {unit}"
    return "as directed"


def correct_medication_name(name: str) -> str:
    """
    Uses Groq to correct OCR medication name errors
    """
    try:
        from groq import Groq
        import os
        
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a medical expert. 
You will receive a medication name that was extracted from a handwritten prescription using OCR.
The name might have OCR errors.
Your job is to return ONLY the correct medication name, nothing else.
If you're not sure, return the original name.
Return only the medication name, no explanation."""
                },
                {
                    "role": "user",
                    "content": f"Correct this medication name: {name}"
                }
            ],
            max_tokens=20
        )
        
        corrected = response.choices[0].message.content.strip()
        return corrected
        
    except Exception:
        return name
     

def parse_medications(raw_text: str) -> List[Dict]:
    """
    Takes raw OCR text and returns a list of structured medications
    """
    medications = []
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    for line in lines:
        # Skip very short lines
        if len(line) < 2:
            continue

        # Skip lines that are just numbers or symbols
        if re.match(r'^[\d\s\.\,\-]+$', line):
            continue

        dosage = extract_dosage(line)
        frequency = extract_frequency(line)
        duration = extract_duration(line)

        # Extract medicine name
        name_match = re.split(r'\d', line)
        med_name = name_match[0].strip().rstrip(',').strip() if name_match else line

        # If name is empty, use the whole line
        if not med_name:
            med_name = line.strip()


        corrected_name = correct_medication_name(med_name)
        medications.append({
            "name": corrected_name,
            "dosage": dosage,
            "frequency": frequency,
            "duration": duration,
        })

    return medications