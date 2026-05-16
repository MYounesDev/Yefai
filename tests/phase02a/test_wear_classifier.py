import pandas as pd
import pytest

from ai.anomalib.wear_classifier import classify_wear_type_from_labels


class TestWearClassifier:
    def test_flank_wear(self):
        df = pd.DataFrame(
            {"ImageFile": ["MATWI/Set1/flank.jpg"], "wear_type": ["flank_wear"]}
        )
        assert classify_wear_type_from_labels("flank.jpg", df) == "flank_wear"

    def test_adhesion(self):
        df = pd.DataFrame(
            {"ImageFile": ["MATWI/Set1/adhesion.jpg"], "wear_type": ["adhesion"]}
        )
        assert classify_wear_type_from_labels("adhesion.jpg", df) == "adhesion"

    def test_combination(self):
        df = pd.DataFrame(
            {"ImageFile": ["MATWI/Set1/combo.jpg"], "wear_type": ["combination"]}
        )
        assert classify_wear_type_from_labels("combo.jpg", df) == "combination"

    def test_unknown_type(self):
        df = pd.DataFrame(
            {"ImageFile": ["MATWI/Set1/unknown.jpg"], "wear_type": ["garbage_type"]}
        )
        assert classify_wear_type_from_labels("unknown.jpg", df) == "unknown"

    def test_empty_type(self):
        df = pd.DataFrame(
            {"ImageFile": ["MATWI/Set1/empty.jpg"], "wear_type": [""]}
        )
        assert classify_wear_type_from_labels("empty.jpg", df) == "unknown"

    def test_missing_image(self):
        df = pd.DataFrame(
            {"ImageFile": ["MATWI/Set1/other.jpg"], "wear_type": ["flank_wear"]}
        )
        assert classify_wear_type_from_labels("missing.jpg", df) == "unknown"
