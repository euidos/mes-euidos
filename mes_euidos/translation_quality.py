"""Validate the production Korean catalog before it reaches an ERP site."""

import csv
import re
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

FORMAT_PLACEHOLDER = re.compile(r"(?<!\{)(?<!\\u)\{[^{}\n]*\}(?!\})")
PRINTF_PLACEHOLDER = re.compile(r"%(?:\([^)]+\))?[#0\-+]?\d*(?:\.\d+)?[diouxXeEfFgGcrs]")
JINJA_PLACEHOLDER = re.compile(r"{{.*?}}|{%.*?%}", re.DOTALL)
JAVASCRIPT_PLACEHOLDER = re.compile(r"\$\{[^{}\n]+\}")
MARKUP_TAG = re.compile(r"</?[A-Za-z][^>]*>")
HTML_ENTITY = re.compile(r"&(?!amp;|quot;|apos;)(?:#[0-9]+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]+);")
URL = re.compile(r"https?://[^\s<>\"']+")
ESCAPE_SEQUENCE = re.compile(r"\\(?:u\{[0-9A-Fa-f]+\}|u[0-9A-Fa-f]{4}|x[0-9A-Fa-f]{2}|[trbfv0])")
LOCALIZABLE_ESCAPES = {r"\u2018", r"\u2019"}
PROTECTED_TERMS = (
	"BOM",
	"Frappe",
	"ERPNext",
	"ERP",
	"MES",
	"API",
	"URL",
	"JSON",
	"CSV",
	"PDF",
	"OAuth",
	"LDAP",
)


def _placeholder_tokens(text: str) -> Counter[str]:
	"""Count format fields so translated messages keep every runtime value."""
	return Counter(
		JINJA_PLACEHOLDER.findall(text)
		+ JAVASCRIPT_PLACEHOLDER.findall(text)
		+ FORMAT_PLACEHOLDER.findall(text)
		+ PRINTF_PLACEHOLDER.findall(text)
	)


def _markup_tokens(text: str) -> Counter[str]:
	"""Count markup tags so translations keep the Desk message structure."""
	return Counter(MARKUP_TAG.findall(text))


def _html_entity_tokens(text: str) -> Counter[str]:
	"""Count encoded HTML symbols so rendered print text stays byte-safe."""
	return Counter(HTML_ENTITY.findall(text))


def _url_tokens(text: str) -> Counter[str]:
	"""Count normalized URLs so translated help text keeps its destinations."""
	return Counter(match.rstrip(".,);]") for match in URL.findall(text))


def _escape_tokens(text: str) -> Counter[str]:
	"""Count non-newline escapes so JavaScript and template bytes stay stable."""
	return Counter(token for token in ESCAPE_SEQUENCE.findall(text) if token not in LOCALIZABLE_ESCAPES)


def _edge_whitespace(text: str) -> tuple[str, str]:
	"""Capture leading and trailing whitespace used to compose UI fragments."""
	return re.match(r"^\s*", text).group(), re.search(r"\s*$", text).group()


def _runtime_source_key(source: str, context: str) -> str:
	"""Build the exact key Frappe creates after expanding CSV newline escapes."""
	source = source.replace("\\n", "\n")
	return f"{source}:{context}" if context else source


def _runtime_translation(translation: str) -> str:
	"""Normalize a target exactly as Frappe's CSV translation loader does."""
	return translation.replace("\\n", "\n").replace("\ufeff", "").replace("\u200b", "").strip()


