import re
from typing import Optional, Dict, Any

ARTIFACT_SYSTEM_INSTRUCTION = """
When the user asks for a reusable document, complete guide, code tool, or interactive calculator, you can create a standalone ARTIFACT.
To create an artifact, wrap the content in XML tags:

<artifact type="html" title="Interactive PLG Calculator">
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: system-ui, sans-serif; padding: 20px; background: #09090b; color: #f4f4f5; }
    .card { background: #18181b; border: 1px solid #27272a; padding: 20px; border-radius: 10px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Interactive Tool</h2>
    <!-- Interactive inputs & JS here -->
  </div>
</body>
</html>
</artifact>

Or for structured documents:
<artifact type="markdown" title="Strategic Growth Memo">
# Title
...
</artifact>
"""

class ArtifactExtractor:
    """Extracts and parses <artifact> tags from streamed or completed LLM text."""

    def __init__(self):
        self.artifact_regex = re.compile(
            r'<artifact\s+(?:type=["\'](?P<type>html|markdown)["\'])?\s*(?:title=["\'](?P<title>[^"\']+)["\'])?\s*>(?P<content>[\s\S]*?)(?:</artifact>|$)',
            re.IGNORECASE
        )

    def extract_artifact(self, text: str) -> Optional[Dict[str, Any]]:
        match = self.artifact_regex.search(text)
        if not match:
            return None

        artifact_type = match.group("type") or "markdown"
        title = match.group("title") or "Generated Artifact"
        content = match.group("content").strip()

        if not content:
            return None

        return {
            "title": title,
            "artifact_type": artifact_type.lower(),
            "content": content
        }

    def clean_text_without_artifact(self, text: str) -> str:
        """Strips the raw artifact tag so only surrounding conversational text appears in chat."""
        cleaned = self.artifact_regex.sub(
            r'\n\n*[Generated Artifact: "\g<title>" is displayed in the side panel]*\n\n',
            text
        )
        return cleaned.strip()

artifact_extractor = ArtifactExtractor()
