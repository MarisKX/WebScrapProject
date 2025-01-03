import re


def clean_make(brand):
    """
    Remove unwanted words like 'Cars' from the brand name.
    """
    unwanted_words = {"cars"}  # Use lowercase since comparison is case-insensitive
    words = brand.split(" ")  # Split into words
    filtered_words = [word for word in words if word.lower() not in unwanted_words]
    return " ".join(filtered_words)


def clean_model(make, model_raw):
    """
    Clean the model by removing unwanted words, repeated make prefix if present,
    and applying proper casing. Only removes unwanted words if there are multiple words in the model name.
    """
    # Strip unwanted characters
    model_raw = model_raw.strip("()[]").strip()
    make_lower = make.lower()

    # List of unwanted words
    unwanted_words = {
        "v6",
        "3.0l",
        "8d",
        "8g",
        "sedan",
        "u9",
        "kompressor",
        "b",
        "executive",
        "cdi",
        "wagon",
        "reihe",
        "3dr",
        "e2",
        "c1.4nz",
        "stationwagen",
        "1yy07",
        "station",
        "1.6i",
        "aut",
        "saloon",
        "at",
        "6.9",
        "b6",
    }

    # Exception phrases that should not be split
    exceptions = {
        "wagon r",
        "6219 sedan",
        '88" stationwagon',
    }

    make_exceptions_to_keep = {
        "mini",
    }

    words = model_raw.split(" ")
    # Preserve exception phrases
    preserved_words = []
    i = 0
    while i < len(words):
        # Check if a phrase matches an exception
        phrase = " ".join(words[i : i + 2]).lower()  # Check two-word phrases
        if phrase in exceptions:
            preserved_words.append(phrase)  # Keep the exception phrase
            i += 2  # Skip the next word
        else:
            preserved_words.append(words[i])  # Otherwise, keep the word for now
            i += 1

    # Only filter unwanted words if there are multiple words in the model
    if len(preserved_words) > 1:
        filtered_words = [
            word for word in preserved_words if word.lower() not in unwanted_words
        ]
    else:
        filtered_words = preserved_words

    cleaned_model = " ".join(filtered_words)

    # Check if the cleaned model starts with the make
    cleaned_model_lower = cleaned_model.lower()

    if any(
        cleaned_model_lower.startswith(exception)
        for exception in make_exceptions_to_keep
    ):
        cleaned_model = cleaned_model_lower
    elif cleaned_model_lower.startswith(make_lower):
        # Remove the make and any extra spaces from the model
        cleaned_model = cleaned_model[len(make) :].strip()

    cleaned_model = cleaned_model.strip("()[]").strip()

    # Apply proper casing
    if len(cleaned_model) <= 3:
        cleaned_model = cleaned_model.upper()
    else:
        cleaned_model = cleaned_model.title()

    print(f"Cleaned model: '{model_raw}' -> '{cleaned_model}'")
    return cleaned_model


def clean_vehicle_category(raw_text):
    """
    Parse a raw text like 'Personenauto (M1)' or 'Enkeldeks (klasse III) (CQ)'
    into display_name and code.
    """
    # Match the last set of parentheses as the code
    match = re.match(r"(.+?)\s\(([^()]+)\)$", raw_text)
    if match:
        display_name = match.group(1).strip()
        code = match.group(2).strip()
        return display_name, code
    else:
        # Handle cases where the input format doesn't match
        return "Undefined", "NA"
