import pytest
from app.providers import get_llm_provider
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import ClaudeProvider, OpenAIProvider
from app.skills.ship30_writer import build_ship30_prompt
from app.skills.artifact_generator import artifact_extractor

def test_provider_factory():
    p_ollama = get_llm_provider("ollama")
    assert isinstance(p_ollama, OllamaProvider)

    p_claude = get_llm_provider("claude")
    assert isinstance(p_claude, ClaudeProvider)

    p_openai = get_llm_provider("openai")
    assert isinstance(p_openai, OpenAIProvider)

def test_ship30_prompt_structure():
    user_query = "Write an essay on Shreyas Doshi's LNO framework"
    chunks = [{
        "episode": "Product Leadership",
        "guest": "Shreyas Doshi",
        "timestamp": "00:04:15",
        "text": "LNO framework divides work into Leverage, Neutral, and Overhead."
    }]
    prompt = build_ship30_prompt(user_query, chunks)

    # Validate structural requirements encoded in prompt
    assert "1,250 words" in prompt
    assert "Ship 30 for 30" in prompt
    assert "1-3-1" in prompt
    assert "Shreyas Doshi" in prompt
    assert "The Hook" in prompt
    assert "Bold Visual Anchors" in prompt

def test_artifact_extractor():
    sample_llm_output = """
Here is your interactive ROI calculator based on the discussion:

<artifact type="html" title="PLG ROI Calculator">
<!DOCTYPE html>
<html>
<head><title>ROI</title></head>
<body><h1>Calculator</h1></body>
</html>
</artifact>

I hope this helps your team plan!
"""
    artifact = artifact_extractor.extract_artifact(sample_llm_output)
    assert artifact is not None
    assert artifact["type"] == "html" or artifact["artifact_type"] == "html"
    assert artifact["title"] == "PLG ROI Calculator"
    assert "<h1>Calculator</h1>" in artifact["content"]

    cleaned_text = artifact_extractor.clean_text_without_artifact(sample_llm_output)
    assert "<artifact" not in cleaned_text
    assert "PLG ROI Calculator" in cleaned_text
