"""Synthetic received-catalog checks; never network or package execution evidence."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent / 'runtime'))
from audit_shipping_payload import catalog_checks


class ShippingCatalogProtocolTests(unittest.TestCase):
    def check(self, version=6, digest='a' * 64, schema='3.1.0'):
        public = {'schemaVersion': schema, 'protocolVersion': version, 'contentDigest': digest}
        return catalog_checks([('client', {'public_snapshot': json.dumps(public)})], {'catalog_digest': 'a' * 64})[0]['status']

    def test_current_received_protocol_and_full_digest_pass(self):
        self.assertEqual(self.check(), 'PASS')

    def test_old_future_and_missing_protocol_are_rejected(self):
        for version in (3, 4, 5, 7, None):
            self.assertEqual(self.check(version=version), 'FAIL')

    def test_wrong_schema_and_stale_catalog_are_rejected(self):
        self.assertEqual(self.check(schema='3.0.0'), 'FAIL')
        self.assertEqual(self.check(digest='b' * 64), 'FAIL')
        self.assertEqual(self.check(digest=None), 'FAIL')


if __name__ == '__main__':
    unittest.main()
