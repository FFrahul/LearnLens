import unittest
from unittest.mock import patch

import validate_local


class ValidateLocalTests(unittest.TestCase):
    def test_required_modules_are_checked(self):
        with patch(
            "validate_local.importlib.util.find_spec",
            return_value=object()
        ), patch("validate_local.run") as run:
            with patch(
                "validate_local.urllib.request.urlopen"
            ) as urlopen:
                response = urlopen.return_value.__enter__.return_value
                response.status = 200
                validate_local.main()

        self.assertEqual(run.call_count, 3)


if __name__ == "__main__":
    unittest.main()
