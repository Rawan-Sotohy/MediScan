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


def parse_medications(raw_text: str) -> List[Dict]:
    """
    Takes raw OCR text and returns a list of structured medications
    """
    medications = []
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    for line in lines:
        if len(line) < 3:
            continue

        dosage = extract_dosage(line)
        frequency = extract_frequency(line)
        duration = extract_duration(line)

        name_match = re.split(r'\d', line)
        med_name = name_match[0].strip().rstrip(',').strip() if name_match else line

        if not med_name or med_name.isdigit():
            continue

        medications.append({
            "name": med_name,
            "dosage": dosage,
            "frequency": frequency,
            "duration": duration,
        })

    return medications