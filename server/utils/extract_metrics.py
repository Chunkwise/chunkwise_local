"""
Contains extrac_metrics function.
"""

from server_types import EvaluationResponse, EvaluationMetrics


def extract_metrics(evaluation_response: EvaluationResponse) -> list[EvaluationMetrics]:
    """
    Takes and returns only the needed metrics from an evaluation response.
    """
    return [
        EvaluationMetrics(
            iou_mean=evals.iou_mean,
            recall_mean=evals.recall_mean,
            precision_mean=evals.precision_mean,
            precision_omega_mean=evals.precision_omega_mean,
        )
        for evals in evaluation_response.results
    ]
