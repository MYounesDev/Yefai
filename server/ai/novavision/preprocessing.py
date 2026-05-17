import base64
import re
from pathlib import Path

from ai.novavision.schemas import PreprocessedImage

SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def _parse_set_from_path(image_path: str) -> int | None:
    match = re.search(r"Set(\d+)", image_path, re.IGNORECASE)
    return int(match.group(1)) if match else None


def resolve_image_path(image_path: str, project_root: Path | None = None) -> Path:
    path = Path(image_path)
    if path.is_absolute() and path.exists():
        return path

    root = project_root or Path(__file__).resolve().parents[3]
    image_name = path.name
    candidates = [
        root / image_path,
        root / "data" / image_path,
        root / "llm_docs" / image_path,
    ]

    set_num = _parse_set_from_path(image_path)
    if set_num is not None:
        set_dir = f"Set{set_num}"
        candidates.extend(
            [
                root / "data" / "MATWI" / set_dir / "images" / image_name,
                root / "data" / "MATWI" / set_dir / set_dir / "images" / image_name,
                root / "data" / "MATWI" / set_dir / image_name,
            ]
        )

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
