import os
import logging
import re
from typing import List, Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

from backend.models.schemas import PaymentTransaction, FailureClassification
from backend.simulator.failure_generator import PaymentFailureSimulator

logger = logging.getLogger(__name__)

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
        if not failure_reason:
            return "UNKNOWN"
        reason_lower = failure_reason.lower()
        for ftype, keywords in FAILURE_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', reason_lower):
                    return ftype
                if kw in reason_lower:
                    return ftype
        return "UNKNOWN"

    def extract_features(self, tx: PaymentTransaction) -> Dict[str, Any]:
        hour = tx.timestamp.hour if hasattr(tx.timestamp, "hour") else 12
        day_of_week = tx.timestamp.weekday() if hasattr(tx.timestamp, "weekday") else 0
        day_of_month = tx.timestamp.day if hasattr(tx.timestamp, "day") else 15
        is_weekend = 1 if day_of_week >= 5 else 0
        is_night = 1 if hour >= 22 or hour <= 6 else 0
        is_salary_day = 1 if day_of_month in [1, 2, 3, 28, 29, 30, 31] else 0

        metadata = tx.metadata or {}
        attempt_count = metadata.get("attempt_count", 1)
        device = metadata.get("device", "unknown")
        failure_reason = tx.failure_reason or ""
        reason_len = len(failure_reason)

        return {
            "amount": float(tx.amount),
            "hour": hour,
            "day_of_week": day_of_week,
            "day_of_month": day_of_month,
            "is_weekend": is_weekend,
            "is_night": is_night,
            "is_salary_day": is_salary_day,
            "attempt_count": attempt_count,
            "reason_len": reason_len,
            "method": tx.method,
            "device": device,
        }

    def classify(self, transaction: PaymentTransaction) -> FailureClassification:
        kw_type = self._keyword_classify(transaction.failure_reason)
        features = self.extract_features(transaction)
        features_used = list(features.keys())

        if self.model is None or not hasattr(self.target_encoder, "classes_"):
            if kw_type != "UNKNOWN":
                return FailureClassification(
                    failure_type=kw_type,
                    confidence_score=0.92,
                    features_used=features_used,
                    raw_reason=transaction.failure_reason,
                )
            return FailureClassification(
                failure_type="BANK_TIMEOUT",
                confidence_score=0.70,
                features_used=features_used,
                raw_reason=transaction.failure_reason,
            )

        try:
            df = pd.DataFrame([features])
            for col in ["method", "device"]:
                if col in self.label_encoders:
                    df[col] = df[col].astype(str).map(
                        lambda s: s if s in self.label_encoders[col].classes_ else self.label_encoders[col].classes_[0]
                    )
                    df[col] = self.label_encoders[col].transform(df[col])

            proba = self.model.predict_proba(df)[0]
            pred_idx = np.argmax(proba)
            model_confidence = float(proba[pred_idx])
            pred_class = self.target_encoder.inverse_transform([pred_idx])[0]

            if kw_type != "UNKNOWN":
                final_type = kw_type
                confidence = max(model_confidence, 0.88)
            else:
                final_type = pred_class
                confidence = model_confidence

            return FailureClassification(
                failure_type=final_type,
                confidence_score=round(confidence, 2),
                features_used=features_used,
                raw_reason=transaction.failure_reason,
            )
        except Exception:
            return FailureClassification(
                failure_type=kw_type if kw_type != "UNKNOWN" else "BANK_TIMEOUT",
                confidence_score=0.80,
                features_used=features_used,
                raw_reason=transaction.failure_reason,
            )

    def self_train(self, n_samples: int = 500) -> Dict[str, Any]:
        sim = PaymentFailureSimulator()
        transactions = sim.generate_batch(n_samples)

        data = []
        for t in transactions:
            feats = self.extract_features(t)
            feats["failure_type"] = t.failure_reason.split(":")[0] if ":" in (t.failure_reason or "") else "INSUFFICIENT_FUNDS"
            for ftype, keywords in FAILURE_KEYWORDS.items():
                if any(kw in (t.failure_reason or "").lower() for kw in keywords):
                    feats["failure_type"] = ftype
                    break
            data.append(feats)

        df = pd.DataFrame(data)
        X = df.drop("failure_type", axis=1)
        y = df["failure_type"]

        self.label_encoders = {}
        for col in ["method", "device"]:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.label_encoders[col] = le

        self.target_encoder = LabelEncoder()
        y_encoded = self.target_encoder.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

        self.model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        self.save_model()
        return {"accuracy": acc, "classes": list(self.target_encoder.classes_)}

    def save_model(self):
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump({
                "label_encoders": self.label_encoders,
                "target_encoder": self.target_encoder,
            }, self.encoder_path)
        except Exception as e:
            logger.warning(f"Could not save classifier model: {e}")

    def load_model(self):
        self.model = joblib.load(self.model_path)
        encoders = joblib.load(self.encoder_path)
        self.label_encoders = encoders["label_encoders"]
        self.target_encoder = encoders["target_encoder"]

    def get_feature_importance(self) -> Dict[str, float]:
        if self.model is None:
            return {}
        feature_names = [
            "amount", "hour", "day_of_week", "day_of_month",
            "is_weekend", "is_night", "is_salary_day",
            "attempt_count", "reason_len", "method", "device"
        ]
        importances = self.model.feature_importances_
        return {name: float(round(imp, 4)) for name, imp in zip(feature_names, importances)}
