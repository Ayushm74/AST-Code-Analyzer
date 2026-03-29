# AI Code Analyzer

AI Code Analyzer is a production-ready Python project that parses Python source code with the built-in `ast` module and generates structured summaries for functions, classes, and methods.

## Features

- Parse Python code into AST safely
- Extract:
  - Functions
  - Classes
  - Methods
  - Arguments
  - Docstrings
  - Line numbers
- Generate structured JSON summaries
- Flask web app with:
  - Upload `.py` file
  - Paste code
  - Result tables and raw JSON
- API endpoint: `POST /analyze`
- Optional OpenAI enrichment:
  - Suggested docstrings
  - Plain-English summaries
- Advanced interview features:
  - Multi-file folder analysis
  - Complexity detection (loop count + recursion check)
  - CLI mode (`--file`, `--folder`)
  - Automatic JSON report saving to `output/`
- UI extras:
  - Drag-and-drop upload
  - Loading indicator
  - Copy JSON button

## How It Works (AST)

1. Input code is parsed with `ast.parse`.
2. AST nodes are traversed using `ast.walk`.
3. Metadata is extracted from:
   - `FunctionDef` / `AsyncFunctionDef`
   - `ClassDef` and contained methods
4. `ast.get_docstring` and `lineno` provide docs and positions.
5. Summary object is built and saved as JSON report.

## Project Structure

```text
code-analyzer/
│── app.py
│── analyzer/
│   │── __init__.py
│   │── parser.py
│   │── extractor.py
│   │── summarizer.py
│   │── ai_doc_generator.py
│── utils/
│   │── file_loader.py
│── web/
│   │── routes.py
│   │── templates/
│   │   │── index.html
│   │   │── result.html
│── static/
│   │── style.css
│── output/
│── samples/
│── config.py
│── requirements.txt
│── README.md
```

## Setup

1. Open terminal in `code-analyzer`
2. Create virtual environment (recommended)
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run app:

```bash
python app.py
```

Flask runs at `http://127.0.0.1:5000`.

## Optional OpenAI Setup

Set environment variables:

```bash
set OPENAI_API_KEY=your_api_key
set OPENAI_MODEL=gpt-4o-mini
```

If key is missing, the app still works normally (without AI enrichment).

## Example Usage

### Web

- Visit `http://127.0.0.1:5000`
- Upload a `.py` file or paste code
- Review function/class/method tables and JSON

### API

```bash
curl -X POST http://127.0.0.1:5000/analyze -F "file=@samples/example.py"
```

or

```bash
curl -X POST http://127.0.0.1:5000/analyze -F "code=def hello(name): return name"
```

### CLI

Analyze single file:

```bash
python app.py --file samples/example.py
```

Analyze folder recursively:

```bash
python app.py --folder samples
```

## Error Handling

- Empty input validation
- Invalid Python syntax detection
- File reading and folder scanning errors
- Clean API and UI error messages

## Screenshots

- Home page: *(add screenshot here)*
- Result page: *(add screenshot here)*
- API output: *(add screenshot here)*

