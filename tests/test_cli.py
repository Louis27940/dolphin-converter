import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import importlib.machinery
import importlib.util

def load_module():
    script_path = Path(__file__).parent.parent / "bin" / "dolphin-convert"
    loader = importlib.machinery.SourceFileLoader("dolphin_convert", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

DOLPHIN_CONVERT = load_module()

class TestCliAndDispatcher(unittest.TestCase):
    def setUp(self):
        self.mod = DOLPHIN_CONVERT

    def test_dispatcher_finds_adapter(self):
        dispatcher = self.mod.ConversionDispatcher()
        adapter_img = dispatcher.get_adapter(Path("photo.jpg"), "png")
        self.assertIsInstance(adapter_img, self.mod.ImageAdapter)

        adapter_media = dispatcher.get_adapter(Path("video.mp4"), "mp3")
        self.assertIsInstance(adapter_media, self.mod.MediaAdapter)

        adapter_doc = dispatcher.get_adapter(Path("doc.docx"), "pdf")
        self.assertIsInstance(adapter_doc, self.mod.DocumentAdapter)

    def test_dispatcher_unsupported_format(self):
        dispatcher = self.mod.ConversionDispatcher()
        with self.assertRaises(self.mod.ConversionError):
            dispatcher.get_adapter(Path("audio.mp3"), "docx")

    def test_dispatcher_convert_single_source_not_found(self):
        dispatcher = self.mod.ConversionDispatcher()
        with self.assertRaises(self.mod.ConversionError) as ctx:
            dispatcher.convert_single(Path("/nonexistent/file.jpg"), "png")
        self.assertIn("Le fichier source n'existe pas", str(ctx.exception))

    def test_dispatcher_convert_single_success(self):
        dispatcher = self.mod.ConversionDispatcher()
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "test.jpg"
            src.touch()
            out_dir = Path(tmpdir) / "output"
            out_dir.mkdir()

            with patch.object(self.mod.ImageAdapter, "convert", return_value=out_dir / "test.png") as mock_convert:
                out = dispatcher.convert_single(src, "png", output_dir=out_dir, quality="80")
                self.assertEqual(out, out_dir / "test.png")
                mock_convert.assert_called_once_with(src, out_dir / "test.png", quality="80")

    def test_dispatcher_run_batch_empty(self):
        dispatcher = self.mod.ConversionDispatcher()
        with patch.object(self.mod.Notifier, "send_start") as mock_start:
            ret = dispatcher.run_batch([], "png")
            self.assertEqual(ret, 0)
            mock_start.assert_not_called()

    @patch.object(DOLPHIN_CONVERT.Notifier, "send_error")
    @patch.object(DOLPHIN_CONVERT.Notifier, "send_success")
    @patch.object(DOLPHIN_CONVERT.Notifier, "send_start")
    def test_dispatcher_run_batch_all_failures(self, mock_start, mock_success, mock_error):
        dispatcher = self.mod.ConversionDispatcher()
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = Path(tmpdir) / "f1.jpg"
            f1.touch()

            with patch.object(self.mod.ImageAdapter, "convert", side_effect=RuntimeError("Boom")):
                ret = dispatcher.run_batch([f1], "png")
                self.assertEqual(ret, 1)
                self.assertTrue(mock_start.called)
                self.assertFalse(mock_success.called)
                self.assertTrue(mock_error.called)
                self.assertIn("Boom", mock_error.call_args[0][0])

    @patch.object(DOLPHIN_CONVERT.Notifier, "send_error")
    @patch.object(DOLPHIN_CONVERT.Notifier, "send_success")
    @patch.object(DOLPHIN_CONVERT.Notifier, "send_start")
    def test_dispatcher_run_batch_partial_failure(self, mock_start, mock_success, mock_error):
        dispatcher = self.mod.ConversionDispatcher()
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = Path(tmpdir) / "f1.jpg"
            f2 = Path(tmpdir) / "f2.jpg"
            f1.touch()
            f2.touch()

            def fake_convert(src, dst, quality=None):
                if src == f1:
                    return dst
                raise RuntimeError("f2 failed")

            with patch.object(self.mod.ImageAdapter, "convert", side_effect=fake_convert):
                ret = dispatcher.run_batch([f1, f2], "png")
                self.assertEqual(ret, 0)
                self.assertTrue(mock_start.called)
                self.assertTrue(mock_success.called)
                self.assertTrue(mock_error.called)
                self.assertIn("f2 failed", mock_error.call_args[0][0])

    @patch.object(DOLPHIN_CONVERT.Notifier, "send_error")
    def test_dispatcher_run_batch_more_than_three_errors(self, mock_error):
        dispatcher = self.mod.ConversionDispatcher()
        with tempfile.TemporaryDirectory() as tmpdir:
            files = []
            for i in range(5):
                f = Path(tmpdir) / f"f{i}.jpg"
                f.touch()
                files.append(f)

            with patch.object(self.mod.ImageAdapter, "convert", side_effect=RuntimeError("Err")):
                ret = dispatcher.run_batch(files, "png")
                self.assertEqual(ret, 1)
                self.assertTrue(mock_error.called)
                err_text = mock_error.call_args[0][0]
                self.assertIn("autre(s) erreur(s)", err_text)

    @patch.object(DOLPHIN_CONVERT.Notifier, "send_start")
    @patch.object(DOLPHIN_CONVERT.Notifier, "send_success")
    def test_cli_execution_batch(self, mock_success, mock_start):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = Path(tmpdir) / "f1.jpg"
            f2 = Path(tmpdir) / "f2.jpg"
            f1.touch()
            f2.touch()

            with patch.object(self.mod.ImageAdapter, "convert", side_effect=lambda src, dst, quality=None: dst):
                ret = self.mod.cli_main(["--format", "webp", str(f1), str(f2)])
                self.assertEqual(ret, 0)
                self.assertTrue(mock_start.called)
                self.assertTrue(mock_success.called)

    @patch("sys.stderr")
    def test_cli_missing_format_argument(self, mock_stderr):
        ret = self.mod.cli_main(["photo.jpg"])
        self.assertNotEqual(ret, 0)

    @patch("sys.stderr")
    def test_cli_missing_files_argument(self, mock_stderr):
        ret = self.mod.cli_main(["-f", "png"])
        self.assertNotEqual(ret, 0)

    @patch.object(DOLPHIN_CONVERT.Notifier, "send_start")
    @patch.object(DOLPHIN_CONVERT.Notifier, "send_success")
    def test_cli_options_parsing(self, mock_success, mock_start):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = Path(tmpdir) / "f1.jpg"
            f1.touch()
            out_dir = Path(tmpdir) / "custom_out"
            out_dir.mkdir()

            with patch.object(self.mod.ImageAdapter, "convert", side_effect=lambda src, dst, quality=None: dst) as mock_conv:
                ret = self.mod.cli_main(["-f", "webp", "-q", "75", "-o", str(out_dir), "--silent", str(f1)])
                self.assertEqual(ret, 0)
                mock_start.assert_called_once_with(count=1, target_format="webp", silent=True)
                self.assertTrue(mock_success.called)
                mock_conv.assert_called_once_with(f1.resolve(), out_dir.resolve() / "f1.webp", quality="75")

    def test_dispatcher_same_format_in_place_error(self):
        dispatcher = self.mod.ConversionDispatcher()
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "image.png"
            src.touch()

            # output_dir is None
            with self.assertRaises(self.mod.ConversionError) as ctx:
                dispatcher.convert_single(src, "png")
            self.assertIn("Le fichier source 'image.png' est deja au format PNG.", str(ctx.exception))

            # output_dir is src.parent
            with self.assertRaises(self.mod.ConversionError) as ctx:
                dispatcher.convert_single(src, "PNG", output_dir=src.parent)
            self.assertIn("Le fichier source 'image.png' est deja au format PNG.", str(ctx.exception))

            # Different output_dir does NOT raise
            out_dir = Path(tmpdir) / "other"
            out_dir.mkdir()
            with patch.object(self.mod.ImageAdapter, "convert", return_value=out_dir / "image.png"):
                res = dispatcher.convert_single(src, "png", output_dir=out_dir)
                self.assertEqual(res, out_dir / "image.png")

    def test_dispatcher_batch_concurrent_reservation(self):
        dispatcher = self.mod.ConversionDispatcher()
        with tempfile.TemporaryDirectory() as tmpdir:
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()
            f1 = dir1 / "photo.jpg"
            f2 = dir2 / "photo.jpg"
            f1.touch()
            f2.touch()
            out_dir = Path(tmpdir) / "out"
            out_dir.mkdir()

            allocated_targets = []
            def fake_convert(src, dst, quality=None):
                import time
                time.sleep(0.02)
                dst.touch()
                allocated_targets.append(dst)
                return dst

            with patch.object(self.mod.ImageAdapter, "convert", side_effect=fake_convert):
                ret = dispatcher.run_batch([f1, f2], "png", output_dir=out_dir, silent=True)
                self.assertEqual(ret, 0)
                self.assertEqual(len(allocated_targets), 2)
                target_names = {t.name for t in allocated_targets}
                self.assertEqual(target_names, {"photo.png", "photo_1.png"})

if __name__ == "__main__":
    unittest.main()
