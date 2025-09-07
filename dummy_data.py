from dataclasses import dataclass
from typing import List

@dataclass
class DummyTicket:
    id: int
    customer_name: str
    customer_id: int
    question: str
    answer: str
    category: str
    status: str   # confirmed, pending, resolved


# 10 dummy tickets for testing
dummy_tickets: List[DummyTicket] = [
    DummyTicket(1, "Ali Khan", 101, "How to reset my password?", "Go to settings > Reset Password.", "account", "resolved"),
    DummyTicket(2, "Sara Ahmed", 102, "What is your refund policy?", "Refunds available within 30 days.", "billing", "confirmed"),
    DummyTicket(3, "Bilal Hussain", 103, "Do you support mobile app?", "Yes, both iOS and Android are available.", "general", "resolved"),
    DummyTicket(4, "Ayesha Malik", 104, "How can I update my email?", "Go to Profile > Edit Email.", "account", "pending"),
    DummyTicket(5, "Omar Farooq", 105, "Can I change my subscription plan?", "Yes, upgrade/downgrade anytime in settings.", "billing", "confirmed"),
    DummyTicket(6, "Hina Gul", 106, "Where can I download invoices?", "Go to Billing > Download Invoice.", "billing", "resolved"),
    DummyTicket(7, "Zain Ali", 107, "Is there 24/7 support available?", "Yes, we provide round-the-clock support.", "support", "confirmed"),
    DummyTicket(8, "Fatima Noor", 108, "How do I delete my account?", "Submit a request via Privacy Settings.", "account", "pending"),
    DummyTicket(9, "Imran Shah", 109, "Do you offer student discounts?", "Yes, 20% student discount is available.", "billing", "resolved"),
    DummyTicket(10, "Maryam Javed", 110, "Can I recover deleted files?", "Sorry, deleted files cannot be recovered.", "general", "confirmed"),
]

# Helper functions for filtered data
def get_tickets_by_status(status: str) -> List[DummyTicket]:
    """Return tickets filtered by status (confirmed, pending, resolved)."""
    return [t for t in dummy_tickets if t.status.lower() == status.lower()]

def get_tickets_by_customer(customer_name: str) -> List[DummyTicket]:
    """Return tickets for a specific customer by name."""
    return [t for t in dummy_tickets if t.customer_name.lower() == customer_name.lower()]
