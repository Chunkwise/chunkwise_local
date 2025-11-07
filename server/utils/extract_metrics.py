from server_types import EvaluationResponse, Evaluations


def extract_metrics(evaluation_response: EvaluationResponse) -> list[Evaluations]:
    return [
        {
            "omega_precision": evals["precision_omega_mean"],
            "precision": evals["precision_mean"],
            "recall": evals["recall_mean"],
            "iou": evals["iou_mean"],
        }
        for evals in evaluation_response["results"]
    ]
