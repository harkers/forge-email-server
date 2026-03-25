from dataclasses import dataclass
from typing import Optional

@dataclass
class NewCase:
    request_type: str
    title: str
    description: str
    submitted_by: str
    urgency: str
    business_area: Optional[str] = None
    controller_name: Optional[str] = None
    client_name: Optional[str] = None
    deadline_at: Optional[str] = None
    confidentiality_level: str = "internal"
    contains_phi: bool = False
    contains_special_category: bool = False
    international_transfer: bool = False
