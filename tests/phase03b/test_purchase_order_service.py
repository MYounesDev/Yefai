"""Tests for purchase order service — Phase 3B."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "server"))

import pytest

from services.purchase_order_service import (
    DuplicateOrderError,
    PurchaseOrder,
    create_auto_order,
    get_purchase_order,
    get_purchase_orders,
    update_po_status,
)


class TestCreateAutoOrder:
    def test_create_order(self):
        """Creating an order should return valid PurchaseOrder."""
        po = create_auto_order(part_id="1", quantity=3, trigger="crisis")
        assert isinstance(po, PurchaseOrder)
        assert po.part_id == "1"
        assert po.quantity == 3
        assert po.status == "ready_for_review"
        assert po.trigger == "crisis"
        assert po.po_id > 0

    def test_duplicate_prevention(self):
        """Same part within 24h should raise error."""
        create_auto_order(part_id="9999", quantity=1)
        with pytest.raises(DuplicateOrderError):
            create_auto_order(part_id="9999", quantity=1)

    def test_force_duplicate(self):
        """force=True should bypass duplicate check."""
        po1 = create_auto_order(part_id="8888", quantity=1)
        po2 = create_auto_order(part_id="8888", quantity=1, force=True)
        assert po2.po_id > po1.po_id


class TestGetPurchaseOrders:
    def test_list_orders(self):
        orders = get_purchase_orders()
        assert isinstance(orders, list)

    def test_filter_by_status(self):
        create_auto_order(part_id="7777", quantity=1)
        ready = get_purchase_orders(status="ready_for_review")
        assert all(po.status == "ready_for_review" for po in ready)


class TestGetPurchaseOrder:
    def test_get_existing(self):
        po = create_auto_order(part_id="6666", quantity=1)
        found = get_purchase_order(po.po_id)
        assert found is not None
        assert found.po_id == po.po_id

    def test_get_nonexistent(self):
        found = get_purchase_order(999999)
        assert found is None


class TestUpdatePoStatus:
    def test_approve(self):
        po = create_auto_order(part_id="5555", quantity=1)
        updated = update_po_status(po.po_id, "approved")
        assert updated is not None
        assert updated.status == "approved"

    def test_cancel(self):
        po = create_auto_order(part_id="4444", quantity=1)
        updated = update_po_status(po.po_id, "cancelled")
        assert updated is not None
        assert updated.status == "cancelled"

    def test_invalid_status(self):
        po = create_auto_order(part_id="3333", quantity=1)
        updated = update_po_status(po.po_id, "invalid_status")
        assert updated is None

    def test_cancelled_cannot_reactivate(self):
        po = create_auto_order(part_id="2222", quantity=1)
        update_po_status(po.po_id, "cancelled")
        updated = update_po_status(po.po_id, "approved")
        assert updated is None

    def test_invalid_po_id(self):
        updated = update_po_status(999999, "approved")
        assert updated is None
