import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.schema import VideoParams


class TestFlowType(unittest.TestCase):
    def test_flow_type_defaults_to_standard(self):
        params = VideoParams(video_subject="x")
        self.assertEqual(params.flow_type, "standard")

    def test_flow_type_accepts_math_explainer(self):
        params = VideoParams(video_subject="x", flow_type="math_explainer")
        self.assertEqual(params.flow_type, "math_explainer")


if __name__ == "__main__":
    unittest.main()
