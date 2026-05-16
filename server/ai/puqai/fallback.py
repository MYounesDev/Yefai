import logging
import platform
import subprocess

logger = logging.getLogger(__name__)


def send_os_notification(message: str, title: str = "Yefai") -> None:
    try:
        system = platform.system()
        if system == "Darwin":
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'display notification "{message}" with title "{title}"',
                ],
                check=False,
                timeout=5,
            )
        elif system == "Linux":
            subprocess.run(
                ["notify-send", title, message],
                check=False,
                timeout=5,
            )
        elif system == "Windows":
            logger.info("Windows notification: %s — %s", title, message)
        logger.info("OS notification sent: %s", title)
    except Exception as e:
        logger.warning("OS notification failed: %s", e)
