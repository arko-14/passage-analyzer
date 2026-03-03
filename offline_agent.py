"""
Offline Agent Module

Provides passage analysis without external API dependencies:
- Word count: Exact count using regex tokenization
- Emotion detection: Lexicon-based with 600+ emotion words and intensity modifiers
- Summary: Extractive summarization using word frequency scoring
- Book identification: Keyword matching against classic literary works
"""
import re
from collections import Counter

# Regex patterns for text processing
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

# Common words to exclude from frequency analysis
STOPWORDS = {
    "the","a","an","and","or","but","if","then","so","because","of","to","in","on","for","with",
    "as","at","by","from","is","are","was","were","be","been","being","it","this","that",
    "i","you","he","she","they","we","my","your","his","her","their","not","no","do","does","did",
    "have","has","had"
}

# Emotion vocabulary for lexicon-based detection
EMOTION_LEXICON = {
    "joy": {
        "joy","joyful","joyous","happy","happiness","happily","happier","happiest",
        "delight","delighted","delightful","smile","smiled","smiling","smiles",
        "laugh","laughed","laughing","laughter","laughs","grin","grinned","grinning",
        "love","loved","loving","loves","beloved","adore","adored","adoring",
        "hope","hopeful","hoping","hopes","hoped",
        "peace","peaceful","peacefully","calm","calming","serene","tranquil",
        "wonder","wonderful","wonderfully","wondrous","awe","awesome","awed",
        "bright","brighter","brightest","brightness","radiant","radiance","glow","glowing",
        "beautiful","beauty","beautifully","gorgeous","lovely","prettiest",
        "blessing","blessed","bliss","blissful","blissfully",
        "freedom","free","freed","liberating","liberated","liberation",
        "warm","warmth","warmly","warmer","cozy",
        "kind","kindness","kindly","kinder","kindest","compassion","compassionate",
        "gentle","gently","gentleness","tender","tenderly","tenderness",
        "gratitude","grateful","gratefully","thankful","thanks","appreciate","appreciated",
        "celebrate","celebrated","celebrating","celebration","celebrations","celebratory",
        "proud","proudly","pride","triumph","triumphant","victory","victorious",
        "excited","exciting","excitement","thrilled","thrilling","thrill",
        "cheerful","cheery","merry","merriment","jolly","gleeful","glee",
        "content","contented","contentment","satisfied","satisfaction","fulfillment","fulfilled",
        "optimistic","optimism","enthusiasm","enthusiastic","eager","eagerly","eagerness",
        "pleasure","pleasant","pleasantly","pleasing","pleased","enjoy","enjoyed","enjoying","enjoyment",
        "amused","amusing","amusement","fun","funny","hilarious","humor","humorous",
        "ecstatic","ecstasy","elated","elation","euphoric","euphoria","jubilant","jubilation",
        "affection","affectionate","affectionately","caring","cared","heartwarming",
        "inspired","inspiring","inspiration","inspirational","uplifting","uplifted",
        "relieved","relief","reassured","reassuring","comfort","comfortable","comforting","comforted",
    },
    "sadness": {
        "sad","sadness","sadly","sadder","saddest","saddened","saddening",
        "cry","cried","crying","cries","weep","wept","weeping","weeps",
        "tears","tearful","tearfully","teary",
        "lonely","loneliness","alone","lonesome","isolated","isolation","solitary","solitude",
        "grief","grieving","grieved","grieve","grieves","grievous",
        "sorrow","sorrowful","sorrowfully","sorrows",
        "empty","emptiness","void","hollow","hollowness",
        "broken","brokenhearted","heartbroken","heartbreak","heartbreaking",
        "regret","regretful","regretfully","regrets","regretted","regretting",
        "mourn","mourning","mourned","mourns","mourner",
        "heartache","ache","aching","ached",
        "despair","despairing","despaired","desperate","desperately","desperation",
        "hopeless","hopelessness","helpless","helplessness","helplessly",
        "miserable","miserably","misery","wretched","wretchedness",
        "depressed","depressing","depression","depressive","dejected","dejection",
        "melancholy","melancholic","gloom","gloomy","gloominess","somber","somberly",
        "unhappy","unhappily","unhappiness","dissatisfied","dissatisfaction",
        "disappointed","disappointing","disappointment","letdown",
        "hurt","hurting","hurts","wounded","wounding",
        "painful","painfully","anguish","anguished","agony","agonizing",
        "suffering","suffered","suffers","suffer",
        "bereaved","bereavement","loss","lost","losing",
        "miss","missed","missing","misses","longing","yearning","yearned",
        "blue","blues","downcast","downhearted","disheartened","crestfallen",
        "forlorn","desolate","desolation","bleak","bleakness",
        "tragic","tragedy","tragedies","tragically","lament","lamented","lamenting",
    },
    "anger": {
        "anger","angry","angrily","angrier","angriest","angered",
        "rage","raging","raged","rages","enraged","enraging","outrage","outraged","outrageous",
        "furious","furiously","fury","fuming","fumed",
        "hate","hated","hating","hates","hatred","hateful","loathe","loathed","loathing",
        "bitter","bitterly","bitterness","resentment","resent","resented","resentful",
        "wrath","wrathful","wrathfully",
        "mad","madder","maddest","madly","maddening","maddened",
        "irritated","irritating","irritation","irritable","annoyed","annoying","annoyance",
        "cruel","cruelly","cruelty","brutal","brutally","brutality","savage","savagely",
        "hostile","hostility","hostilely","aggressive","aggressively","aggression",
        "frustrated","frustrating","frustration","exasperated","exasperating","exasperation",
        "infuriated","infuriating","incensed",
        "vengeful","vengeance","revenge","vindictive","vindictiveness","spite","spiteful",
        "contempt","contemptuous","contemptuously","scorn","scornful","scornfully",
        "indignant","indignation","offended","offensive",
        "seething","seethe","seethed","livid",
        "irate","wroth","choleric","belligerent","bellicose",
        "ferocious","ferociously","ferocity","fierce","fiercely","fierceness",
        "violent","violently","violence","vicious","viciously","viciousness",
        "defiant","defiance","defiantly","rebellious","rebellion",
        "rant","ranting","ranted","rants","yell","yelled","yelling","shout","shouted","shouting",
    },
    "fear": {
        "fear","feared","fearing","fears","fearful","fearfully","fearsome",
        "afraid","unafraid",
        "terror","terrified","terrifying","terrorized","terrorizing","terrible","terribly",
        "panic","panicked","panicking","panics","panicky",
        "scared","scares","scaring","scary","scarier","scariest",
        "anxious","anxiously","anxiety","anxieties",
        "danger","dangerous","dangerously","endangered","endangering",
        "threat","threatened","threatening","threats","threaten",
        "horror","horrified","horrifying","horrible","horribly","horrendous",
        "dread","dreaded","dreading","dreadful","dreadfully",
        "worry","worried","worrying","worries","worrisome",
        "nervous","nervously","nervousness","nerves",
        "frightened","frightening","frighten","frightens","fright","frightful",
        "alarmed","alarming","alarm","alarms",
        "apprehensive","apprehension","apprehensively",
        "uneasy","uneasiness","unease","disquiet","disquieting",
        "distressed","distressing","distress",
        "petrified","paralyzed","frozen","trembling","trembled","tremble","shaking","shook","shiver","shivering",
        "nightmare","nightmarish","nightmares",
        "haunted","haunting","haunt","haunts",
        "creepy","creeping","creep","eerie","eerily",
        "sinister","ominous","ominously","foreboding",
        "phobia","phobic","paranoid","paranoia",
        "coward","cowardly","cowardice","timid","timidly","timidity",
        "insecure","insecurity","insecurities","vulnerable","vulnerability",
        "menace","menacing","menacingly",
        "intimidate","intimidated","intimidating","intimidation",
    },
    "disgust": {
        "disgust","disgusted","disgusting","disgustingly",
        "filthy","filth","filthiness",
        "nasty","nastier","nastiest","nastiness",
        "repulsive","repulsed","repulsion","repugnant","repugnance",
        "rotten","rotting","rot","rotted","decay","decayed","decaying",
        "vile","vileness","viler","vilest",
        "gross","grossed","grossly","grossness",
        "sickening","sickened","sicken","sickens",
        "revolting","revolted","revolt","revulsion",
        "nauseating","nauseated","nausea","nauseous",
        "abhorrent","abhor","abhorred","abhorrence",
        "loathsome","detestable","detested","detestation",
        "foul","fouler","foulest","foulness",
        "putrid","putrescence","stench","stink","stinking","stinky","smelly",
        "offensive","offensively","offensiveness",
        "distasteful","distaste",
        "unpleasant","unpleasantly","unpleasantness",
        "yuck","yucky","ew","eww","ugh","ick","icky",
        "contaminated","contamination","contaminate","polluted","pollution",
        "corrupt","corrupted","corruption","corrupting",
        "obscene","obscenity","indecent","indecency",
        "despicable","deplorable","abominable","odious",
        "squalid","squalor","grimy","grime","muck","mucky","scummy",
        "sleazy","sleaziness","slimy","sliminess",
    },
    "surprise": {
        "surprise","surprised","surprising","surprisingly","surprises",
        "astonished","astonishing","astonishment","astonishingly",
        "amazed","amazing","amazingly","amazement",
        "unexpected","unexpectedly",
        "shock","shocked","shocking","shockingly","shocks",
        "startled","startling","startle","startles",
        "incredible","incredibly","unbelievable","unbelievably",
        "stunned","stunning","stunningly","stun","stuns",
        "astounded","astounding","astoundingly",
        "speechless","dumbfounded","dumbstruck","flabbergasted",
        "bewildered","bewildering","bewilderment",
        "perplexed","perplexing","perplexity",
        "baffled","baffling","baffle",
        "disbelief","unbelief",
        "sudden","suddenly","abrupt","abruptly",
        "whoa","wow","gasp","gasped","gasping",
        "extraordinary","extraordinarily",
        "remarkable","remarkably",
        "unforeseen","unanticipated",
        "revelation","revelations","reveal","revealed","revealing",
        "aghast","taken aback",
        "miraculous","miraculously","miracle",
    },
}

