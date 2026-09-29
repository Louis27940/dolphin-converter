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

if __name__ == "__main__":
    unittest.main()
