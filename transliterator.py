import re

# Mapping for Hindi consonants, vowels, matras to conversational Roman Hindi (Hinglish)
VOWELS = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
    'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
    'अं': 'an', 'अः': 'ah'
}

MATRAS = {
    'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
    'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
    'ं': 'n', 'ँ': 'n', 'ः': 'h', '्': ''
}

CONSONANTS = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
    'ष': 'sh', 'स': 's', 'ह': 'h',
    'क़': 'q', 'ख़': 'kh', 'ग़': 'gh', 'ज़': 'z', 'ड़': 'd',
    'ढ़': 'dh', 'फ़': 'f', 'य़': 'y', 'झ़': 'zh'
}

# Full dictionary for CBCS experiment terminology
COMMON_OVERRIDES = {
    'है': 'h',
    'हैं': 'hain',
    'ह': 'h',
    'को': 'ko',
    'का': 'ka',
    'की': 'ki',
    'के': 'ke',
    'कर': 'kr',
    'करना': 'krna',
    'करते': 'krte',
    'करता': 'krta',
    'रहा': 'raha',
    'रही': 'rhi',
    'रहे': 'rhe',
    'सिपाही': 'siphai',
    'पुलिस': 'police',
    'तैरक': 'tairak',
    'तैराक': 'tairak',
    'नाविक': 'navik',
    'नाभिक': 'navik',
    'भागते': 'bhagte',
    'भागता': 'bhagta',
    'भागती': 'bhagti',
    'दौड़': 'daud',
    'दौड़ा': 'dauda',
    'पकड़ने': 'pakadne',
    'पकड़': 'pakad',
    'पकड़ते': 'pakadte',
    'पकड़के': 'pakadke',
    'कोशिश': 'koshish',
    'कोसिस': 'koshish',
    'कुछिस': 'koshish',
    'एक': 'ek',
    'मार': 'maar',
    'मारा': 'mara',
    'मारे': 'mare',
    'मारने': 'marne',
    'माने': 'marne',
    'लात': 'laat',
    'गोली': 'goli',
    'गुली': 'goli',
    'धक्का': 'dhakka',
    'मुक्का': 'mukka',
    'मुक्के': 'mukke',
    'मुके': 'mukke',
    'छू': 'chu',
    'छुआ': 'chua',
    'खींच': 'kheech',
    'खींचता': 'kheechta',
    'खींचते': 'kheechte',
    'कुक': 'cook',
    'शेफ': 'chef',
    'बावर्ची': 'bawarchi',
    'बावरची': 'bawarchi',
    'बाबरची': 'bawarchi',
    'रसोइया': 'rasoyia',
    'रसोईया': 'rasoyia',
    'नर्तकी': 'nartaki',
    'नारदकी': 'nartaki',
    'नार्टकी': 'nartaki',
    'नार्थकी': 'nartaki',
    'नारथकी': 'nartaki',
    'नाटकी': 'nartaki',
    'साधु': 'sadhu',
    'आदमी': 'aadmi',
    'अदमी': 'aadmi',
    'व्यक्ति': 'vyakti',
    'महिला': 'mahila',
    'औरत': 'aurat',
    'लड़की': 'ldki',
    'लडकी': 'ldki',
    'सैनिक': 'sainik',
    'सैनिकों': 'sainikon',
    'डॉक्टर': 'doctor',
    'डाक्टर': 'doctor',
    'जज': 'jaj',
    'टीचर': 'teacher',
    'नन': 'nun',
    'चोर': 'chor',
    'चोड': 'chor',
    'आतंकवादी': 'aatankwadi',
    'आतंगवादी': 'aatankwadi',
    'आतंगवाती': 'aatankwadi',
    'आतंग': 'aatank',
    'रस्सी': 'rassi',
    'रसी': 'rassi',
    'प्याला': 'pyala',
    'कप': 'cup',
    'मग': 'mug',
    'केक': 'cake',
    'वेट्रेस': 'waitress'
}

# Phonetic corrections for common spoken fumbles / speech errors
PHONETIC_CORRECTIONS = {
    'चोड': 'चोर',
    'गुली': 'गोली',
    'कुछिस': 'कोशिश',
    'कोसिस': 'कोशिश',
    'माने': 'मारने',
    'अदमी': 'आदमी',
    'नाभिक': 'नाविक',
    'लक्री': 'लकड़ी',
    'बाबरची': 'बावर्ची',
    'बावरची': 'बावर्ची',
    'नारदकी': 'नर्तकी',
    'नार्थकी': 'नर्तकी',
    'नाटकी': 'नर्तकी',
    'आतंगवाती': 'आतंकवादी',
    'आतंगवादी': 'आतंकवादी',
    'रसी': 'रस्सी'
}

def hindi_to_roman(text):
    text = text.strip()
    # Normalize punctuation
    text = re.sub(r'[।,.?!;:"\']', ' ', text)
    words = text.split()
    roman_words = []
    
    # Context-aware pre-processing (e.g. "भागते वे" -> "भागते हुए")
    cleaned_words = []
    for i, w in enumerate(words):
        w_clean = w.strip()
        if w_clean in PHONETIC_CORRECTIONS:
            w_clean = PHONETIC_CORRECTIONS[w_clean]
        if w_clean == 'वे' and i > 0 and 'भाग' in words[i-1]:
            w_clean = 'हुए'
        cleaned_words.append(w_clean)
        
    for word in cleaned_words:
        if not word:
            continue
            
        if word in COMMON_OVERRIDES:
            roman_words.append(COMMON_OVERRIDES[word])
            continue
            
        # Transliterate character by character
        chars = list(word)
        res = []
        i = 0
        n = len(chars)
        while i < n:
            ch = chars[i]
            # Nukta handling
            if i + 1 < n and chars[i+1] == '़':
                comb = ch + '़'
                if comb in CONSONANTS:
                    base = CONSONANTS[comb]
                    i += 2
                    if i < n and chars[i] in MATRAS:
                        res.append(base + MATRAS[chars[i]])
                        i += 1
                    else:
                        res.append(base + ('a' if i < n else ''))
                    continue

            if ch in VOWELS:
                res.append(VOWELS[ch])
                i += 1
            elif ch in CONSONANTS:
                base = CONSONANTS[ch]
                i += 1
                if i < n and chars[i] in MATRAS:
                    matra = chars[i]
                    res.append(base + MATRAS[matra])
                    i += 1
                else:
                    # In Hindi, inherent 'a' is suppressed at the end of word (schwa deletion)
                    res.append(base + ('a' if i < n else ''))
            elif ch in MATRAS:
                res.append(MATRAS[ch])
                i += 1
            else:
                res.append(ch)
                i += 1
        
        rom = ''.join(res)
        # Normalize double letters
        rom = re.sub(r'aa+', 'aa', rom)
        rom = re.sub(r'ee+', 'ee', rom)
        rom = re.sub(r'oo+', 'oo', rom)
        roman_words.append(rom)
        
    sentence = ' '.join(roman_words).strip()
    return sentence[:1].upper() + sentence[1:] if sentence else ""

if __name__ == '__main__':
    samples = [
        "भागते वे नाविक को एक सिपाही पकड़ने की कोशिश कर रहा है",
        "एक जज एक नन को लाठी से मारने की कोशिश कर रहा है लकड़ी से",
        "एक सैनिक एक अदमी को मुक्का मार रहा है",
        "एक बावर्ची एक चोड को गोली मार रहा है"
    ]
    for s in samples:
        print(s, "->", hindi_to_roman(s))
