import logging
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ANOMALY_THRESHOLD = 0.5


def load_anomalib_model(model_path: Path, device: str = "auto"):
    import torch
    from anomalib.models import Patchcore

    if device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

    checkpoint = torch.load(str(model_path), map_location=device, weights_only=False)
    state_dict = checkpoint.get("model_state_dict", checkpoint)

    model = Patchcore(
        backbone="wide_resnet50_2",
        layers=("layer2", "layer3"),
        pre_trained=False,
        coreset_sampling_ratio=0.1,
        num_neighbors=9,
    )
    model.load_state_dict(state_dict, strict=False)
    model.to(device)
    model.eval()

    logger.info("Model loaded on %s", device)
    return model, device


def preprocess_image(image_path: Path) -> Any:  # returns torch.Tensor
    from torchvision import transforms

    transform = transforms.Compose(
        [
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    image = Image.open(image_path).convert("RGB")
    return transform(image).unsqueeze(0)


def predict_image(model, image_tensor, device: str) -> dict:
    import torch

    image_tensor = image_tensor.to(device)
    with torch.no_grad():
        output = model(image_tensor)

    anomaly_score = float(output.pred_score.cpu().numpy().flatten()[0])
    is_anomaly = anomaly_score > ANOMALY_THRESHOLD
    anomaly_map = (
        output.anomaly_map.cpu().numpy().squeeze() if hasattr(output, "anomaly_map") else None
    )

    return {
        "anomaly_score": anomaly_score,
        "is_anomaly": is_anomaly,
        "threshold": ANOMALY_THRESHOLD,
        "anomaly_map_shape": list(anomaly_map.shape) if anomaly_map is not None else None,
    }


def run_inference_on_test_set(
    model_path: Path,
    test_dir: Path,
    labels: pd.DataFrame,
    output_path: Path | None = None,
):
    model, device = load_anomalib_model(model_path)

    test_images = list(test_dir.rglob("*.jpg")) + list(test_dir.rglob("*.png"))
    logger.info("Running inference on %d test images", len(test_images))

    results = []
    for img_path in test_images:
        try:
            tensor = preprocess_image(img_path)
            result = predict_image(model, tensor, device)
            result["image_path"] = str(img_path)
            result["image_name"] = img_path.name
            results.append(result)
        except Exception as e:
            logger.error("Inference failed for %s: %s", img_path.name, e)

    df = pd.DataFrame(results)
    logger.info(
        "Inference complete: %d images, %d anomalies detected (threshold=%.2f)",
        len(df),
        df["is_anomaly"].sum(),
        ANOMALY_THRESHOLD,
    )

    if output_path:
        df.to_csv(output_path, index=False)
        logger.info("Results saved to %s", output_path)

    return df


def write_results_to_supabase(results_df: pd.DataFrame, labels_df: pd.DataFrame):
    try:
        from db.client import get_supabase_client

        client = get_supabase_client()
        if client is None:
            logger.warning("Supabase client not available — skipping DB write")
            return

        for _, row in results_df.iterrows():
            image_name = row["image_name"]
            label_row = labels_df[labels_df["ImageFile"].str.contains(image_name, na=False)]
            if label_row.empty:
                continue
            label_row = label_row.iloc[0]

            client.table("anomalies").upsert(
                {
                    "image_id": int(label_row.get("id", 0)) if "id" in label_row else None,
                    "anomaly_score": float(row["anomaly_score"]),
                    "is_anomaly": bool(row["is_anomaly"]),
                    "threshold": ANOMALY_THRESHOLD,
                }
            ).execute()
        logger.info("Results written to Supabase anomalies table")
    except ImportError:
        logger.warning("Supabase SDK not available — skipping DB write")


def main():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    model_path = project_root / "models" / "patchcore_matwi.pt"
    test_dir = project_root / "data" / "anomalib_format" / "test"
    labels_path = project_root / "server" / "dataset" / "labels.csv"
    output_path = project_root / "data" / "anomalib_inference_results.csv"

    if not model_path.exists():
        logger.error("Model not found at %s. Run train.py and export.py first.", model_path)
        return

    labels = pd.read_csv(labels_path)
    run_inference_on_test_set(model_path, test_dir, labels, output_path)


if __name__ == "__main__":
    main()