# Intensity modifiers
INTENSIFIERS = {"very","extremely","incredibly","absolutely","totally","completely","utterly","deeply","profoundly","terribly","awfully","really","so","such","truly","genuinely"}
DIMINISHERS = {"slightly","somewhat","a bit","kind of","sort of","barely","hardly","scarcely","little","mildly"}

BOOK_HINTS = {
    "The Alchemist — Paulo Coelho": {"dream","dreams","destiny","journey","soul","treasure","omen","omens","desert","legend","heart","personal","shepherd","Santiago","caravan","oasis","pyramids","universe","maktub"},
    "Man's Search for Meaning — Viktor Frankl": {"meaning","suffering","purpose","camp","camps","freedom","choice","dignity","logotherapy","prisoner","prisoners","Auschwitz","survive","psychological","existence","responsibility"},
    "To Kill a Mockingbird — Harper Lee": {"trial","court","judge","jury","town","race","racial","justice","Atticus","Scout","Finch","Maycomb","Alabama","mockingbird","innocent","Boo","Radley","Tom","Robinson"},
    "Pride and Prejudice — Jane Austen": {"marriage","estate","gentleman","lady","ball","Darcy","Elizabeth","Bennet","pride","prejudice","society","manners","courtship"},
    "1984 — George Orwell": {"party","Big Brother","Winston","thoughtcrime","telescreen","ministry","Oceania","freedom","slavery","war","peace","surveillance","doublethink"},
    "The Great Gatsby — F. Scott Fitzgerald": {"Gatsby","Daisy","Nick","West Egg","mansion","party","parties","wealth","green light","jazz","roaring","American dream"},
    "Jane Eyre — Charlotte Brontë": {"Jane","Rochester","Thornfield","governess","orphan","Lowood","attic","Bertha","moor","independence","passion"},
    "Wuthering Heights — Emily Brontë": {"Heathcliff","Catherine","Cathy","moors","revenge","ghost","Linton","Earnshaw","passion","wild","storm"},
    "Crime and Punishment — Fyodor Dostoevsky": {"Raskolnikov","murder","guilt","confession","redemption","Petersburg","axe","pawnbroker","Sonya","conscience"},
    "The Catcher in the Rye — J.D. Salinger": {"Holden","phony","phonies","Caulfield","Phoebe","childhood","innocence","Central Park","ducks","museum"},
}

