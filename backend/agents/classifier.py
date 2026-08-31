"""
ML Failure Classifier for RecoverAI.
Uses a two-stage approach:
1. Rule-based keyword matcher for instant classification (high accuracy)
2. RandomForest classifier on transaction features for confidence scoring
"""

import os
import datetime
import logging
import re
from typing import List, Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.preprocessing import LabelEncoder, StandardScaler

from backend.models.schemas import PaymentTransaction, FailureClassification
from backend.simulator.failure_generator import PaymentFailureSimulator

logger = logging.getLogger(__name__)

# Keyword-based classification rules (stage 1 - deterministic, high accuracy)
FAILURE_KEYWORDS = {
    "INSUFFICIENT_FUNDS": ["insufficient", "low balance", "nsf", "not enough", "no funds"],
    "BANK_TIMEOUT": ["bank timeout", "bank server", "bank down", "bank_timeout", "acquiring bank"],
    "UPI_TIMEOUT": ["upi timeout", "upi expired", "upi_timeout", "upi app", "collect request expired"],
    "NETWORK_ERROR": ["network", "connection", "dns", "ssl", "internet", "network_error"],
    "EXPIRED_CARD": ["expired", "card expired", "expired_card", "validity"],
    "INVALID_CARD": ["invalid card", "wrong card", "invalid_card", "card number"],
    "AUTHENTICATION_FAILED": ["authentication", "otp failed", "3ds", "auth_failed", "authentication_failed"],
    "INCORRECT_PIN": ["incorrect pin", "wrong pin", "pin mismatch", "incorrect_pin"],
    "APP_NOT_RESPONDING": ["app not responding", "app crash", "app_not_responding", "app timeout"],
    "SESSION_EXPIRED": ["session expired", "session_expired", "session timeout", "login expired"],
    "LIMIT_EXCEEDED": ["limit exceeded", "limit_exceeded", "daily limit", "max amount"],
    "RISK_BLOCKED": ["risk", "fraud", "blocked", "suspicious", "risk_blocked"],
}


