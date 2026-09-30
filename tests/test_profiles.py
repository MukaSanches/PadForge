import unittest
from pathlib import Path
from padforge.profile_manager import ProfileManager


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = ProfileManager(Path(__file__).resolve().parents[1] / "profiles")

    def test_profiles_load(self):
        self.assertGreaterEqual(len(self.manager.profiles), 5)

    def test_nfs_auto_match(self):
        p = self.manager.match_executable("C:/Games/NFSMW/speed.exe")
        self.assertIsNotNone(p)
        self.assertIn("Racing", p.name)

    def test_pes_auto_match(self):
        p = self.manager.match_executable("pes5.exe")
        self.assertIsNotNone(p)
        self.assertIn("Football", p.name)

    def test_unknown_no_match(self):
        self.assertIsNone(self.manager.match_executable("totally_unknown_game.exe"))


if __name__ == "__main__":
    unittest.main()
