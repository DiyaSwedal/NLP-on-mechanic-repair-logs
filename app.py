from flask import Flask, request, render_template
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

app = Flask(__name__)

nltk.download('punkt')
nltk.download('stopwords')

df = pd.read_csv("dataset.csv")
df.columns = df.columns.str.strip()

stop_words = set(stopwords.words('english'))

SYNONYMS = {
    "battery not working": "dead battery",
    "battery issue": "dead battery",
    "battery problem": "dead battery",
    "battery drained": "battery drainage",
    "brake issue": "brake noise",
    "brakes making noise": "brake noise",
    "car making noise": "exhaust noise",
    "engine getting hot": "engine overheating",
    "car overheating": "engine overheating",
    "overheating": "engine overheating",
    "check engine": "check engine light",
    "engine light on": "check engine light",
    "ac problem": "ac not cooling",
    "ac not cold": "ac not cooling",
    "wheel problem": "misaligned wheels",
    "alignment issue": "misalignment"
}

def normalize_text(text):
    text = str(text).lower().strip()
    for key, value in SYNONYMS.items():
        if key in text:
            text = value
    return text

def preprocess(text):
    words = word_tokenize(str(text).lower())
    filtered = [w for w in words if w.isalnum() and w not in stop_words]
    return set(filtered)

def simplify_log(user_input):
    user_input = normalize_text(user_input)
    user_words = preprocess(user_input)

    best_match = None
    max_score = 0

    for _, row in df.iterrows():
        problem = str(row['COMMON PROBLEM']).strip().lower()
        problem_words = preprocess(problem)

        score = len(user_words & problem_words)

        if user_input == problem:
            score += 5

        if score > max_score:
            max_score = score
            best_match = row

    if best_match is not None and max_score > 0:
        return {
            "problem": best_match['COMMON PROBLEM'],
            "solution": best_match['SOLUTION USED'],
            "company": best_match['VEHICAL COMPANY'],
            "score": max_score
        }

    return {
        "problem": "Not found",
        "solution": "No matching issue found. Please check manually.",
        "company": "Unknown",
        "score": 0
    }

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None

    if request.method == 'POST':
        log = request.form.get('log', '')
        vehicle = request.form.get('vehicle', '')

        match = simplify_log(log)

        result = {
            "vehicle": vehicle.upper(),
            "problem": match["problem"],
            "solution": match["solution"],
            "company": match["company"],
            "score": match["score"]
        }

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)