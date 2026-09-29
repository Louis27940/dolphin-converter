import unittest
import subprocess
from pathlib import Path
import tempfile
import shutil

class TestEndToEndConversion(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.bin_path = Path(__file__).parent.parent / "bin" / "dolphin-convert"

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_e2e_image_conversion(self):
        if not shutil.which("magick") and not shutil.which("convert"):
            self.skipTest("ImageMagick non installe")

        src = Path(self.tmpdir) / "test.png"
        tool = shutil.which("magick") or "convert"
        subprocess.run([tool, "-size", "100x100", "xc:blue", str(src)], check=True)

        res = subprocess.run([str(self.bin_path), "--silent", "--format", "webp", str(src)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)

        expected = Path(self.tmpdir) / "test.webp"
        self.assertTrue(expected.exists())
        self.assertGreater(expected.stat().st_size, 0)

    def test_e2e_audio_extraction(self):
        if not shutil.which("ffmpeg"):
            self.skipTest("FFmpeg non installe")

        src = Path(self.tmpdir) / "synth.wav"
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-f", "lavfi",
            "-i", "sine=frequency=440:duration=1", str(src)
        ], check=True)

        res = subprocess.run([str(self.bin_path), "--silent", "--format", "mp3", str(src)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)

        expected = Path(self.tmpdir) / "synth.mp3"
        self.assertTrue(expected.exists())
        self.assertGreater(expected.stat().st_size, 0)

    def test_e2e_pandoc_md_to_docx_and_html(self):
        if not shutil.which("pandoc"):
            self.skipTest("Pandoc non installe")

        src = Path(self.tmpdir) / "notes.md"
        src.write_text("# Titre Document\n\nCeci est un test de conversion Pandoc.")

        # Test MD -> DOCX
        res_docx = subprocess.run([str(self.bin_path), "--silent", "--format", "docx", str(src)], capture_output=True, text=True)
        self.assertEqual(res_docx.returncode, 0)
        expected_docx = Path(self.tmpdir) / "notes.docx"
        self.assertTrue(expected_docx.exists())
        self.assertGreater(expected_docx.stat().st_size, 1000)

        # Test MD -> HTML
        res_html = subprocess.run([str(self.bin_path), "--silent", "--format", "html", str(src)], capture_output=True, text=True)
        self.assertEqual(res_html.returncode, 0)
        expected_html = Path(self.tmpdir) / "notes.html"
        self.assertTrue(expected_html.exists())
        content = expected_html.read_text()
        self.assertIn("Titre Document", content)

    def test_e2e_pandoc_docx_to_md(self):
        if not shutil.which("pandoc"):
            self.skipTest("Pandoc non installe")

        md_src = Path(self.tmpdir) / "original.md"
        md_src.write_text("# Chapitre 1\n\nTexte du document.")
        docx_file = Path(self.tmpdir) / "original.docx"
        subprocess.run(["pandoc", str(md_src), "-o", str(docx_file)], check=True)

        # Convert DOCX -> MD
        out_dir = Path(self.tmpdir) / "out_md"
        out_dir.mkdir()
        res = subprocess.run([str(self.bin_path), "--silent", "--format", "md", "-o", str(out_dir), str(docx_file)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        expected_md = out_dir / "original.md"
        self.assertTrue(expected_md.exists())
        content = expected_md.read_text()
        self.assertIn("Chapitre 1", content)

if __name__ == "__main__":
    unittest.main()
