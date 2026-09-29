import unittest
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

class TestNamingResolver(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.resolver = self.mod.NamingResolver

    def test_extension_replacement(self):
        source = Path("/tmp/photos/vacances.jpg")
        target = self.resolver.resolve_target_path(source, "png")
        self.assertEqual(target, Path("/tmp/photos/vacances.png"))

    def test_extension_replacement_lowercase(self):
        source = Path("/tmp/photos/DOC.JPG")
        target = self.resolver.resolve_target_path(source, "WEBP")
        self.assertEqual(target, Path("/tmp/photos/DOC.webp"))

    def test_custom_output_dir(self):
        source = Path("/tmp/photos/vacances.jpg")
        out_dir = Path("/tmp/converted")
        target = self.resolver.resolve_target_path(source, "png", output_dir=out_dir)
        self.assertEqual(target, Path("/tmp/converted/vacances.png"))

    def test_collision_incrementation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            target = base / "image.png"
            target.touch()

            unique_1 = self.resolver.get_unique_path(target)
            self.assertEqual(unique_1, base / "image_1.png")
            unique_1.touch()

            unique_2 = self.resolver.get_unique_path(target)
            self.assertEqual(unique_2, base / "image_2.png")

if __name__ == "__main__":
    unittest.main()
