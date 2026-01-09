import pytest
from types import SimpleNamespace
from pydantic import ValidationError

from server.server_types import EvaluationResponse, EvaluationMetrics
from server.utils.extract_metrics import extract_metrics


def make_eval_metrics(iou, recall, precision, precision_omega):
    return EvaluationMetrics(
        iou_mean=iou,
        recall_mean=recall,
        precision_mean=precision,
        precision_omega_mean=precision_omega,
    )


def test_extract_metrics_with_pydantic_models():
    e1 = make_eval_metrics(0.1, 0.2, 0.3, 0.4)
    e2 = make_eval_metrics(0.5, 0.6, 0.7, 0.8)

    response = EvaluationResponse(
        embedding_model="emb",
        corpus_id="corpus",
        document_s3_key="doc",
        queries_s3_key="queries",
        queries_generated=True,
        num_queries=1,
        chunkers_evaluated=["c1"],
        results=[e1, e2],
    )

    out = extract_metrics(response)

    assert isinstance(out, list)
    assert len(out) == 2
    assert all(isinstance(x, EvaluationMetrics) for x in out)

    assert out[0].iou_mean == pytest.approx(0.1)
    assert out[0].recall_mean == pytest.approx(0.2)
    assert out[1].precision_mean == pytest.approx(0.7)
    assert out[1].precision_omega_mean == pytest.approx(0.8)


def test_extract_metrics_empty_results():
    response = EvaluationResponse(
        embedding_model="emb",
        corpus_id="corpus",
        document_s3_key="doc",
        queries_s3_key="queries",
        queries_generated=False,
        num_queries=0,
        chunkers_evaluated=[],
        results=[],
    )

    out = extract_metrics(response)
    assert out == []


def test_extract_metrics_with_simple_namespace():
    # Works with plain objects that have the expected attributes
    r = SimpleNamespace(
        results=[
            SimpleNamespace(
                iou_mean=1.0,
                recall_mean=1.1,
                precision_mean=1.2,
                precision_omega_mean=1.3,
            )
        ]
    )

    out = extract_metrics(r)
    assert len(out) == 1
    assert out[0].iou_mean == pytest.approx(1.0)
    assert out[0].recall_mean == pytest.approx(1.1)
    assert out[0].precision_mean == pytest.approx(1.2)
    assert out[0].precision_omega_mean == pytest.approx(1.3)


def test_missing_metric_attribute_raises_attribute_error():
    # results item missing `precision_mean`
    r = SimpleNamespace(
        results=[
            SimpleNamespace(iou_mean=0.1, recall_mean=0.2, precision_omega_mean=0.3)
        ]
    )
    with pytest.raises(AttributeError):
        extract_metrics(r)


def test_none_metric_raises_validation_error():
    r = SimpleNamespace(
        results=[
            SimpleNamespace(
                iou_mean=None,
                recall_mean=0.2,
                precision_mean=0.3,
                precision_omega_mean=0.4,
            )
        ]
    )
    with pytest.raises(ValidationError):
        extract_metrics(r)


def test_invalid_type_raises_validation_error():
    r = SimpleNamespace(
        results=[
            SimpleNamespace(
                iou_mean="not a number",
                recall_mean=0.2,
                precision_mean=0.3,
                precision_omega_mean=0.4,
            )
        ]
    )
    with pytest.raises(ValidationError):
        extract_metrics(r)


def test_non_iterable_results_raises_type_error():
    r = SimpleNamespace(results=None)
    with pytest.raises(TypeError):
        extract_metrics(r)


def test_mixed_good_and_bad_results_raises_validation_error():
    r = SimpleNamespace(
        results=[
            SimpleNamespace(
                iou_mean=0.1,
                recall_mean=0.2,
                precision_mean=0.3,
                precision_omega_mean=0.4,
            ),
            SimpleNamespace(
                iou_mean="bad",
                recall_mean=0.2,
                precision_mean=0.3,
                precision_omega_mean=0.4,
            ),
        ]
    )
    with pytest.raises(ValidationError):
        extract_metrics(r)


def test_large_values_preserved():
    val = 1e308
    r = SimpleNamespace(
        results=[
            SimpleNamespace(
                iou_mean=val,
                recall_mean=val,
                precision_mean=val,
                precision_omega_mean=val,
            )
        ]
    )
    out = extract_metrics(r)
    assert out[0].iou_mean == pytest.approx(val)
