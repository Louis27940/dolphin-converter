import unittest
from unittest.mock import patch
from pathlib import Path
import importlib.machinery
import importlib.util

def load_module():
    script_path = Path(__file__).parent.parent / "bin" / "dolphin-convert"
    loader = importlib.machinery.SourceFileLoader("dolphin_convert", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

class TestNotifier(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.notifier = self.mod.Notifier

    @patch("subprocess.run")
    def test_send_start_non_silent(self, mock_run):
        self.notifier.send_start(count=3, target_format="webp", silent=False)
        self.assertTrue(mock_run.called)
        args = mock_run.call_args[0][0]
        self.assertIn("notify-send", args)
        self.assertIn("Dolphin Converter", args)
        self.assertTrue(any("3" in a and "webp" in a.lower() for a in args))

    @patch("subprocess.run")
    def test_send_start_silent(self, mock_run):
        self.notifier.send_start(count=3, target_format="webp", silent=True)
        self.assertFalse(mock_run.called)

    @patch("subprocess.run")
    def test_send_start_zero_count(self, mock_run):
        self.notifier.send_start(count=0, target_format="webp", silent=False)
        self.assertFalse(mock_run.called)

    @patch("subprocess.run")
    def test_send_start_single(self, mock_run):
        self.notifier.send_start(count=1, target_format="webp", silent=False)
        self.assertTrue(mock_run.called)
        args = mock_run.call_args[0][0]
        self.assertTrue(any("1 fichier vers WEBP" in a for a in args))

    @patch("subprocess.run")
    def test_send_success_single(self, mock_run):
        self.notifier.send_success(success_count=1, target_format="png", sample_file=Path("/home/user/photo.png"))
        self.assertTrue(mock_run.called)
        args = mock_run.call_args[0][0]
        self.assertIn("notify-send", args)
        self.assertTrue(any("photo.png" in a for a in args))

    @patch("subprocess.run")
    def test_send_success_multiple(self, mock_run):
        self.notifier.send_success(success_count=3, target_format="jpg")
        self.assertTrue(mock_run.called)
        args = mock_run.call_args[0][0]
        self.assertIn("notify-send", args)
        self.assertTrue(any("3 fichiers convertis avec succes vers JPG." in a for a in args))

    @patch("subprocess.run")
    def test_send_success_zero_count(self, mock_run):
        self.notifier.send_success(success_count=0, target_format="png")
        self.assertFalse(mock_run.called)

    @patch("subprocess.run")
    def test_send_error(self, mock_run):
        self.notifier.send_error("Erreur critique test")
        self.assertTrue(mock_run.called)
        args = mock_run.call_args[0][0]
        self.assertIn("notify-send", args)
        self.assertIn("critical", args)
        self.assertTrue(any("Erreur critique test" in a for a in args))

    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_run_notify_without_notify_send(self, mock_run, mock_which):
        self.notifier.send_error("Test sans notify-send")
        self.assertFalse(mock_run.called)

    @patch("shutil.which", return_value="/usr/bin/notify-send")
    @patch("subprocess.run", side_effect=OSError("Command failed"))
    def test_run_notify_oserror_handled(self, mock_run, mock_which):
        # Should not raise exception
        self.notifier.send_error("Test oserror")
        self.assertTrue(mock_run.called)

if __name__ == "__main__":
    unittest.main()
