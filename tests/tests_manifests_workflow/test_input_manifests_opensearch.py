# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import os
import unittest
from unittest.mock import MagicMock, call, patch

from manifests.input_manifest import Component
from manifests_workflow.input_manifests_opensearch import InputManifestsOpenSearch


class TestInputManifestsOpenSearch(unittest.TestCase):
    def test_files(self):
        files = InputManifestsOpenSearch.files()
        self.assertTrue(len(files) >= 2)
        manifest = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "manifests",
                "1.1.0",
                "opensearch-1.1.0.yml",
            )
        )
        self.assertTrue(manifest in files)

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("manifests_workflow.input_manifests.InputManifests.add_to_cron")
    @patch("manifests_workflow.input_manifests.InputManifest.from_path")
    @patch("manifests_workflow.input_manifests_opensearch.ComponentOpenSearchMin")
    @patch("manifests_workflow.input_manifests_opensearch.ComponentOpenSearch")
    @patch("manifests_workflow.input_manifests.InputManifest")
    def test_update(self, mock_input_manifest, mock_component_opensearch, mock_component_opensearch_min, mock_input_manifest_from_path, mock_add_to_cron, *mocks):
        mock_component_opensearch_min.return_value = MagicMock(name="OpenSearch")
        mock_component_opensearch_min.branches.return_value = ["main", "0.9.0"]
        mock_component_opensearch_min.checkout.return_value = MagicMock(version="0.9.0")
        mock_component_opensearch.return_value = MagicMock(name="common-utils")
        mock_component_opensearch.checkout.return_value = MagicMock(version="0.10.0")
        mock_input_manifest_from_path.return_value.components = {
            "common-utils": Component({"name": "common-utils", "repository": "git", "ref": "ref"})
        }
        manifests = InputManifestsOpenSearch()
        manifests.update()
        self.assertEqual(mock_input_manifest().to_file.call_count, 2)
        calls = [
            call(
                os.path.join(
                    InputManifestsOpenSearch.manifests_path(),
                    "0.10.0",
                    "opensearch-0.10.0.yml",
                )
            ),
            call(
                os.path.join(
                    InputManifestsOpenSearch.manifests_path(),
                    "0.9.0",
                    "opensearch-0.9.0.yml",
                )
            ),
        ]
        mock_input_manifest().to_file.assert_has_calls(calls)
        mock_add_to_cron.assert_has_calls([
            call('0.10.0'),
            call('0.9.0')
        ])

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("manifests_workflow.input_manifests.InputManifests.add_to_cron")
    @patch("manifests_workflow.input_manifests_opensearch.ComponentOpenSearchMin")
    @patch("manifests_workflow.input_manifests_opensearch.ComponentOpenSearch")
    @patch("manifests_workflow.input_manifests_opensearch.InputManifestsOpenSearch.write_manifest")
    def test_update_with_latest_manifest(self, mock_write_manifest, mock_component_opensearch, mock_component_opensearch_min, mock_add_to_cron, *mocks):
        mock_component_opensearch_min.return_value = MagicMock(name="OpenSearch")
        mock_component_opensearch_min.branches.return_value = ["main"]
        mock_component_opensearch_min.checkout.return_value = MagicMock(version="0.9.0")
        mock_component_opensearch.return_value = MagicMock(name="common-utils")
        mock_component_opensearch.checkout.return_value = MagicMock(version="0.10.0")
        manifests = InputManifestsOpenSearch()
        manifests.update()
        mock_component_opensearch_min.branches.assert_called()
        mock_write_manifest.assert_called_with("0.9.0", [mock_component_opensearch_min.checkout.return_value])
        mock_add_to_cron.assert_called_with("0.9.0")
