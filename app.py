#!/usr/bin/env python3
"""
Meeting Translator - Corporate Speak Decoder
Translates what people say in meetings to what they actually mean
"""

import re
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Translation dictionary - phrase: [possible translations]
TRANSLATIONS = {
    # Classic corporate speak
    "let's circle back": [
        "I'm ignoring this for now",
        "I need time to come up with an excuse",
        "This is going in the 'never' pile",
    ],
    "circle back": [
        "revisit this when we've all forgotten about it",
        "procrastinate professionally",
    ],
    "let's take this offline": [
        "This is getting awkward and I want it to stop",
        "I don't want witnesses for what I'm about to say",
        "You're embarrassing yourself and I'm giving you an exit",
    ],
    "take this offline": [
        "stop talking about this in front of everyone",
        "we need to fight in private",
    ],
    "let's table this": [
        "I'm killing this idea but politely",
        "We'll never discuss this again",
        "This idea is going to die of natural causes",
    ],
    "great question": [
        "I don't know the answer",
        "I wasn't expecting you to push back",
        "I'm stalling while I make something up",
    ],
    "that's a great point": [
        "I hadn't thought of that and I'm slightly annoyed",
        "You just made my job harder",
        "This is going to derail my whole presentation",
    ],
    "per my last email": [
        "I already told you this, can you read?",
        "Check your inbox before wasting my time",
        "I'm creating a paper trail because I don't trust you",
    ],
    "as per my previous email": [
        "I'm documenting your incompetence",
        "Read. Your. Email.",
    ],
    "just to clarify": [
        "You clearly didn't understand what I said",
        "Let me speak more slowly",
        "I'm going to repeat myself but make it sound like your fault",
    ],
    "going forward": [
        "I'm pretending the past didn't happen",
        "Don't bring up our previous failures",
        "Let's all collectively agree to amnesia",
    ],
    "let's be strategic": [
        "I don't have a plan but I need to sound smart",
        "Let's overthink this instead of doing it",
        "I'm about to suggest something obvious but with more words",
    ],
    "synergy": [
        "I have no idea what I'm talking about",
        "buzzword filler, please ignore",
        "I read a business book from 2003",
    ],
    "deep dive": [
        "we're going to waste a lot of time on this",
        "I want to micromanage every detail",
        "prepare for a very long meeting",
    ],
    "bandwidth": [
        "time and energy (but make it corporate)",
        "I'm too busy (but can't say that)",
        "my capacity to care is at zero",
    ],
    "i don't have the bandwidth": [
        "I don't want to do this",
        "This is not my problem",
        "Please find someone else to bother",
    ],
    "quick sync": [
        "A meeting that will not be quick",
        "I have no idea what's going on and I'm panicking",
        "I need to appear busy",
    ],
    "quick chat": [
        "An uncomfortable conversation is coming",
        "You're about to get feedback you don't want",
        "This will not be quick",
    ],
    "touch base": [
        "Check if you've done your job",
        "I'm micromanaging but making it sound friendly",
        "I need something from you but I'm easing into it",
    ],
    "low-hanging fruit": [
        "The easy stuff you should have already done",
        "I'm going to take credit for obvious wins",
        "Let's do the minimum and call it strategy",
    ],
    "move the needle": [
        "Actually make a difference (unlikely)",
        "I need metrics that make me look good",
        "Do something that matters for once",
    ],
    "loop me in": [
        "I want to know everything but do nothing",
        "Add me to emails so I can feel important",
        "I have FOMO about work decisions",
    ],
    "keep me in the loop": [
        "I don't trust you to handle this",
        "CC me on everything",
        "I want plausible deniability",
    ],
    "let's align": [
        "I want you to agree with me",
        "I'm about to overrule you but collaboratively",
        "Your opinion is wrong but I'll pretend to consider it",
    ],
    "we're aligned": [
        "You've agreed to do what I want",
        "I've won this argument politely",
        "I'm declaring victory before you realize what happened",
    ],
    "let me push back": [
        "I disagree and I'm about to tell you why",
        "Your idea is bad and I have receipts",
        "Prepare for conflict but make it professional",
    ],
    "with all due respect": [
        "I'm about to be disrespectful",
        "You're wrong and I have opinions",
        "This is the professional version of 'no offense, but...'",
    ],
    "to be transparent": [
        "I'm about to tell you something you won't like",
        "Here comes the bad news",
        "I've been hiding something but now I have to share",
    ],
    "let's be honest": [
        "I'm about to be brutally honest and you might cry",
        "I've been diplomatic but I'm done",
        "Prepare for the truth you've been avoiding",
    ],
    "it is what it is": [
        "This situation sucks and there's nothing we can do",
        "I've given up but professionally",
        "Acceptance is the final stage of corporate grief",
    ],
    "we'll see": [
        "No, but I don't want to fight about it",
        "This is never happening",
        "I'm hoping you'll forget about this",
    ],
    "interesting": [
        "I completely disagree",
        "This is the worst idea I've heard today",
        "I'm processing how to diplomatically destroy this",
    ],
    "that's one way to look at it": [
        "That's the wrong way to look at it",
        "Allow me to correct you politely",
        "Your perspective is creative but incorrect",
    ],
    "i'll try": [
        "I will not try",
        "This is already a no",
        "I'm managing your expectations down to zero",
    ],
    "noted": [
        "I've heard you but I'm ignoring you",
        "Your input has been acknowledged and discarded",
        "This is going straight to my mental trash folder",
    ],
    "thanks for your input": [
        "I did not ask for this",
        "Your opinion is noted and will be ignored",
        "Please stop talking",
    ],
    "happy to help": [
        "I am not happy about this",
        "Adding this to my resentment collection",
        "I'm helping because I have to, not because I want to",
    ],
    "no worries": [
        "I'm definitely worried but it's fine",
        "This is going to be a problem later",
        "I'm absorbing your failure as my own",
    ],
    "sounds good": [
        "I stopped listening 30 seconds ago",
        "Whatever, fine",
        "I'm agreeing to end this conversation",
    ],
    "makes sense": [
        "I don't fully understand but I'm pretending I do",
        "I'm too tired to ask clarifying questions",
        "Sure, why not",
    ],
    "let me know if you have any questions": [
        "Please don't have questions",
        "Figure it out yourself",
        "I'm ending this conversation",
    ],
    "i'll get back to you": [
        "I'm hoping you forget about this",
        "I need to Google this first",
        "This is going to my 'maybe never' list",
    ],
}

