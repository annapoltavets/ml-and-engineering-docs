import pandas as pd
def languages():
    lang_map = {
        "cs": "Czech",
        "da": "Danish",
        "de": "German",
        "el": "Greek",
        "en": "English",
        "es": "Spanish",
        "et": "Estonian",
        "fi": "Finnish",
        "fr": "French",
        "ga": "Irish",
        "he": "Hebrew",
        "hr": "Croatian",
        "hu": "Hungarian",
        "id": "Indonesian",
        "is": "Icelandic",
        "it": "Italian",
        "lt": "Lithuanian",
        "lv": "Latvian",
        "nl": "Dutch",
        "no": "Norwegian",
        "pl": "Polish",
        "pt": "Portuguese",
        "ro": "Romanian",
        "ru": "Russian",
        "sk": "Slovak",
        "sl": "Slovenian",
        "sq": "Albanian",
        "sr": "Serbian",
        "sv": "Swedish",
        "uk": "Ukrainian",
    }


    df_lang = pd.DataFrame(list(lang_map.items()), columns=["code", "language"])
    print(df_lang)
