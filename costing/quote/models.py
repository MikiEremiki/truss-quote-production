"""
Commercial Proposal (Quote), Versioning, and Approval Models.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ApprovalStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT_TO_CLIENT = "sent_to_client"
    ACCEPTED = "accepted"


@dataclass
class QuoteItem:
    item_no: int
    name: str
    description: str
    quantity: int
    unit: str
    unit_price: float
    total_price: float
    category: str = "structure"  # 'structure', 'service', 'extra', 'discount', 'vat'


@dataclass
class QuoteVersion:
    version_id: int
    created_at: str
    created_by: str
    status: ApprovalStatus
    comment: str
    items: List[QuoteItem] = field(default_factory=list)
    total_net: float = 0.0
    discount_amount: float = 0.0
    vat_amount: float = 0.0
    final_total: float = 0.0
    profit_net: float = 0.0
    profit_margin_pct: float = 0.0


@dataclass
class CommercialQuote:
    quote_id: str
    project_name: str
    client_name: str
    date_str: str
    current_version: int
    versions: List[QuoteVersion] = field(default_factory=list)
    manager_name: str = "ДревКаркас Инжиниринг"
