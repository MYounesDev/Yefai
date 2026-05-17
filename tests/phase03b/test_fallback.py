"""Tests for OS notification fallback — Phase 3B."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "server"))



from ai.puqai.fallback import send_os_notification


class TestOsNotification:
    def test_send_returns(self):
        """Should not raise any exceptions."""
        # This just verifies the function runs without error
        # Actual notification depends on OS and display server
        send_os_notification(message="Test notification", title="Test")
        assert True

    def test_empty_message(self):
        """Should handle empty message gracefully."""
        send_os_notification(message="", title="Yefai")
        assert True

    def test_long_message(self):
        """Should handle long messages."""
        long_msg = "X" * 500
        send_os_notification(message=long_msg, title="Long Test")
        assert True
