from app.domain.value_objects.prediction import PredictedClass, Prediction
from app.infrastructure.ai.predictor import MockInferenceEngine
from app.tests.conftest import make_png_bytes


def test_mock_inference_is_deterministic():
    engine = MockInferenceEngine()
    data = make_png_bytes(brightness=210)
    first = engine.predict(data)
    second = engine.predict(data)
    assert first.predicted_class == second.predicted_class
    assert first.confidence_score == second.confidence_score


def test_mock_inference_returns_valid_prediction():
    engine = MockInferenceEngine()
    pred = engine.predict(make_png_bytes(brightness=50))
    assert isinstance(pred, Prediction)
    assert pred.predicted_class in set(PredictedClass)
    assert 0.0 <= pred.confidence_score <= 1.0
    assert pred.class_probabilities


def test_bright_and_dark_images_differ():
    engine = MockInferenceEngine()
    dark = engine.predict(make_png_bytes(brightness=10))
    bright = engine.predict(make_png_bytes(brightness=245))
    # Different brightness should move the probability distribution.
    assert dark.class_probabilities != bright.class_probabilities
