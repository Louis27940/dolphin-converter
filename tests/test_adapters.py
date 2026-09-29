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

class TestAdapters(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_image_adapter_can_handle(self):
        adapter = self.mod.ImageAdapter()
        self.assertTrue(adapter.can_handle(Path("photo.jpg"), "webp"))
        self.assertTrue(adapter.can_handle(Path("dessin.png"), "jpg"))
        self.assertFalse(adapter.can_handle(Path("video.mp4"), "webp"))

    def test_media_adapter_can_handle(self):
        adapter = self.mod.MediaAdapter()
        self.assertTrue(adapter.can_handle(Path("video.mp4"), "mkv"))
        self.assertTrue(adapter.can_handle(Path("video.mp4"), "mp3"))
        self.assertTrue(adapter.can_handle(Path("audio.wav"), "ogg"))
        self.assertFalse(adapter.can_handle(Path("doc.pdf"), "mp3"))

    def test_document_adapter_can_handle(self):
        adapter = self.mod.DocumentAdapter()
        self.assertTrue(adapter.can_handle(Path("doc.pdf"), "png"))
        self.assertTrue(adapter.can_handle(Path("note.md"), "pdf"))
        self.assertTrue(adapter.can_handle(Path("fichier.docx"), "pdf"))
        self.assertTrue(adapter.can_handle(Path("note.md"), "docx"))
        self.assertTrue(adapter.can_handle(Path("note.md"), "html"))
        self.assertFalse(adapter.can_handle(Path("fichier.docx"), "png"))

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/magick")
    def test_image_convert_command(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        adapter = self.mod.ImageAdapter()
        src = Path("/tmp/test.png")
        dst = Path("/tmp/test.webp")
        out = adapter.convert(src, dst, quality="80")
        self.assertEqual(out, dst)
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "/usr/bin/magick")
        self.assertIn("-quality", args)
        self.assertIn("80", args)

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_media_convert_audio_extraction(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        adapter = self.mod.MediaAdapter()
        src = Path("/tmp/video.mp4")
        dst = Path("/tmp/video.mp3")
        out = adapter.convert(src, dst)
        self.assertEqual(out, dst)
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "/usr/bin/ffmpeg")
        self.assertIn("-vn", args)
        self.assertIn("libmp3lame", args)

    @patch("shutil.which", return_value=None)
    def test_missing_tool_error(self, mock_which):
        adapter = self.mod.ImageAdapter()
        with self.assertRaises(self.mod.MissingToolError):
            adapter.convert(Path("test.png"), Path("test.webp"))

    def test_base_adapter_abstract_methods(self):
        adapter = self.mod.BaseAdapter()
        with self.assertRaises(NotImplementedError):
            adapter.can_handle(Path("test.png"), "webp")
        with self.assertRaises(NotImplementedError):
            adapter.convert(Path("test.png"), Path("test.webp"))

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/magick")
    def test_image_convert_default_qualities(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        adapter = self.mod.ImageAdapter()

        # JPEG default 90
        adapter.convert(Path("/tmp/test.png"), Path("/tmp/test.jpg"))
        args = mock_run.call_args[0][0]
        self.assertIn("-quality", args)
        self.assertIn("90", args)

        # WebP default 85
        adapter.convert(Path("/tmp/test.png"), Path("/tmp/test.webp"))
        args = mock_run.call_args[0][0]
        self.assertIn("-quality", args)
        self.assertIn("85", args)

        # AVIF default 80
        adapter.convert(Path("/tmp/test.png"), Path("/tmp/test.avif"))
        args = mock_run.call_args[0][0]
        self.assertIn("-quality", args)
        self.assertIn("80", args)

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/magick")
    def test_image_convert_failure(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="Corrupt image file", stdout="")
        adapter = self.mod.ImageAdapter()
        with self.assertRaises(self.mod.ConversionError) as ctx:
            adapter.convert(Path("/tmp/bad.png"), Path("/tmp/bad.jpg"))
        self.assertIn("Corrupt image file", str(ctx.exception))

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_media_convert_targets(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        adapter = self.mod.MediaAdapter()

        # MP4
        adapter.convert(Path("/tmp/input.mkv"), Path("/tmp/output.mp4"))
        args = mock_run.call_args[0][0]
        self.assertIn("libx264", args)
        self.assertIn("+faststart", args)

        # MKV
        adapter.convert(Path("/tmp/input.mp4"), Path("/tmp/output.mkv"))
        args = mock_run.call_args[0][0]
        self.assertIn("libx264", args)

        # WebM
        adapter.convert(Path("/tmp/input.mp4"), Path("/tmp/output.webm"))
        args = mock_run.call_args[0][0]
        self.assertIn("libvpx-vp9", args)
        self.assertIn("libopus", args)

        # AAC
        adapter.convert(Path("/tmp/input.mp4"), Path("/tmp/output.aac"))
        args = mock_run.call_args[0][0]
        self.assertIn("aac", args)
        self.assertIn("-vn", args)

        # FLAC
        adapter.convert(Path("/tmp/input.wav"), Path("/tmp/output.flac"))
        args = mock_run.call_args[0][0]
        self.assertIn("flac", args)

        # WAV
        adapter.convert(Path("/tmp/input.mp3"), Path("/tmp/output.wav"))
        args = mock_run.call_args[0][0]
        self.assertIn("pcm_s16le", args)

        # OGG
        adapter.convert(Path("/tmp/input.mp3"), Path("/tmp/output.ogg"))
        args = mock_run.call_args[0][0]
        self.assertIn("libvorbis", args)

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_media_convert_failure(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="FFmpeg decoding error", stdout="")
        adapter = self.mod.MediaAdapter()
        with self.assertRaises(self.mod.ConversionError) as ctx:
            adapter.convert(Path("/tmp/bad.mp4"), Path("/tmp/bad.mp3"))
        self.assertIn("FFmpeg decoding error", str(ctx.exception))

    @patch("shutil.which", return_value=None)
    def test_media_convert_missing_tool(self, mock_which):
        adapter = self.mod.MediaAdapter()
        with self.assertRaises(self.mod.MissingToolError):
            adapter.convert(Path("/tmp/input.mp4"), Path("/tmp/output.mp3"))

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/pdftoppm")
    def test_document_convert_pdf_to_images(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        adapter = self.mod.DocumentAdapter()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src = tmp_path / "document.pdf"
            src.touch()
            dst = tmp_path / "document.png"

            # Simulate single page generation
            single_page = tmp_path / "document-1.png"
            single_page.touch()

            out = adapter.convert(src, dst)
            self.assertEqual(out, dst)
            self.assertTrue(dst.exists())
            self.assertFalse(single_page.exists())

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/libreoffice")
    def test_document_convert_doc_to_pdf(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        adapter = self.mod.DocumentAdapter()
        src = Path("/tmp/test.docx")
        dst = Path("/tmp/test.pdf")

        out = adapter.convert(src, dst)
        self.assertEqual(out, dst)
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "/usr/bin/libreoffice")
        self.assertIn("--headless", args)
        self.assertIn("--convert-to", args)
        self.assertIn("pdf", args)

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/pandoc")
    def test_document_convert_md_to_docx(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        adapter = self.mod.DocumentAdapter()
        src = Path("/tmp/test.md")
        dst = Path("/tmp/test.docx")

        out = adapter.convert(src, dst)
        self.assertEqual(out, dst)
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "/usr/bin/pandoc")
        self.assertIn("-o", args)

    @patch("shutil.which", return_value=None)
    def test_document_convert_missing_tools(self, mock_which):
        adapter = self.mod.DocumentAdapter()

        # Missing poppler
        with self.assertRaises(self.mod.MissingToolError) as ctx:
            adapter.convert(Path("/tmp/test.pdf"), Path("/tmp/test.png"))
        self.assertEqual(ctx.exception.tool_name, "poppler")

        # Missing libreoffice
        with self.assertRaises(self.mod.MissingToolError) as ctx:
            adapter.convert(Path("/tmp/test.docx"), Path("/tmp/test.pdf"))
        self.assertEqual(ctx.exception.tool_name, "libreoffice")

        # Missing pandoc
        with self.assertRaises(self.mod.MissingToolError) as ctx:
            adapter.convert(Path("/tmp/test.md"), Path("/tmp/test.docx"))
        self.assertEqual(ctx.exception.tool_name, "pandoc")

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/libreoffice")
    def test_document_convert_failure(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="LibreOffice crash", stdout="")
        adapter = self.mod.DocumentAdapter()
        with self.assertRaises(self.mod.ConversionError) as ctx:
            adapter.convert(Path("/tmp/test.docx"), Path("/tmp/test.pdf"))
        self.assertIn("LibreOffice crash", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
