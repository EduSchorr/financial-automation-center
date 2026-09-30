from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

@dataclass(frozen=True)
class RefundCandidate:
    order_id: str
    transaction_reference: str
    amount: Decimal
    status: str

class RefundReconciliationService:
    """Matches refund transactions against operational control rows.

    The public portfolio implementation keeps the reconciliation rules local and
    deliberately excludes production gateways, credentials and private endpoints.
    """

    @staticmethod
    def normalize_order(value) -> str:
        return "".join(ch for ch in str(value or "").strip().upper() if ch.isalnum())

    @staticmethod
    def normalize_reference(value) -> str:
        return "".join(ch for ch in str(value or "").strip().upper() if ch.isalnum())

    @staticmethod
    def money(value) -> Decimal:
        text = str(value or "0").replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        try:
            return Decimal(text).quantize(Decimal("0.01"))
        except Exception:
            return Decimal("0.00")

    def reconcile(self, transactions: Iterable[dict], control_rows: Iterable[dict]) -> dict:
        tx_index = {}
        for row in transactions:
            order_id = self.normalize_order(row.get("order_id"))
            reference = self.normalize_reference(row.get("transaction_reference"))
            if not order_id and not reference:
                continue
            tx_index[(order_id, reference)] = RefundCandidate(
                order_id=order_id,
                transaction_reference=reference,
                amount=self.money(row.get("amount")),
                status=str(row.get("status") or "").strip().upper(),
            )

        matched, pending, differences = [], [], []
        for row in control_rows:
            order_id = self.normalize_order(row.get("order_id"))
            reference = self.normalize_reference(row.get("transaction_reference"))
            expected = self.money(row.get("amount"))
            transaction = tx_index.get((order_id, reference))

            if not transaction:
                pending.append({**row, "reason": "transaction_not_found"})
                continue

            result = {
                "order_id": order_id,
                "transaction_reference": reference,
                "expected_amount": str(expected),
                "transaction_amount": str(transaction.amount),
                "transaction_status": transaction.status,
            }
            if transaction.amount != expected:
                result["difference"] = str(transaction.amount - expected)
                differences.append(result)
            else:
                matched.append(result)

        return {
            "matched": matched,
            "pending": pending,
            "differences": differences,
            "totals": {
                "matched": len(matched),
                "pending": len(pending),
                "differences": len(differences),
            },
        }
