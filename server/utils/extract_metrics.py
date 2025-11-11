"""
Contains extrac_metrics function.
"""

from server_types import EvaluationResponse, EvaluationMetrics


def extract_metrics(evaluation_response: EvaluationResponse) -> list[EvaluationMetrics]:
    """
    Takes and returns only the needed metrics from an evaluation response.
    """
    return [
        {
            "precision_omega_mean": evals["precision_omega_mean"],
            "precision_mean": evals["precision_mean"],
            "recall_mean": evals["recall_mean"],
            "iou_mean": evals["iou_mean"],
        }
        for evals in evaluation_response["results"]
    ]