def _tokenize(text: str):
    return [w.lower() for w in WORD_RE.findall(text or "")]

def _sentences(text: str):
    t = (text or "").strip()
    if not t:
        return []
    return [s.strip() for s in SENT_SPLIT_RE.split(t) if s.strip()]

def word_count(text: str) -> int:
    """Count total words in text."""
    return len(_tokenize(text))


def emotion(text: str):
    """Analyze and return the predominant emotion in the text."""
    words = _tokenize(text)
    
    scores = {e: 0.0 for e in EMOTION_LEXICON}
    
    # Analyze with context awareness (check for intensifiers)
    for i, w in enumerate(words):
        for emo, vocab in EMOTION_LEXICON.items():
            if w in vocab:
                # Base score
                base_score = 1.0
                
                # Check for intensifiers in nearby words (within 3 words before)
                for j in range(max(0, i-3), i):
                    if words[j] in INTENSIFIERS:
                        base_score = 1.5  # Boost score
                        break
                    elif words[j] in DIMINISHERS:
                        base_score = 0.5  # Reduce score
                        break
                
                scores[emo] += base_score

    # Normalize and sort
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_emo, top_val = sorted_scores[0]
    
    # Convert scores to int for display
    int_scores = {e: int(round(s)) for e, s in scores.items()}

    # No emotion detected
    if top_val == 0:
        return "neutral", int_scores, 0.0

    # Calculate confidence based on margin between top and second
    total_emotion = sum(scores.values())
    if total_emotion > 0:
        # Confidence = how dominant is the top emotion
        conf = top_val / total_emotion
    else:
        conf = 0.0
    
    return top_emo, int_scores, float(conf)

