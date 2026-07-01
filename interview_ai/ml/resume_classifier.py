"""
ml/resume_classifier.py
TF-IDF + Logistic Regression classifier trained on real job_title_des.csv dataset.
2277 labelled JD samples across 15 normalised roles.
"""

import os, pickle, sys
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_score

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import get_training_corpus

_MODEL_DIR  = os.path.join(os.path.dirname(__file__), "..", "ml_models")
_MODEL_PATH = os.path.join(_MODEL_DIR, "classifier.pkl")
_ENC_PATH   = os.path.join(_MODEL_DIR, "label_enc.pkl")


def train_and_save() -> dict:
    os.makedirs(_MODEL_DIR, exist_ok=True)
    texts, labels = get_training_corpus()

    le = LabelEncoder()
    y  = le.fit_transform(labels)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=12000,
            sublinear_tf=True,
            min_df=2,
            strip_accents="unicode",
            analyzer="word",
        )),
        ("clf", LogisticRegression(
            C=4.0,
            max_iter=2000,
            solver="lbfgs",
            class_weight="balanced",
            random_state=42,
        )),
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, texts, y, cv=cv, scoring="accuracy")
    pipeline.fit(texts, y)

    with open(_MODEL_PATH, "wb") as f: pickle.dump(pipeline, f)
    with open(_ENC_PATH,   "wb") as f: pickle.dump(le, f)

    return {
        "cv_mean":   round(float(cv_scores.mean()), 4),
        "cv_std":    round(float(cv_scores.std()),  4),
        "n_samples": len(texts),
        "n_classes": len(le.classes_),
        "classes":   list(le.classes_),
    }


def load_model():
    if not (os.path.exists(_MODEL_PATH) and os.path.exists(_ENC_PATH)):
        train_and_save()
    with open(_MODEL_PATH, "rb") as f: pipeline = pickle.load(f)
    with open(_ENC_PATH,   "rb") as f: le       = pickle.load(f)
    return pipeline, le


def predict(text: str) -> dict:
    pipeline, le = load_model()
    proba   = pipeline.predict_proba([text])[0]
    top_idx = int(np.argmax(proba))

    role_key   = le.classes_[top_idx]
    confidence = float(proba[top_idx])

    top3_idx = np.argsort(proba)[::-1][:3]
    top3 = [{
        "role":        le.classes_[i],
        "probability": round(float(proba[i]), 4),
    } for i in top3_idx]

    all_probs = {le.classes_[i]: round(float(p), 4) for i, p in enumerate(proba)}

    return {
        "role":       role_key,
        "confidence": round(confidence, 4),
        "top3":       top3,
        "all_probs":  all_probs,
    }
