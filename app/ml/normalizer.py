# app/ml/normalizer.py

import numpy as np

class FeatureNormalizer:
    """
    Simple rolling mean/std normalizer.
    """

    def __init__(self):
        self.mean = None
        self.std = None

    def fit(self, X: np.ndarray) -> None:
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0) + 1e-6  # avoid division tantrums

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.mean is None or self.std is None:
            return X
        return (X - self.mean) / self.std

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)