def summary(text: str, max_sentences: int = 3) -> str:
    """
    Generate extractive summary by selecting most important sentences.
    
    Uses word frequency to score sentences - sentences with more
    frequent (important) words get higher scores.
    
    Args:
        text: The passage to summarize
        max_sentences: Maximum sentences to include (default: 3)
        
    Returns:
        Summary string with top sentences in original order
    """
    sents = _sentences(text)
    if not sents:
        return ""
    if len(sents) <= max_sentences:
        return " ".join(sents)

    words = [w for w in _tokenize(text) if w not in STOPWORDS]
    if not words:
        return " ".join(sents[:max_sentences])

    freq = Counter(words)
    scored = []
    for i, s in enumerate(sents):
        sw = [w for w in _tokenize(s) if w not in STOPWORDS]
        score = sum(freq.get(w, 0) for w in sw) / max(1, len(sw))
        scored.append((i, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    chosen = sorted([i for i, _ in scored[:max_sentences]])
    return " ".join(sents[i] for i in chosen)

def possible_books(text: str, top_k: int = 3):
    """
    Identify possible source books using keyword matching.
    
    Compares text against known book vocabularies and returns
    books with most keyword matches.
    
    Args:
        text: The passage to analyze
        top_k: Number of book suggestions to return
        
    Returns:
        List of book titles (with authors)
    """
    words = set(_tokenize(text))
    scored = []
    for book, kws in BOOK_HINTS.items():
        scored.append((book, len(words & kws)))
    scored.sort(key=lambda x: x[1], reverse=True)
    out = [b for b, s in scored[:top_k] if s > 0]
    return out if out else [b for b, _ in scored[:top_k]]

def run_offline(text: str):
    """
    Run complete offline analysis on text.
    
    Args:
        text: The passage to analyze
        
    Returns:
        Dict with word_count, predominant_emotion, emotion_scores,
        emotion_confidence, possible_books, and summary
    """
    wc = word_count(text)
    emo, emo_scores, emo_conf = emotion(text)
    summ = summary(text, max_sentences=3)
    books = possible_books(text, top_k=3)

    return {
        "word_count": wc,
        "predominant_emotion": emo,
        "emotion_scores": emo_scores,
        "emotion_confidence": emo_conf,
        "possible_books": books,
        "summary": summ,
    }