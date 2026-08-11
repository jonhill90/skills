from __future__ import annotations

import importlib.util
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT_PATH = Path(__file__).parents[1] / "skills" / "notify" / "scripts" / "notify.py"
SPEC = importlib.util.spec_from_file_location("notify", SCRIPT_PATH)
assert SPEC and SPEC.loader
notify = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = notify
SPEC.loader.exec_module(notify)


class NotifyTelegramChannelTests(unittest.TestCase):
    """skills#146: the notify skill must grow a Telegram channel so it becomes
    the single canonical sender, with Telegram tried first and iMessage as a
    Mac-only fallback -- exactly the order and env var names already proven
    in agent-dotfiles/scripts/supervisor/notify.sh."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        env = {
            "NOTIFY_STATE_DIR": self.tmpdir.name,
        }
        self.env_patch = mock.patch.dict(os.environ, env, clear=True)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def run_notify(self, argv: list[str]) -> tuple[int, str, str]:
        parser = notify.build_parser()
        args = parser.parse_args(argv)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = notify.run(args)
        return rc, out.getvalue(), err.getvalue()

    def test_auto_mode_with_nothing_configured_is_a_loud_config_error(self) -> None:
        rc, _, err = self.run_notify(["--message", "hi"])
        self.assertEqual(rc, 2)
        self.assertIn("AGENT_NOTIFY_TELEGRAM_TOKEN", err)
        self.assertIn("AGENT_NOTIFY_TELEGRAM_CHAT_ID", err)
        self.assertIn("NOTIFY_IMESSAGE_TARGET", err)

    def test_auto_mode_prefers_telegram_over_imessage(self) -> None:
        os.environ["AGENT_NOTIFY_TELEGRAM_TOKEN"] = "faketoken"
        os.environ["AGENT_NOTIFY_TELEGRAM_CHAT_ID"] = "12345"
        os.environ["NOTIFY_IMESSAGE_TARGET"] = "jon@example.com"
        with mock.patch.object(notify, "send_telegram") as tg, mock.patch.object(
            notify, "send_imessage"
        ) as im:
            rc, out, _ = self.run_notify(["--message", "hi", "--send"])
        self.assertEqual(rc, 0)
        tg.assert_called_once_with("faketoken", "12345", "hi")
        im.assert_not_called()
        self.assertIn("channel=telegram", out)

    def test_auto_mode_falls_back_to_imessage_when_telegram_fails(self) -> None:
        os.environ["AGENT_NOTIFY_TELEGRAM_TOKEN"] = "faketoken"
        os.environ["AGENT_NOTIFY_TELEGRAM_CHAT_ID"] = "12345"
        os.environ["NOTIFY_IMESSAGE_TARGET"] = "jon@example.com"
        with mock.patch.object(
            notify, "send_telegram", side_effect=notify.SendError("boom")
        ) as tg, mock.patch.object(notify, "send_imessage") as im:
            rc, out, _ = self.run_notify(["--message", "hi", "--send"])
        self.assertEqual(rc, 0)
        tg.assert_called_once()
        im.assert_called_once_with("jon@example.com", "hi")
        self.assertIn("channel=imessage", out)
        log = (Path(self.tmpdir.name) / "notify.log").read_text(encoding="utf-8")
        self.assertIn("SEND-FAILED channel=telegram", log)

    def test_auto_mode_exits_nonzero_and_logs_when_every_channel_fails(self) -> None:
        os.environ["AGENT_NOTIFY_TELEGRAM_TOKEN"] = "faketoken"
        os.environ["AGENT_NOTIFY_TELEGRAM_CHAT_ID"] = "12345"
        os.environ["NOTIFY_IMESSAGE_TARGET"] = "jon@example.com"
        with mock.patch.object(
            notify, "send_telegram", side_effect=notify.SendError("telegram down")
        ), mock.patch.object(
            notify, "send_imessage", side_effect=notify.SendError("imessage down")
        ):
            rc, _, err = self.run_notify(["--message", "hi", "--send"])
        self.assertEqual(rc, 1)
        self.assertIn("telegram down", err)
        self.assertIn("imessage down", err)
        log = (Path(self.tmpdir.name) / "notify.log").read_text(encoding="utf-8")
        self.assertIn("UNREACHABLE", log)

    def test_explicit_channel_does_not_fall_back(self) -> None:
        os.environ["AGENT_NOTIFY_TELEGRAM_TOKEN"] = "faketoken"
        os.environ["AGENT_NOTIFY_TELEGRAM_CHAT_ID"] = "12345"
        os.environ["NOTIFY_IMESSAGE_TARGET"] = "jon@example.com"
        with mock.patch.object(
            notify, "send_imessage", side_effect=notify.SendError("imessage down")
        ) as im, mock.patch.object(notify, "send_telegram") as tg:
            rc, _, err = self.run_notify(
                ["--message", "hi", "--channel", "imessage", "--send"]
            )
        self.assertEqual(rc, 1)
        im.assert_called_once()
        tg.assert_not_called()
        self.assertIn("imessage down", err)

    def test_telegram_missing_chat_id_is_config_error(self) -> None:
        os.environ["AGENT_NOTIFY_TELEGRAM_TOKEN"] = "faketoken"
        rc, _, err = self.run_notify(["--message", "hi", "--channel", "telegram"])
        self.assertEqual(rc, 2)
        self.assertIn("AGENT_NOTIFY_TELEGRAM_CHAT_ID", err)

    def test_unbuilt_channel_still_refuses_with_exit_2(self) -> None:
        rc, _, err = self.run_notify(["--message", "hi", "--channel", "discord"])
        self.assertEqual(rc, 2)
        self.assertIn("discord", err)

    def test_dry_run_never_calls_a_real_sender(self) -> None:
        os.environ["AGENT_NOTIFY_TELEGRAM_TOKEN"] = "faketoken"
        os.environ["AGENT_NOTIFY_TELEGRAM_CHAT_ID"] = "12345"
        with mock.patch.object(notify, "send_telegram") as tg:
            rc, out, _ = self.run_notify(["--message", "hi"])
        self.assertEqual(rc, 0)
        tg.assert_not_called()
        self.assertIn("DRY-RUN", out)

    def test_no_real_token_or_chat_id_committed_in_source(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("bot-token", source.lower())
        # Credentials must be read from the environment only.
        self.assertIn("AGENT_NOTIFY_TELEGRAM_TOKEN", source)
        self.assertIn("os.environ", source)

    def test_self_test_passes(self) -> None:
        self.assertTrue(notify.self_test())


if __name__ == "__main__":
    unittest.main()
