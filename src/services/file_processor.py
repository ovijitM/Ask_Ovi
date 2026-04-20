import base64
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from langchain_community.document_loaders import TextLoader


class FileProcessor:
    """Standardize user uploads into model-ready content blocks and display metadata."""

    @staticmethod
    def process_upload(uploaded_file) -> Dict[str, Any]:
        if uploaded_file is None:
            return {
                "prompt_suffix": "",
                "agent_content": None,
                "image_b64": None,
            }

        if uploaded_file.type == "text/plain":
            text = FileProcessor._load_text_with_loader(uploaded_file)
            return {
                "prompt_suffix": f"\n\n[File Content]\n{text}",
                "agent_content": None,
                "image_b64": None,
            }

        image_bytes = uploaded_file.getvalue()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime_type = "image/jpeg" if uploaded_file.name.lower().endswith(("jpg", "jpeg")) else "image/png"

        return {
            "prompt_suffix": f"\n\n[User uploaded image: {uploaded_file.name}]",
            "agent_content": {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
            },
            "image_b64": image_b64,
        }

    @staticmethod
    def _load_text_with_loader(uploaded_file) -> str:
        data = uploaded_file.getvalue().decode("utf-8", errors="replace")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        try:
            loader = TextLoader(tmp_path, encoding="utf-8")
            docs = loader.load()
            merged = "\n\n".join(doc.page_content for doc in docs).strip()
            return merged[:12000]
        finally:
            Path(tmp_path).unlink(missing_ok=True)
