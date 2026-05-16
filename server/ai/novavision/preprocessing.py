import base64
from pathlib import Path

from ai.novavision.schemas import PreprocessedImage

SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def resolve_image_path(image_path: str, project_root: Path | None = None) -> Path:
    path = Path(image_path)
    if path.is_absolute() and path.exists():
        return path

    root = project_root or Path(__file__).resolve().parents[3]
    candidates = [
        root / image_path,
        root / "data" / image_path,
        root / "llm_docs" / image_path,
    ]
    if image_path.startswith("MATWI/"):
        candidates.append(root / "llm_docs" / image_path.removeprefix("MATWI/"))

    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Image path not found: {image_path}")


def preprocess_image(image_path: str, project_root: Path | None = None) -> PreprocessedImage:
    path = resolve_image_path(image_path, project_root=project_root)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_IMAGE_SUFFIXES:
        raise ValueError(f"Unsupported image format: {suffix}. Expected JPEG or PNG")

    image_bytes = path.read_bytes()
    if not image_bytes:
        raise ValueError(f"Image file is empty: {path}")

    mime_type = "image/png" if suffix == ".png" else "image/jpeg"
    return PreprocessedImage(
        image_base64=base64.b64encode(image_bytes).decode("ascii"),
        mime_type=mime_type,
        source_path=path,
        size_bytes=len(image_bytes),
    )


def preprocess_base64(image_base64: str) -> PreprocessedImage:
    try:
        decoded = base64.b64decode(image_base64, validate=True)
    except ValueError as exc:
        raise ValueError("image_base64 must be valid base64") from exc
    if not decoded:
        raise ValueError("image_base64 is empty")
    return PreprocessedImage(
        image_base64=image_base64,
        mime_type="application/octet-stream",
        size_bytes=len(decoded),
    )
