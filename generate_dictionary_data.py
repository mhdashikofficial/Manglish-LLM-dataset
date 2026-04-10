import json
import random

OUTPUT_FILE = "dictionary_training_data.json"
SYSTEM_PROMPT = "You are a friendly AI that speaks natural Malayalam and Manglish. Keep responses human-like, clear, and helpful."
TARGET_SIZE = 6000

# Tuples of (Manglish, Malayalam)
DICT_BASIC = [
    ("entha", "എന്താ"), ("poyi", "പോയി"), ("varunnu", "വരുന്നു"),
    ("sukhamaano", "സുഖമാണോ"), ("evide", "എവിടെ"), ("aaha", "ആഹാ"),
    ("illa", "ഇല്ല"), ("undu", "ഉണ്ട്"), ("aara", "ആരാ"),
    ("vannu", "വന്നു"), ("njan", "ഞാൻ"), ("nee", "നീ"),
    ("avide", "അവിടെ"), ("ivide", "ഇവിടെ"), ("eppozha", "എപ്പോഴാ"),
    ("innu", "ഇന്ന്"), ("nale", "നാളെ"), ("kazhinju", "കഴിഞ്ഞു"),
    ("enthukond", "എന്തുകൊണ്ട്"), ("samayam", "സമയം"),
    ("kaanam", "കാണാം"), ("parayu", "പറയൂ"), ("kelkam", "കേൾക്കാം"),
    ("vegam", "വേഗം"), ("pinnude", "പിന്നീട്"), ("sari", "ശരി"),
    ("athe", "അതെ"), ("urappit", "ഉറപ്പായിട്ടും"), ("venda", "വേണ്ട"),
    ("mathi", "മതി"), ("valare", "വളരെ"), ("manassilayi", "മനസ്സിലായി"),
    ("ishtayi", "ഇഷ്ടമായി"), ("nallathu", "നല്ലത്"), ("mosham", "മോശം"),
    ("kuzhappamilla", "കുഴപ്പമില്ല"), ("engane", "എങ്ങനെ"),
    ("adipoli", "അടിപൊളി"), ("kidilam", "കിടിലം"), ("polichu", "പൊളിച്ചു"),
    ("santhosham", "സന്തോഷം"), ("dukham", "ദുഃഖം"), ("deshyam", "ദേഷ്യം"),
    ("vannaalo", "വന്നാലോ"), ("nokkam", "നോക്കാം"), ("shramikam", "ശ്രമിക്കാം")
]

# Tuples of (Slang/Base, Variations/Meaning)
DICT_SLANG = [
    ("bro", "bro, macha, aliya"),
    ("machane", "aliya, bro, chank"),
    ("pwoli", "adipoli, kidilam, super"),
    ("set", "set aanu, ready, ok"),
    ("thug", "mass, pwoli"),
    ("choodavalle", "deshyapedalle, cool aavu"),
    ("theernnu", "poyi, shubham"),
    ("scene", "presnam, vishayam"),
    ("oomphi", "potti, tholvi"),
    ("shokam", "mosham, bore"),
    ("chali", "joke, thമാശ"),
    ("vibes", "mood, feel"),
    ("kidu", "kidilam, nallathu"),
    ("chunk", "best friend, macha"),
    ("scene contra", "valiya presnam")
]

# Meaning specific
DICT_MEANING = [
    ("poyi", "പോയി"), 
    ("santhosham", "സന്തോഷം (happy)"),
    ("urakkam", "ഉറക്കം (sleep)"),
    ("bhakshanam", "ഭക്ഷണം (food)"),
    ("vishakkunnu", "വിശക്കുന്നു (hungry)"),
    ("ariyaam", "അറിയാം (know)"),
    ("ariyilla", "അറിയില്ല (don't know)"),
    ("venda", "വേണ്ട (don't want)"),
    ("venam", "വേണം (want)"),
    ("ishtam", "ഇഷ്ടം (like)")
]

