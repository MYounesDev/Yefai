import logging
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MODEL_NAME = "jinaai/jina-clip-v2"
EMBEDDING_DIM = 1024
CACHE_DIR = str(Path.home() / ".cache" / "huggingface")


def get_device() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_jina_model(device: str | None = None) -> Any:
    import transformers.models.clip.modeling_clip as clip_modeling
    from transformers import AutoModel

    if device is None:
        device = get_device()

    logger.info("Loading Jina CLIP v2 on %s...", device)
    if not hasattr(clip_modeling, "clip_loss") and hasattr(
        clip_modeling, "image_text_contrastive_loss"
    ):
        # Jina CLIP v2 remote code imports the older Transformers symbol
        # `clip_loss`; Transformers 5 exposes the same behavior as
        # `image_text_contrastive_loss`.
        clip_modeling.clip_loss = clip_modeling.image_text_contrastive_loss  # type: ignore[attr-defined]

    # Jina's remote config checks torch dtype names with hasattr(torch, torch_dtype),
    # so pass the dtype as a string rather than a torch.dtype object.
    torch_dtype = "float16" if device != "cpu" else "float32"
    model = AutoModel.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        torch_dtype=torch_dtype,
        cache_dir=CACHE_DIR,
    )
    model.to(device)
    model.eval()

    logger.info("Jina CLIP v2 loaded successfully")
    return model


def encode_image(model: Any, image: Any, device: str | None = None) -> list[float]:
    if device is None:
        device = get_device()

    embedding = model.encode_image(image)
    if hasattr(embedding, "cpu"):
        embedding = embedding.cpu().detach().numpy()
    return embedding.flatten().tolist()  # type: ignore[no-any-return]


def encode_text(model: Any, text: str, device: str | None = None) -> list[float]:
    if device is None:
        device = get_device()

    embedding = model.encode_text(text)
    if hasattr(embedding, "cpu"):
        embedding = embedding.cpu().detach().numpy()
    return embedding.flatten().tolist()  # type: ignore[no-any-return]


def warmup_model(model: Any) -> None:
    import time

    from PIL import Image

    dummy_img = Image.new("RGB", (256, 256), color=(128, 128, 128))
    dummy_text = "warmup test"

    t0 = time.monotonic()
    encode_image(model, dummy_img)
    t1 = time.monotonic()
    img_latency = (t1 - t0) * 1000

    t0 = time.monotonic()
    encode_text(model, dummy_text)
    t1 = time.monotonic()
    text_latency = (t1 - t0) * 1000

    logger.info("Warmup complete — image: %.0fms, text: %.0fms", img_latency, text_latency)
