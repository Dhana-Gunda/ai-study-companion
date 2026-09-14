import os
import json
from playwright.sync_api import sync_playwright

def md_to_pdf(playwright, md_path, pdf_path, title):
    print(f"Converting {md_path} -> {pdf_path}")
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Escape backticks and backslashes for JS template literal
    escaped_md = json.dumps(md_text)

    html_template = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    @page {{
      size: A4;
      margin: 18mm 15mm 18mm 15mm;
      @bottom-right {{
        content: counter(page);
      }}
    }}
    body {{
      background: #ffffff !important;
      color: #1f2328 !important;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
    }}
    .markdown-body {{
      background: #ffffff !important;
      font-size: 13px;
      line-height: 1.6;
    }}
    .markdown-body pre {{
      background-color: #f6f8fa !important;
      border: 1px solid #d0d7de !important;
      border-radius: 6px;
      padding: 12px;
    }}
    .markdown-body table {{
      display: table !important;
      width: 100% !important;
      margin-top: 12px;
      margin-bottom: 12px;
      border-collapse: collapse;
    }}
    .markdown-body table th, .markdown-body table td {{
      border: 1px solid #d0d7de !important;
      padding: 6px 10px;
    }}
    .markdown-body table th {{
      background-color: #f6f8fa !important;
    }}
    .header-banner {{
      border-bottom: 2px solid #0969da;
      padding-bottom: 8px;
      margin-bottom: 20px;
    }}
    .header-banner h1 {{
      margin: 0;
      color: #0969da;
      font-size: 24px;
    }}
    .header-banner p {{
      margin: 4px 0 0 0;
      color: #57609a;
      font-size: 12px;
    }}
  </style>
</head>
<body class="markdown-body">
  <div class="header-banner">
    <h1>AI Study Companion</h1>
    <p>Candidate Challenge Documentation • Candidate: Dhana Gunda</p>
  </div>
  <div id="content"></div>
  <script>
    const rawMd = {escaped_md};
    document.getElementById('content').innerHTML = marked.parse(rawMd);
  </script>
</body>
</html>"""

    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_content(html_template, wait_until="networkidle")
    page.wait_for_timeout(1500)  # Wait for marked.js rendering

    page.pdf(
        path=pdf_path,
        format="A4",
        print_background=True,
        margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"}
    )
    browser.close()
    print(f"Successfully generated: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

def generate_all():
    desktop_dir = r"C:\Users\gunda\OneDrive\Desktop"
    project_docs = r"c:\Users\gunda\OneDrive\Desktop\newProject\docs"
    
    docs_to_convert = [
        {
            "src": r"c:\Users\gunda\OneDrive\Desktop\newProject\docs\architecture.md",
            "name": "Architecture_Documentation.pdf",
            "title": "System Architecture Specification"
        },
        {
            "src": r"c:\Users\gunda\OneDrive\Desktop\newProject\docs\ai_usage.md",
            "name": "AI_Tools_and_Usage_Documentation.pdf",
            "title": "AI Tools, Usage & Telemetry Guide"
        },
        {
            "src": r"c:\Users\gunda\OneDrive\Desktop\newProject\agent_transcripts\prompts.md",
            "name": "AI_Prompts_Used_During_Development.pdf",
            "title": "AI Prompts Record"
        }
    ]

    with sync_playwright() as p:
        for doc in docs_to_convert:
            desktop_target = os.path.join(desktop_dir, doc["name"])
            project_target = os.path.join(project_docs, doc["name"])
            
            md_to_pdf(p, doc["src"], desktop_target, doc["title"])
            
            # Copy to project docs folder as well
            import shutil
            shutil.copyfile(desktop_target, project_target)

if __name__ == "__main__":
    generate_all()