def validate_rows(rows: Sequence[Sequence[str]]) -> list[str]:
	"""Check translation rows and return every production-blocking issue."""
	issues: list[str] = []
	seen: dict[tuple[str, str], str] = {}
	runtime_seen: dict[str, str] = {}
	for row_number, row in enumerate(rows, start=1):
		if len(row) not in (2, 3):
			issues.append(f"row {row_number}: expected 2 or 3 columns, got {len(row)}")
			continue
		source = row[0]
		translation = row[1]
		context = row[2] if len(row) == 3 else ""
		if not translation:
			issues.append(f"row {row_number}: empty translation")
			continue
		semantic_key = (source, context)
		exact_duplicate = semantic_key in seen
		if exact_duplicate:
			previous = seen[semantic_key]
			if previous != translation:
				issues.append(f"row {row_number}: inconsistent translation for {source!r} [{context}]")
			else:
				issues.append(f"row {row_number}: duplicate translation key {source!r} [{context}]")
		else:
			seen[semantic_key] = translation
		runtime_key = _runtime_source_key(source, context)
		runtime_target = _runtime_translation(translation)
		if runtime_key in runtime_seen and not exact_duplicate:
			if runtime_seen[runtime_key] != runtime_target:
				issues.append(
					f"row {row_number}: runtime-normalized inconsistent translation "
					f"for {source!r} [{context}]"
				)
		else:
			runtime_seen[runtime_key] = runtime_target
		if _edge_whitespace(source) != _edge_whitespace(translation):
			issues.append(f"row {row_number}: edge whitespace mismatch")
		source_tokens = _placeholder_tokens(source)
		translated_tokens = _placeholder_tokens(translation)
		if source_tokens != translated_tokens:
			missing = source_tokens - translated_tokens
			issues.append(f"row {row_number}: placeholder mismatch ({', '.join(missing.elements())})")
		source_markup = _markup_tokens(source)
		translated_markup = _markup_tokens(translation)
		if source_markup != translated_markup:
			missing = source_markup - translated_markup
			issues.append(f"row {row_number}: markup mismatch ({', '.join(missing.elements())})")
		source_entities = _html_entity_tokens(source)
		translated_entities = _html_entity_tokens(translation)
		if source_entities != translated_entities:
			missing = source_entities - translated_entities
			issues.append(f"row {row_number}: HTML entity mismatch ({', '.join(missing.elements())})")
		source_newlines = source.count("\n")
		translated_newlines = translation.count("\n")
		if source_newlines != translated_newlines:
			issues.append(
				f"row {row_number}: newline mismatch "
				f"(expected {source_newlines}, got {translated_newlines})"
			)
		source_escaped_newlines = source.count("\\n")
		translated_escaped_newlines = translation.count("\\n")
		if source_escaped_newlines != translated_escaped_newlines:
			issues.append(
				f"row {row_number}: escaped newline mismatch "
				f"(expected {source_escaped_newlines}, got {translated_escaped_newlines})"
			)
		source_escapes = _escape_tokens(source)
		translated_escapes = _escape_tokens(translation)
		if source_escapes != translated_escapes:
			missing = source_escapes - translated_escapes
			issues.append(f"row {row_number}: escape mismatch ({', '.join(missing.elements())})")
		source_urls = _url_tokens(source)
		translated_urls = _url_tokens(translation)
		if source_urls != translated_urls:
			missing = source_urls - translated_urls
			issues.append(f"row {row_number}: URL mismatch ({', '.join(missing.elements())})")
		for term in PROTECTED_TERMS:
			source_term = rf"\b{re.escape(term)}s?\b" if term == "BOM" else rf"\b{re.escape(term)}\b"
			if re.search(source_term, source) and term not in translation:
				issues.append(f"row {row_number}: protected term missing ({term})")
	return issues


def validate_catalog(path: Path) -> list[str]:
	"""Read one runtime CSV and return every production-blocking issue."""
	with path.open(encoding="utf-8", newline="") as catalog_file:
		return validate_rows(list(csv.reader(catalog_file)))


def main(argv: Sequence[str] | None = None) -> int:
	"""Validate a catalog path and return a shell-friendly quality result."""
	args = list(argv if argv is not None else sys.argv[1:])
	if len(args) != 1:
		print("usage: translation_quality.py CATALOG.csv")
		return 2
	issues = validate_catalog(Path(args[0]))
	for issue in issues:
		print(issue)
	return 1 if issues else 0


if __name__ == "__main__":
	raise SystemExit(main())
