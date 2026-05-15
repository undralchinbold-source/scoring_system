"""
PPT Алхам 3: Predictor класс (Singleton)
ml/predictor.py — Загварыг нэг удаа ачааллаж, дахин ачаалахгүй.
"""
import os
import warnings

import joblib
import numpy as np
import pandas as pd

# Ажлын байрны төрлүүд (загвар сургасан утгуудтай таарах ёстой)
EMPLOYMENT_TYPES = [
    "Багш",
    "Барилгачин",
    "Бизнес эрхлэгч",
    "Жолооч",
    "Инженер",
    "Малчин",
    "Тариаланч",
    "Төрийн албан хаагч",
    "Хувийн салбар",
    "Худалдагч",
    "Эмч",
    "Үйлчилгээ",
]


class LoanPredictor:
    """
    Singleton: ганц instance үүсгэж загварыг санах ойд нэг удаа хадгална.
    Request бүрд дахин ачаалахгүй тул хурдан ажиллана.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    # ------------------------------------------------------------------
    # Ачаалах
    # ------------------------------------------------------------------

    def load(self, model_path: str) -> None:
        """pkl файлаас бүх объектуудыг нэг удаа ачаална."""
        if self._loaded:
            return

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Загварын файл олдсонгүй: {model_path}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bundle: dict = joblib.load(model_path)

        self._model = bundle["model"]
        self._scaler = bundle["scaler"]
        self._le_employment = bundle["label_encoder_employment"]
        self._le_decision = bundle["label_encoder_decision"]
        self._feature_cols = bundle["feature_cols"]
        self.model_version: str = bundle.get("model_version", "v1.0.0")
        self.model_name: str = bundle.get("model_name", "Unknown")
        self._loaded = True

    # ------------------------------------------------------------------
    # Preprocessing
    # ------------------------------------------------------------------

    def _preprocess(self, data: dict) -> np.ndarray:
        """
        Оруулсан мэдээллийг загварт тохирох feature vector болгоно.
        feature_cols дарааллыг чандлан сахина.
        """
        monthly_income = float(data["monthly_income"])
        employment_years = float(data["employment_years"])
        requested_amount = float(data["requested_amount"])
        employment_type: str = data["employment_type"]

        # LabelEncoder-ээр encode хийнэ
        employment_encoded = int(
            self._le_employment.transform([employment_type])[0]
        )

        # Загвар сургахад ашигласан derived feature-үүд
        amount_to_income_ratio = requested_amount / monthly_income
        annual_dti = requested_amount / (monthly_income * 12)
        log_income = float(np.log(monthly_income))
        log_amount = float(np.log(requested_amount))

        feature_map = {
            "monthly_income": monthly_income,
            "employment_years": employment_years,
            "requested_amount": requested_amount,
            "amount_to_income_ratio": amount_to_income_ratio,
            "annual_dti": annual_dti,
            "log_income": log_income,
            "log_amount": log_amount,
            "employment_type_encoded": employment_encoded,
        }

        # pandas DataFrame ашигласнаар sklearn feature name warning арилна
        return pd.DataFrame([feature_map], columns=self._feature_cols)

    # ------------------------------------------------------------------
    # Таамаглал
    # ------------------------------------------------------------------

    def predict(self, data: dict) -> dict:
        """
        data: monthly_income, employment_years, requested_amount, employment_type
        Буцаах: score, decision, probabilities, model_version
        """
        if not self._loaded:
            raise RuntimeError("Predictor ачаалагдаагүй байна. load() дуудна уу.")

        X = self._preprocess(data)
        scaled_values = self._scaler.transform(X)
        X_scaled = pd.DataFrame(scaled_values, columns=self._feature_cols)

        pred_index = int(self._model.predict(X_scaled)[0])
        probas = self._model.predict_proba(X_scaled)[0]

        decision: str = self._le_decision.inverse_transform([pred_index])[0]

        # "approved" классын магадлалыг score болгоно
        classes = list(self._le_decision.classes_)
        approved_idx = classes.index("approved") if "approved" in classes else 0
        score = float(probas[approved_idx])

        return {
            "score": round(score, 4),
            "decision": decision,
            "probabilities": {
                label: round(float(prob), 4)
                for label, prob in zip(classes, probas)
            },
            "model_version": self.model_version,
            "model_name": self.model_name,
        }


# Модуль түвшний singleton instance
predictor = LoanPredictor()
