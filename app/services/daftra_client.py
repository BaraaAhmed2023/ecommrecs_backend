import os
import httpx
from typing import Dict, Any, List
from datetime import datetime

class DaftraClient:
    def __init__(self):
        self.base_url = os.getenv("DAFTRA_BASE_URL", "https://app.daftra.com/api2")
        self.token = os.getenv("DAFTRA_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def prepare_invoice_data(self, order, user, order_items: List[Dict]) -> Dict[str, Any]:
        """Prepare invoice data for Daftra API"""

        # Map order items to Daftra line items
        line_items = []
        for item in order_items:
            line_items.append({
                "item_id": item["product"].daftra_item_id,  # type: ignore
                "quantity": item["quantity"],
                "price": item["price"],
                "description": item["product"].title,  # type: ignore
                "unit": "pcs"
            })

        # Get current date for invoice
        current_date = datetime.now().strftime("%Y-%m-%d")

        invoice_data = {
            "Invoice": {
                "contact_id": None,  # You might want to create/use contacts in Daftra
                "contact_name": user.name,  # type: ignore
                "contact_email": user.email,  # type: ignore
                "date": current_date,
                "due_date": current_date,
                "lines": line_items,
                "notes": f"Order #{order.id} from E-commerce Store"  # type: ignore
            }
        }

        return invoice_data

    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create invoice in Daftra"""

        if not self.token:
            raise Exception("Daftra token not configured")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/invoices",
                    json=invoice_data,
                    headers=self.headers,
                    timeout=30.0
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPError as e:
                raise Exception(f"Daftra API error: {str(e)}")
            except Exception as e:
                raise Exception(f"Failed to create Daftra invoice: {str(e)}")