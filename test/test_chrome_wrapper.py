import unittest
from unittest.mock import patch

from flathunter.chrome_wrapper import get_chrome_version

class ChromeWrapperTest(unittest.TestCase):

    @patch("flathunter.chrome_wrapper.get_command_output")
    def test_parse_chrome_version(self, subprocess_mock):
        subprocess_mock.side_effect = [
            None, None, None,
            None, 'Chromium 107.0.5304.87 built on Debian bookworm/sid, running on Debian bookworm/sid',
            'Google Chrome 107.0.5304.110',
            'Chromium 107.0.5304.87 built on Debian 11.5, running on Debian 11.5'
        ]
        self.assertEqual(get_chrome_version(), None)
        self.assertEqual(get_chrome_version(), "107")
        self.assertEqual(get_chrome_version(), "107")
        self.assertEqual(get_chrome_version(), "107")