class FailureClassifier:
    """ML Failure Classification with keyword + RandomForest hybrid approach."""

    def __init__(self, model_path: str = "failure_model.joblib", encoder_path: str = "encoders.joblib"):
        self.model = None
        self.model_path = model_path
        self.encoder_path = encoder_path
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.target_encoder = LabelEncoder()

        if os.path.exists(self.model_path) and os.path.exists(self.encoder_path):
            try:
                self.load_model()
            except Exception:
                pass

    def _keyword_classify(self, failure_reason: str) -> str:
        """Stage 1: Deterministic keyword-based classification."""
        reason_lower = (failure_reason or "").lower().replace("_", " ")

        # Direct match (failure_reason IS the enum key, e.g. "INSUFFICIENT_FUNDS")
        reason_upper = (failure_reason or "").upper().replace(" ", "_")
        if reason_upper in FAILURE_KEYWORDS:
            return reason_upper

        # Keyword search
        for failure_type, keywords in FAILURE_KEYWORDS.items():
            for kw in keywords:
                if kw in reason_lower:
                    return failure_type

        return "UNKNOWN"

    def _extract_features(self, tx: PaymentTransaction) -> Dict[str, Any]:
        """Extract ML features from PaymentTransaction."""
        hour = tx.timestamp.hour if tx.timestamp else 12
        day_of_week = tx.timestamp.weekday() if tx.timestamp else 0

        if tx.amount < 500:
            amount_bucket = "low"
        elif tx.amount < 5000:
            amount_bucket = "medium"
        elif tx.amount < 20000:
            amount_bucket = "high"
        else:
            amount_bucket = "very_high"

        meta = tx.metadata or {}

        return {
            "amount": tx.amount,
            "amount_bucket": amount_bucket,
            "method": tx.method or "unknown",
            "hour_of_day": hour,
            "day_of_week": day_of_week,
            "attempt_count": meta.get("attempt_count", 1),
            "device": meta.get("device", "unknown"),
            "browser": meta.get("browser", "unknown"),
        }

    def _prepare_data(self, transactions: List[PaymentTransaction], is_training: bool = False) -> pd.DataFrame:
        """Convert transactions into feature vectors."""
        feature_dicts = [self._extract_features(tx) for tx in transactions]
        df = pd.DataFrame(feature_dicts)

        categorical_cols = ["amount_bucket", "method", "device", "browser"]

        if is_training:
            self.label_encoders = {}
            for col in categorical_cols:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        else:
            for col in categorical_cols:
                le = self.label_encoders.get(col)
                if le:
                    classes = list(le.classes_)
                    df[col] = df[col].apply(lambda x: x if x in classes else classes[0])
                    df[col] = le.transform(df[col].astype(str))
                else:
                    df[col] = 0

        numeric_cols = ["amount", "hour_of_day", "day_of_week", "attempt_count"]
        if is_training:
            df[numeric_cols] = self.scaler.fit_transform(df[numeric_cols])
        else:
            df[numeric_cols] = self.scaler.transform(df[numeric_cols])

        return df

    def train(self, transactions: List[PaymentTransaction]) -> Dict[str, Any]:
        """Train the RandomForest on generated data."""
        if not transactions:
            raise ValueError("No transactions provided for training.")

        X = self._prepare_data(transactions, is_training=True)

        # Use keyword classification as the ground truth (much more accurate)
        y_raw = [self._keyword_classify(tx.failure_reason) for tx in transactions]
        self.target_encoder.fit(y_raw)
        y = self.target_encoder.transform(y_raw)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)

        metrics = {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}
        logger.info(f"Classifier trained: accuracy={acc:.3f}, f1={f1:.3f}")

        self.save_model()
        return metrics

    def classify(self, transaction: PaymentTransaction) -> FailureClassification:
        """Classify a single transaction using hybrid approach."""
        # Stage 1: keyword-based (always available, high accuracy)
        keyword_result = self._keyword_classify(transaction.failure_reason)

        # Stage 2: ML confidence score (if model trained)
        confidence = 0.5
        features = self._extract_features(transaction)

        if self.model:
            try:
                X = self._prepare_data([transaction], is_training=False)
                probabilities = self.model.predict_proba(X)
                ml_prediction = self.target_encoder.inverse_transform(self.model.predict(X))[0]
                confidence = float(np.max(probabilities[0]))

                # If keyword match is strong, use it. Otherwise use ML.
                if keyword_result == "UNKNOWN":
                    keyword_result = ml_prediction
            except Exception as e:
                logger.warning(f"ML prediction failed, using keyword only: {e}")

        return FailureClassification(
            transaction_id=transaction.id,
            failure_type=keyword_result,
            confidence=confidence,
            features=features,
        )

    def classify_batch(self, transactions: List[PaymentTransaction]) -> List[FailureClassification]:
        """Classify a batch of transactions."""
        return [self.classify(tx) for tx in transactions]

    def get_feature_importance(self) -> Dict[str, float]:
        """Return feature importances."""
        if not self.model:
            return {}

        feature_names = ["amount", "amount_bucket", "method", "hour_of_day",
                         "day_of_week", "attempt_count", "device", "browser"]
        importances = self.model.feature_importances_
        return dict(zip(feature_names, map(float, importances)))

    def save_model(self):
        """Save model and encoders."""
        if self.model:
            joblib.dump(self.model, self.model_path)
            state = {
                "label_encoders": self.label_encoders,
                "target_encoder": self.target_encoder,
                "scaler": self.scaler,
            }
            joblib.dump(state, self.encoder_path)

    def load_model(self):
        """Load model and encoders."""
        self.model = joblib.load(self.model_path)
        state = joblib.load(self.encoder_path)
        self.label_encoders = state["label_encoders"]
        self.target_encoder = state["target_encoder"]
        self.scaler = state["scaler"]

    def self_train(self, n_samples: int = 1000) -> Dict[str, Any]:
        """Generate synthetic data and train."""
        sim = PaymentFailureSimulator()
        transactions = sim.generate_batch(n_samples)
        return self.train(transactions)
