from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from deps_message_flow.events.common import DomainEvent


@dataclass
class OCRCompleted(DomainEvent):
    document_id: int
    source_id: str
    file_path: str
    extraction_params: Dict[str, Any]
    ocr_data: List[Dict[str, Any]]
    identify_document: bool
    extract_data: bool
    document_type: Optional[str] = None
