from dataclasses import dataclass
from typing import Literal

@dataclass
class DecisionResult:
    status: Literal['real', 'fake', 'uncertain']
    confidence: float
    reasoning: str

class DecisionEngine:
    def __init__(self):
        self.thresholds = {
            'high_similarity': 0.70,
            'high_credibility': 0.85,
            'min_sources': 2,
        }

    def decide(
        self,
        similarity_score: float,
        credibility_score: float,
        source_count: int,
        top_source_credibility: float,
        has_high_cred_source: bool = False
    ) -> DecisionResult:
        if has_high_cred_source and source_count >= 1:
            confidence = min(1.0, 0.9 + (credibility_score / 10))
            return DecisionResult(
                status='real',
                confidence=confidence,
                reasoning="At least one high-credibility source confirms this claim",
            )
        if (
            similarity_score >= self.thresholds['high_similarity']
            and credibility_score >= self.thresholds['high_credibility']
            and source_count >= self.thresholds['min_sources']
        ):
            confidence = min(1.0, 0.8 + (similarity_score + credibility_score) / 10)
            return DecisionResult(
                status='real',
                confidence=confidence,
                reasoning="Multiple high-credibility sources confirm this claim",
            )

        if similarity_score < 0.30 and (top_source_credibility < 0.70) and source_count < 2:
            confidence = min(1.0, 0.7 + (0.3 - similarity_score) / 2)
            return DecisionResult(
                status='fake',
                confidence=confidence,
                reasoning="Low similarity to credible sources suggests the claim is likely false",
            )

        confidence = max(0.4, min(0.7, 0.4 + (similarity_score + credibility_score) / 4))
        return DecisionResult(
            status='uncertain',
            confidence=confidence,
            reasoning="Insufficient or mixed evidence to make a definitive determination",
        )