# Phrase mapping (English, Manglish, Malayalam)
DICT_PHRASES = [
    ("I am coming", "njan varunnu", "ഞാൻ വരുന്നു"),
    ("Where are you?", "nee evideya?", "നീ എവിടെയാ?"),
    ("Had your food?", "food kazhicho?", "ഭക്ഷണം കഴിച്ചോ?"),
    ("What are you doing?", "entha cheyyunne?", "എന്താ ചെയ്യുന്നേ?"),
    ("I don't know", "enikku ariyilla", "എനിക്ക് അറിയില്ല"),
    ("See you tomorrow", "nale kaanam", "നാളെ കാണാം"),
    ("Are you okay?", "kuzhappam onnum illallo?", "കുഴപ്പമൊന്നും ഇല്ലല്ലോ?"),
    ("Call me later", "pinne vilikko", "പിന്നെ വിളിക്കൂ"),
    ("I forgot", "njan marannu", "ഞാൻ മറന്നു"),
    ("Good morning", "suprabhatham / good morning", "സുപ്രഭാതം"),
    ("Thank you", "valare upakaram / thanks", "വളരെ നന്ദി"),
    ("Sorry", "kshamikanam / sorry", "ക്ഷമിക്കണം"),
    ("How much?", "ethraya?", "എത്രയാ?"),
    ("Let's go", "namukku pokaam", "നമുക്ക് പോകാം")
]

def generate_sample():
    dataset = []
    
    counts = {
        "m2m": int(TARGET_SIZE * 0.30),
        "mal2man": int(TARGET_SIZE * 0.30),
        "meanings": int(TARGET_SIZE * 0.15),
        "phrases": int(TARGET_SIZE * 0.15),
        "slang": int(TARGET_SIZE * 0.10)
    }
    
    # 1. Manglish -> Malayalam
    templates_m2m = [
        "'{word}' enna vakyathinte malayalam entha?",
        "how to say '{word}' in malayalam script?",
        "'{word}' malayalam font-il type cheyyamo?",
        "malayalam for '{word}'",
        "'{word}' engane malayalam aksharangalil ezhuthum?"
    ]
    for _ in range(counts["m2m"]):
        man, mal = random.choice(DICT_BASIC)
        temp = random.choice(templates_m2m).format(word=man)
        dataset.append([temp, mal])
        
    # 2. Malayalam -> Manglish
    templates_mal2man = [
        "'{word}' manglish-il ezhuthamo?",
        "type '{word}' in manglish",
        "how to write '{word}' in english letters?",
        "'{word}' adiyamo manglishil?",
        "manglish translation for '{word}'"
    ]
    for _ in range(counts["mal2man"]):
        man, mal = random.choice(DICT_BASIC)
        temp = random.choice(templates_mal2man).format(word=mal)
        dataset.append([temp, man])
        
    # 3. Word Meanings
    templates_meanings = [
        "'{word}' ennu paranjal entha artham?",
        "what is the meaning of '{word}'?",
        "'{word}' englishil entha?",
        "meaning of '{word}' in malayalam?",
        "entha '{word}' nn paranjal?"
    ]
    for _ in range(counts["meanings"]):
        man, mean = random.choice(DICT_MEANING)
        temp = random.choice(templates_meanings).format(word=man)
        ans = f"'{man}' ennu paranjal '{mean}' ennanu artham."
        dataset.append([temp, ans])
        
    # 4. Phrase Coverage
    templates_phrases_manglish = [
        "'{phrase}' manglish-il engane parayum?",
        "how to say '{phrase}' in manglish chat?",
        "translate '{phrase}' to manglish"
    ]
    templates_phrases_malayalam = [
        "'{phrase}' malayalam-il translate cheyyu",
        "'{phrase}' malayalam paranjal entha?"
    ]
    for _ in range(counts["phrases"]):
        eng, man, mal = random.choice(DICT_PHRASES)
        if random.random() > 0.5:
            temp = random.choice(templates_phrases_manglish).format(phrase=eng)
            dataset.append([temp, man])
        else:
            temp = random.choice(templates_phrases_malayalam).format(phrase=eng)
            dataset.append([temp, mal])

    # 5. Slang Forms
    templates_slang = [
        "'{word}' pole words entha?",
        "synonyms for '{word}' in manglish?",
        "'{word}' nte vere words parayu",
        "what are casual alternatives for '{word}' malayalam slang?"
    ]
    for _ in range(counts["slang"]):
        base, syns = random.choice(DICT_SLANG)
        temp = random.choice(templates_slang).format(word=base)
        dataset.append([temp, syns])

    # Shuffle to ensure randomness and structure the JSON
    random.shuffle(dataset)
    
    final_output = []
    for user_q, assistant_a in dataset:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_q},
            {"role": "assistant", "content": assistant_a}
        ]
        final_output.append({"messages": messages})
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
        
    print(f"Generated successfully: {len(final_output)} dictionary entries.")

if __name__ == "__main__":
    generate_sample()
