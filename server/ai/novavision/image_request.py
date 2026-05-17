import base64
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def _env_required(value: str | None, env_name: str) -> str:
    resolved = value or os.getenv(env_name, "")
    if not resolved:
        raise ValueError(f"{env_name} must be provided as an argument or environment variable")
    return resolved


def resize_image_to_256(
    image_path: str,
    output_path: str | None = None,
    size: tuple[int, int] = (256, 256),
) -> str:
    """
    Verilen path'teki image'i 256x256 resize eder.

    Eğer image zaten 256x256 ise ve output_path verilmediyse aynı path'i döner,
    dosyayı yeniden kaydetmez. Eğer output_path verilirse her durumda output_path'e kaydeder.

    Args:
        image_path: Resize edilecek image path'i.
        output_path: Kaydedilecek path. Verilmezse aynı dosyanın yanına
            *_256x256.<ext> olarak kaydeder.
        size: Hedef boyut. Default: (256, 256).

    Returns:
        Resize edilmiş image'in path'i. Zaten 256x256 ise original path dönebilir.
    """

    input_path = Path(image_path)

    with Image.open(input_path) as image:
        if image.size == size and output_path is None:
            return str(input_path)

        if output_path is None:
            output_path = str(input_path.with_name(f"{input_path.stem}_256x256{input_path.suffix}"))

        resized_image = image.convert("RGB").resize(size, Image.Resampling.LANCZOS)
        resized_image.save(output_path)

    return output_path


def send_image_to_novavision(
    image_path: str,
    api_url: str = "http://localhost:7001/api",
    app_id: str = "19EC35",
    port: int = 3030,
    workspace: str | None = None,
    ws_channel: str | None = None,
    header_access_token: str | None = None,
    payload_access_token: str | None = None,
    storage_access_token: str | None = None,
    storage_access_url: str = "http://dev.suite.novavision.ai/api/storage",
    service: str = "diginova-wsl",
    normalization_type: str = "zscore",
    timeout: int = 60,
) -> requests.Response:
    """
    Local NovaVision workflow'a image base64 olarak gönderir.

    Workflow:
        ImageLoad -> Normalization

    Args:
        image_path: Gönderilecek image dosyasının path'i.
        api_url: NovaVision local API endpoint'i.
        app_id: NovaVision workflow/app ID.
        port: NovaVision app port'u.
        workspace: NovaVision workspace ID.
        ws_channel: WebSocket channel değeri.
        header_access_token: Request header access-token değeri.
        payload_access_token: Payload içindeki access-token değeri.
        storage_access_token: app.storage access-token değeri.
        storage_access_url: app.storage access-url değeri.
        service: NovaVision service adı.
        normalization_type: Normalization config type. Örn: zscore.
        timeout: Request timeout saniyesi.

    Returns:
        requests.Response
    """

    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    header_access_token = _env_required(header_access_token, "NOVAVISION_HEADER_ACCESS_TOKEN")
    payload_access_token = _env_required(payload_access_token, "NOVAVISION_PAYLOAD_ACCESS_TOKEN")
    storage_access_token = _env_required(storage_access_token, "NOVAVISION_STORAGE_ACCESS_TOKEN")
    if workspace is None:
        workspace = os.getenv("NOVAVISION_WORKSPACE", "934815ad542a4a7c5e8a2dfa04fea9f5")
    if ws_channel is None:
        ws_channel = os.getenv("NOVAVISION_WS_CHANNEL", "/ws/1057e5612fcf11af7978dccb280b07af")

    payload: dict[str, Any] = {
        "module": "Server",
        "executor": "App",
        "ws_channel": ws_channel,
        "app": {
            "nodes": [
                {
                    "type": "component",
                    "name": "Normalization",
                    "configs": {
                        "executor": {
                            "name": "ConfigExecutor",
                            "value": {
                                "name": "Normalization",
                                "value": {
                                    "name": "Normalization",
                                    "inputs": {
                                        "name": "Normalization",
                                        "inputImage": {
                                            "name": "inputImage",
                                            "type": "object",
                                        },
                                    },
                                    "configs": {
                                        "configType": {
                                            "name": "configType",
                                            "value": {
                                                "name": normalization_type,
                                                "value": normalization_type,
                                                "type": "string",
                                                "field": "option",
                                            },
                                            "type": "object",
                                            "field": "dependentDropdownlist",
                                        }
                                    },
                                },
                                "type": "object",
                                "field": "option",
                            },
                            "type": "executor",
                            "field": "dependentDropdownlist",
                        }
                    },
                    "debug": "False",
                    "api": "False",
                    "uID": "WBwm7R",
                },
                {
                    "type": "component",
                    "name": "ImageLoad",
                    "configs": {
                        "executor": {
                            "name": "ConfigExecutor",
                            "value": {
                                "name": "ImageLoad",
                                "value": {
                                    "name": "ImageLoad",
                                    "configs": {
                                        "imageFieldType": {
                                            "name": "imageFieldType",
                                            "value": {
                                                "name": "base64",
                                                "value": "base64",
                                                "type": "string",
                                                "field": "option",
                                                "path": {
                                                    "name": "basedata",
                                                    "value": image_base64,
                                                    "type": "string",
                                                    "field": "textInput",
                                                },
                                            },
                                            "type": "object",
                                            "field": "dependentDropdownlist",
                                        }
                                    },
                                },
                                "type": "object",
                                "field": "option",
                            },
                            "type": "executor",
                            "field": "dependentDropdownlist",
                        }
                    },
                    "debug": "False",
                    "api": "False",
                    "uID": "26SgzP",
                },
            ],
            "connections": [
                {
                    "node": "WBwm7R",
                    "nodeFrom": "26SgzP",
                    "node_matching": {
                        "outputImage": "inputImage",
                    },
                }
            ],
            "outputs": {
                "26SgzP-outputImage": "object",
                "WBwm7R-outputImage": "object",
            },
            "app": {
                "access-token": storage_access_token,
                "access-url": storage_access_url,
            },
            "mode": "debug",
            "debug": "true",
            "app_id": app_id,
            "payload": [],
            "ws_channel": ws_channel,
            "port": port,
            "ssl": "DISABLE",
            "service": service,
        },
        "workspace": workspace,
        "access-token": payload_access_token,
    }

    headers = {
        "Content-Type": "application/json",
        "access-token": header_access_token,
    }

    return requests.post(api_url, headers=headers, json=payload, timeout=timeout)


def send_image_to_novavision_json(image_path: str, **kwargs: Any) -> tuple[int, Any]:
    """Response'u JSON parse etmeye çalışır; olmazsa text döner."""

    response = send_image_to_novavision(image_path=image_path, **kwargs)

    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, response.text


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Image dosyasını base64'e çevirip NovaVision workflow'a gönderir."
    )
    parser.add_argument("image_path", help="Gönderilecek image path'i")
    parser.add_argument("--api-url", default="http://localhost:7001/api")
    parser.add_argument("--app-id", default="19EC35")
    parser.add_argument("--port", type=int, default=3030)
    parser.add_argument("--normalization-type", default="zscore")
    parser.add_argument("--header-access-token", default=None)
    parser.add_argument("--payload-access-token", default=None)
    parser.add_argument("--storage-access-token", default=None)

    args = parser.parse_args()

    status_code, result = send_image_to_novavision_json(
        image_path=args.image_path,
        api_url=args.api_url,
        app_id=args.app_id,
        port=args.port,
        normalization_type=args.normalization_type,
        header_access_token=args.header_access_token,
        payload_access_token=args.payload_access_token,
        storage_access_token=args.storage_access_token,
    )

    print("status_code:", status_code)
    print(result)
