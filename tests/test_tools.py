"""Offline unit tests; these tests never contact a live n8n instance."""
import json
import os
import unittest
from unittest.mock import patch

from tools import N8NRestError, _configuration, _workflow_id, list_workflows, create_workflow


class ValidationTests(unittest.TestCase):
    def test_missing_configuration_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(N8NRestError):
                _configuration()

    def test_requires_https_for_remote_hosts(self):
        with patch.dict(os.environ, {"N8N_BASE_URL": "http://n8n.example.com", "N8N_API_KEY": "test"}):
            with self.assertRaises(N8NRestError):
                _configuration()

    def test_localhost_http_is_allowed_for_tests(self):
        with patch.dict(os.environ, {"N8N_BASE_URL": "http://localhost:5678/", "N8N_API_KEY": "test"}):
            base, key = _configuration()
            self.assertEqual(base, "http://localhost:5678")
            self.assertEqual(key, "test")

    def test_workflow_id_is_url_encoded(self):
        self.assertEqual(_workflow_id({"workflow_id": "abc/def"}), "abc%2Fdef")

    def test_invalid_workflow_id_rejected(self):
        with self.assertRaises(N8NRestError):
            _workflow_id({"workflow_id": " "})

    def test_limit_bounds(self):
        for limit in (0, 101, True, "5"):
            with self.subTest(limit=limit), self.assertRaises(N8NRestError):
                list_workflows({"limit": limit})

    def test_create_requires_workflow_shape(self):
        with self.assertRaises(N8NRestError):
            create_workflow({"workflow": {"name": "incomplete"}})


if __name__ == "__main__":
    unittest.main()
