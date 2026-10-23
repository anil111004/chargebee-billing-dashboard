from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from chargebee import Chargebee, Filters

from config import CHARGEBEE_API_KEY, CHARGEBEE_SITE, DEMO_MODE

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class ChargebeeService:
    def __init__(self):
        self.api_key = CHARGEBEE_API_KEY
        self.site = CHARGEBEE_SITE
        self.demo_mode = DEMO_MODE
        self.client = None

        if self.api_key and self.site:
            try:
                self.client = Chargebee(api_key=self.api_key, site=self.site)
                logger.info("Chargebee client initialized for site %s", self.site)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Chargebee initialization failed: %s", exc)
                self.client = None

    def get_demo_customers(self):
        return [
            {"id": "cust_demo_101", "first_name": "Ava", "last_name": "Patel", "email": "ava@northstar.io", "created_at": 1710000000},
            {"id": "cust_demo_102", "first_name": "Daniel", "last_name": "Kim", "email": "daniel@bluepeak.io", "created_at": 1712000000},
            {"id": "cust_demo_103", "first_name": "Chloe", "last_name": "Nguyen", "email": "chloe@harborlabs.ai", "created_at": 1714000000},
        ]

    def get_demo_subscriptions(self):
        return [
            {"id": "sub_demo_201", "customer_id": "cust_demo_101", "status": "active", "plan_id": "starter_plan", "item_price_id": "price_starter", "trial_end": 1733000000, "created_at": 1710000000},
            {"id": "sub_demo_202", "customer_id": "cust_demo_102", "status": "trialing", "plan_id": "pro_plan", "item_price_id": "price_pro", "trial_end": 1735600000, "created_at": 1712000000},
            {"id": "sub_demo_203", "customer_id": "cust_demo_103", "status": "cancelled", "plan_id": "basic_plan", "item_price_id": "price_basic", "trial_end": 1716000000, "created_at": 1714000000},
        ]

    def get_demo_invoices(self):
        return [
            {"id": "inv_demo_301", "customer_id": "cust_demo_101", "status": "paid", "amount": 4990, "currency_code": "USD", "date": 1710000000},
            {"id": "inv_demo_302", "customer_id": "cust_demo_102", "status": "payment_due", "amount": 9900, "currency_code": "USD", "date": 1712000000},
            {"id": "inv_demo_303", "customer_id": "cust_demo_103", "status": "voided", "amount": 0, "currency_code": "USD", "date": 1714000000},
        ]

    def _normalize_customer(self, customer: Any) -> Dict[str, Any]:
        if customer is None:
            return {}
        return {
            "id": getattr(customer, "id", ""),
            "first_name": getattr(customer, "first_name", ""),
            "last_name": getattr(customer, "last_name", ""),
            "email": getattr(customer, "email", ""),
            "created_at": getattr(customer, "created_at", None),
            "name": getattr(customer, "first_name", "") + " " + getattr(customer, "last_name", ""),
        }

    def _normalize_subscription(self, subscription: Any) -> Dict[str, Any]:
        if subscription is None:
            return {}
        return {
            "id": getattr(subscription, "id", ""),
            "customer_id": getattr(subscription, "customer_id", ""),
            "status": getattr(subscription, "status", ""),
            "plan_id": getattr(subscription, "plan_id", ""),
            "item_price_id": getattr(subscription, "item_price_id", ""),
            "trial_end": getattr(subscription, "trial_end", None),
            "created_at": getattr(subscription, "created_at", None),
        }

    def _normalize_invoice(self, invoice: Any) -> Dict[str, Any]:
        if invoice is None:
            return {}
        return {
            "id": getattr(invoice, "id", ""),
            "customer_id": getattr(invoice, "customer_id", ""),
            "status": getattr(invoice, "status", ""),
            "amount": getattr(invoice, "total", 0) or getattr(invoice, "amount", 0),
            "currency_code": getattr(invoice, "currency_code", "USD"),
            "date": getattr(invoice, "date", None),
        }

    def _search_filter(self, items, search_text):
        if not search_text:
            return items
        keyword = search_text.lower().strip()
        return [
            item for item in items
            if keyword in str(item.get("id", "")).lower()
            or keyword in str(item.get("email", "")).lower()
            or keyword in str(item.get("customer_id", "")).lower()
            or keyword in str(item.get("status", "")).lower()
        ]

    def _pagination(self, items, page, limit):
        start = (page - 1) * limit
        end = start + limit
        return items[start:end], len(items)

    def test_connection(self):
        if self.demo_mode:
            return {"status": "ok", "message": "Demo mode active. Chargebee API is not required for local testing."}
        if not self.client:
            return {"status": "error", "message": "Chargebee credentials are missing or invalid."}
        try:
            response = self.client.Customer.list(self.client.Customer.ListParams(limit=1))
            return {"status": "ok", "message": "Chargebee connection successful."}
        except Exception as exc:
            logger.exception("Chargebee connection test failed: %s", exc)
            return {"status": "error", "message": "Chargebee connection failed. Check credentials and site configuration."}

    def list_customers(self, page=1, limit=10, search=""):
        if self.demo_mode:
            items = self.get_demo_customers()
            filtered = self._search_filter(items, search)
            paginated, total = self._pagination(filtered, page, limit)
            return {"items": paginated, "page": page, "limit": limit, "total": total, "source": "demo"}
        if not self.client:
            raise ValueError("Chargebee client is not configured.")
        try:
            offset = str((page - 1) * limit)
            params = self.client.Customer.ListParams(limit=limit, offset=offset)
            response = self.client.Customer.list(params)
            items = []
            for entry in response:
                customer = getattr(entry, "customer", None)
                if customer:
                    items.append(self._normalize_customer(customer))
            filtered = self._search_filter(items, search)
            paginated, total = self._pagination(filtered, page, limit)
            return {"items": paginated, "page": page, "limit": limit, "total": total, "source": "chargebee"}
        except Exception as exc:
            logger.exception("Error listing customers: %s", exc)
            raise

    def list_subscriptions(self, page=1, limit=10, status="all", search=""):
        if self.demo_mode:
            items = self.get_demo_subscriptions()
            if status and status != "all":
                items = [item for item in items if item.get("status") == status]
            filtered = self._search_filter(items, search)
            paginated, total = self._pagination(filtered, page, limit)
            return {"items": paginated, "page": page, "limit": limit, "total": total, "source": "demo"}
        if not self.client:
            raise ValueError("Chargebee client is not configured.")
        try:
            offset = str((page - 1) * limit)
            params = self.client.Subscription.ListParams(limit=limit, offset=offset)
            if status and status != "all":
                params.status = Filters.EnumFilter(IN=[status])
            response = self.client.Subscription.list(params)
            items = []
            for entry in response:
                subscription = getattr(entry, "subscription", None)
                if subscription:
                    items.append(self._normalize_subscription(subscription))
            filtered = self._search_filter(items, search)
            paginated, total = self._pagination(filtered, page, limit)
            return {"items": paginated, "page": page, "limit": limit, "total": total, "source": "chargebee"}
        except Exception as exc:
            logger.exception("Error listing subscriptions: %s", exc)
            raise

    def get_subscription(self, subscription_id):
        if self.demo_mode:
            for item in self.get_demo_subscriptions():
                if item["id"] == subscription_id:
                    return item
            return None
        if not self.client:
            raise ValueError("Chargebee client is not configured.")
        try:
            response = self.client.Subscription.retrieve(subscription_id)
            return self._normalize_subscription(getattr(response, "subscription", None))
        except Exception as exc:
            logger.exception("Error retrieving subscription: %s", exc)
            raise

    def create_subscription(self, payload: Dict[str, Any]):
        if self.demo_mode:
            customer_id = payload.get("customer_id", "").strip()
            plan_id = payload.get("plan_id", "").strip()
            item_price_id = payload.get("item_price_id", "").strip()
            if not customer_id:
                raise ValueError("Customer ID is required.")
            if not plan_id and not item_price_id:
                raise ValueError("Either plan_id or item_price_id is required.")
            created = {
                "id": f"sub_demo_{abs(hash(customer_id + str(len(customer_id))))}",
                "customer_id": customer_id,
                "plan_id": plan_id or item_price_id,
                "item_price_id": item_price_id or plan_id,
                "status": payload.get("status", "trialing"),
                "trial_end": payload.get("trial_end"),
                "created_at": 1717000000,
            }
            return {"subscription": created, "source": "demo"}
        if not self.client:
            raise ValueError("Chargebee client is not configured.")
        required_fields = ["customer_id"]
        for field in required_fields:
            if not payload.get(field):
                raise ValueError(f"{field} is required.")
        if not payload.get("plan_id") and not payload.get("item_price_id"):
            raise ValueError("Either plan_id or item_price_id is required.")
        try:
            params = {
                "customer_id": payload["customer_id"],
            }
            if payload.get("plan_id"):
                params["plan_id"] = payload["plan_id"]
            if payload.get("item_price_id"):
                params["item_price_id"] = payload["item_price_id"]
            if payload.get("trial_end"):
                params["trial_end"] = int(payload["trial_end"])
            response = self.client.Subscription.create(self.client.Subscription.CreateParams(**params))
            return {"subscription": getattr(response, "subscription", None), "source": "chargebee"}
        except Exception as exc:
            logger.exception("Error creating subscription: %s", exc)
            raise

    def list_invoices(self, page=1, limit=10, search=""):
        if self.demo_mode:
            items = self.get_demo_invoices()
            filtered = self._search_filter(items, search)
            paginated, total = self._pagination(filtered, page, limit)
            return {"items": paginated, "page": page, "limit": limit, "total": total, "source": "demo"}
        if not self.client:
            raise ValueError("Chargebee client is not configured.")
        try:
            offset = str((page - 1) * limit)
            params = self.client.Invoice.ListParams(limit=limit, offset=offset)
            response = self.client.Invoice.list(params)
            items = []
            for entry in response:
                invoice = getattr(entry, "invoice", None)
                if invoice:
                    items.append(self._normalize_invoice(invoice))
            filtered = self._search_filter(items, search)
            paginated, total = self._pagination(filtered, page, limit)
            return {"items": paginated, "page": page, "limit": limit, "total": total, "source": "chargebee"}
        except Exception as exc:
            logger.exception("Error listing invoices: %s", exc)
            raise

    def get_invoice(self, invoice_id):
        if self.demo_mode:
            for item in self.get_demo_invoices():
                if item["id"] == invoice_id:
                    return item
            return None
        if not self.client:
            raise ValueError("Chargebee client is not configured.")
        try:
            response = self.client.Invoice.retrieve(invoice_id)
            return self._normalize_invoice(getattr(response, "invoice", None))
        except Exception as exc:
            logger.exception("Error retrieving invoice: %s", exc)
            raise

    def get_dashboard(self):
        customers_response = self.list_customers(page=1, limit=100)
        subscriptions_response = self.list_subscriptions(page=1, limit=100)
        invoices_response = self.list_invoices(page=1, limit=100)

        customers = customers_response["items"]
        subscriptions = subscriptions_response["items"]
        invoices = invoices_response["items"]

        active_subscriptions = sum(1 for item in subscriptions if str(item.get("status", "")).lower() == "active")
        trialing_subscriptions = sum(1 for item in subscriptions if str(item.get("status", "")).lower() == "trialing")
        total_revenue = sum(float(item.get("amount", 0) or 0) for item in invoices)

        recent_subscriptions = sorted(subscriptions, key=lambda x: x.get("created_at") or 0, reverse=True)[:5]
        recent_invoices = sorted(invoices, key=lambda x: x.get("date") or 0, reverse=True)[:5]

        return {
            "metrics": {
                "total_customers": len(customers),
                "active_subscriptions": active_subscriptions,
                "trials_in_progress": trialing_subscriptions,
                "invoice_total": total_revenue,
            },
            "recent_subscriptions": recent_subscriptions,
            "recent_invoices": recent_invoices,
            "source": customers_response.get("source", "demo"),
        }
