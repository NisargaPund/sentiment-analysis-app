from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer


LABELS = ["negative", "neutral", "positive"]


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / np.sum(e)


@dataclass
class SentimentResult:
    positive: float
    neutral: float
    negative: float

    def as_percentages(self) -> Dict[str, float]:
        return {
            "positive": round(self.positive * 100.0, 2),
            "neutral": round(self.neutral * 100.0, 2),
            "negative": round(self.negative * 100.0, 2),
        }


class TwitterRobertaSentiment:
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment") -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def predict_proba(self, text: str) -> Dict[str, float]:
        encoded = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        out = self.model(**encoded)
        scores = out.logits.detach().cpu().numpy()[0]
        probs = _softmax(scores)
        # Model order is: negative, neutral, positive
        return {LABELS[i]: float(probs[i]) for i in range(3)}
    
    def analyze_with_explanation(self, text: str) -> Dict:
        """Analyze text and provide explanation for the sentiment classification"""
        probs = self.predict_proba(text)
        
        # Determine dominant sentiment
        dominant = max(probs.items(), key=lambda x: x[1])
        dominant_label = dominant[0]
        confidence = dominant[1]
        
        # Extract key words (simple approach: look for sentiment indicators)
        words = text.lower().split()
        
        # Common positive words
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                         'love', 'best', 'awesome', 'brilliant', 'perfect', 'outstanding',
                         'positive', 'success', 'win', 'happy', 'joy', 'excited', 'proud']
        
        # Common negative words
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'disappointed',
                         'sad', 'angry', 'frustrated', 'failed', 'problem', 'issue', 'crisis',
                         'negative', 'worried', 'concerned', 'disaster', 'tragedy', 'loss']
        
        # Find sentiment words in the text
        found_positive = [w for w in words if any(pos in w for pos in positive_words)]
        found_negative = [w for w in words if any(neg in w for neg in negative_words)]
        
        # Generate explanation
        confidence_pct = round(confidence * 100, 1)
        
        if dominant_label == "positive":
            explanation = f"This news is classified as **Positive** with {confidence_pct}% confidence. "
            if found_positive:
                explanation += f"The text contains positive words like: {', '.join(set(found_positive[:5]))}. "
            explanation += "The overall tone and sentiment of the text indicates a favorable or optimistic perspective."
            
        elif dominant_label == "negative":
            explanation = f"This news is classified as **Negative** with {confidence_pct}% confidence. "
            if found_negative:
                explanation += f"The text contains negative words like: {', '.join(set(found_negative[:5]))}. "
            explanation += "The overall tone and sentiment of the text indicates an unfavorable or pessimistic perspective."
            
        else:  # neutral
            explanation = f"This news is classified as **Neutral** with {confidence_pct}% confidence. "
            explanation += "The text appears to be factual or balanced, without strong positive or negative emotional indicators. "
            if not found_positive and not found_negative:
                explanation += "No strong sentiment words were detected."
        
        return {
            "sentiment": dominant_label,
            "confidence": confidence_pct,
            "probabilities": {
                "positive": round(probs["positive"] * 100, 2),
                "neutral": round(probs["neutral"] * 100, 2),
                "negative": round(probs["negative"] * 100, 2),
            },
            "explanation": explanation,
            "key_words": {
                "positive": list(set(found_positive[:5])),
                "negative": list(set(found_negative[:5]))
            }
        }

    def aggregate(self, texts: List[str]) -> SentimentResult:
        if not texts:
            return SentimentResult(positive=0.0, neutral=0.0, negative=0.0)

        sums = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        for t in texts:
            p = self.predict_proba(t)
            for k in sums:
                sums[k] += p[k]

        n = float(len(texts))
        return SentimentResult(
            positive=sums["positive"] / n,
            neutral=sums["neutral"] / n,
            negative=sums["negative"] / n,
        )

