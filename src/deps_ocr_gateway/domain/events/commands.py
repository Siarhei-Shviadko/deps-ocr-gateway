from dataclasses import dataclass
from typing import Any, Optional

from deps_message_flow.commands.common import Command


@dataclass
class OCRImage(Command):
    document_id: int
    source_id: str
    file_path: str
    extraction_params: dict[str, Any]
    identify_document: bool
    extract_data: bool
    document_type: Optional[str] = None
