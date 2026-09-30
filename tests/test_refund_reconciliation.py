from decimal import Decimal
import unittest

from backend.refund_reconciliation import RefundReconciliationService

class RefundReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.service = RefundReconciliationService()

    def test_matches_same_order_reference_and_amount(self):
        result = self.service.reconcile(
            [{"order_id":"ORDER-001","transaction_reference":"PSP-ABC","amount":"56,25","status":"REFUNDED"}],
            [{"order_id":"ORDER-001","transaction_reference":"PSP-ABC","amount":"56,25"}],
        )
        self.assertEqual(result["totals"]["matched"], 1)

    def test_reports_amount_difference(self):
        result = self.service.reconcile(
            [{"order_id":"ORDER-002","transaction_reference":"PSP-XYZ","amount":"60,00","status":"REFUNDED"}],
            [{"order_id":"ORDER-002","transaction_reference":"PSP-XYZ","amount":"56,25"}],
        )
        self.assertEqual(result["totals"]["differences"], 1)
        self.assertEqual(Decimal(result["differences"][0]["difference"]), Decimal("3.75"))

    def test_reports_missing_transaction(self):
        result = self.service.reconcile([], [{"order_id":"ORDER-003","transaction_reference":"PSP-NOT-FOUND","amount":"10,00"}])
        self.assertEqual(result["totals"]["pending"], 1)

if __name__ == "__main__":
    unittest.main()