# Sentence-ending patterns
TONE_SUFFIXES = {
    "...": " (said with dead eyes)",
    "!": " (forced enthusiasm)",
    ".": "",
}


def translate_phrase(text):
    """Translate corporate speak to real meaning."""
    text_lower = text.lower().strip()

    # Check for exact matches first
    for phrase, translations in TRANSLATIONS.items():
        if phrase in text_lower:
            return {
                "original": phrase,
                "translation": random.choice(translations),
                "confidence": random.randint(85, 99),
            }

    return None


def translate_text(text):
    """Translate a full text block."""
    results = []
    sentences = re.split(r"(?<=[.!?])\s+", text)

    for sentence in sentences:
        if not sentence.strip():
            continue

        translation = translate_phrase(sentence)
        if translation:
            results.append(
                {
                    "original": sentence,
                    "translated": translation["translation"],
                    "matched_phrase": translation["original"],
                    "confidence": translation["confidence"],
                }
            )
        else:
            results.append(
                {
                    "original": sentence,
                    "translated": None,
                    "matched_phrase": None,
                    "confidence": 0,
                }
            )

    return results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    results = translate_text(text)
    translated_count = len([r for r in results if r["translated"]])

    return jsonify(
        {
            "results": results,
            "summary": {
                "total_sentences": len(results),
                "translated": translated_count,
                "corporate_density": round(translated_count / max(len(results), 1) * 100),
            },
        }
    )


@app.route("/phrases")
def phrases():
    """Return all known phrases for reference."""
    all_phrases = []
    for phrase, translations in TRANSLATIONS.items():
        all_phrases.append({"phrase": phrase, "translations": translations})
    return jsonify({"phrases": all_phrases})


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Meeting Translator")
    print("=" * 50)
    print("\n  Decoding corporate speak at: http://localhost:5011")
    print("  Press Ctrl+C to stop\n")
    app.run(debug=True, port=5011)
