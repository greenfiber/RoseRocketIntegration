import unittest
from backend import RoseRocketIntegrationBackend
from integrationutils import RoseRocketIntegrationUtils
from integration import RoseRocketIntegration

class TestOrderUpload(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.db=RoseRocketIntegrationBackend()
        self.rrutil=RoseRocketIntegrationUtils()

    def test_upload(self):
        pass