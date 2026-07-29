import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

from babel.messages.pofile import read_po

KOREAN_CATALOG = Path(__file__).parents[1] / "translations" / "ko.csv"
KOREAN_CONTEXT_OVERRIDES = Path(__file__).parents[1] / "translations" / "ko.context-overrides.json"
KOREAN_SOURCE = Path(__file__).parents[1] / "translations" / "ko.source.jsonl"
KOREAN_POT = Path(__file__).parents[1] / "locale" / "main.pot"
KOREAN_PO = Path(__file__).parents[1] / "locale" / "ko.po"
KOREAN_ENGLISH_ALLOWLIST = Path(__file__).parents[1] / "translations" / "ko.english-allowlist.json"
QUALITY_VALIDATOR = Path(__file__).parents[1] / "translation_quality.py"


def load_quality_validator():
	"""Load the standalone validator without importing the Frappe application."""
	spec = importlib.util.spec_from_file_location("translation_quality", QUALITY_VALIDATOR)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


def test_korean_runtime_catalog_keeps_bom_as_bom():
	"""Reject the production-breaking mistranslation of BOM as a Korean season."""
	assert KOREAN_CATALOG.is_file(), f"missing runtime catalog: {KOREAN_CATALOG}"

	with KOREAN_CATALOG.open(encoding="utf-8", newline="") as catalog_file:
		translations = {row[0]: row[1] for row in csv.reader(catalog_file) if len(row) >= 2}

	assert translations["BOM"] == "BOM"


def test_korean_source_inventory_is_versioned_with_the_catalog():
	"""Keep the exact source/context inventory available for coverage audits."""
	assert KOREAN_SOURCE.is_file(), f"missing source inventory: {KOREAN_SOURCE}"
	inventory = [json.loads(line) for line in KOREAN_SOURCE.read_text(encoding="utf-8").splitlines()]

	assert len(inventory) == 16_512
	assert len({row["source"] for row in inventory}) == 16_354
	assert all(
		row["apps"] and row["locations"] and row["extraction_methods"] for row in inventory
	)


def test_korean_unchanged_english_allowlist_is_versioned():
	"""Require an explicit human-readable reason for intentional English residue."""
	assert KOREAN_ENGLISH_ALLOWLIST.is_file(), f"missing English allowlist: {KOREAN_ENGLISH_ALLOWLIST}"


def test_korean_context_overrides_are_versioned():
	"""Require an explicit reason for every catalog key outside source extraction."""
	assert (
		KOREAN_CONTEXT_OVERRIDES.is_file()
	), f"missing context override manifest: {KOREAN_CONTEXT_OVERRIDES}"
	overrides = json.loads(KOREAN_CONTEXT_OVERRIDES.read_text(encoding="utf-8"))

	assert len(overrides) == 73
	assert all(item["reason"].strip() for item in overrides)


def test_korean_non_korean_results_are_individually_reviewed():
	"""Catch English-only results hidden among legitimate acronyms and identifiers."""
	with KOREAN_CATALOG.open(encoding="utf-8", newline="") as catalog_file:
		non_korean = {
			(row[0], row[2] if len(row) == 3 else ""): row[1]
			for row in csv.reader(catalog_file)
			if (
				len(row) in (2, 3) and re.search(r"[A-Za-z]{2}", row[0]) and not re.search(r"[가-힣]", row[1])
			)
		}
	allowlist = json.loads(KOREAN_ENGLISH_ALLOWLIST.read_text(encoding="utf-8"))
	allowlisted = {(item["source"], item.get("context", "")): item["translation"] for item in allowlist}

	assert all(item.get("reason", "").strip() for item in allowlist)
	assert non_korean == allowlisted, (
		f"English review manifest differs: "
		f"{len(non_korean.keys() - allowlisted.keys())} unreviewed, "
		f"{len(allowlisted.keys() - non_korean.keys())} stale"
	)


def test_korean_runtime_catalog_covers_every_linguistic_source():
	"""Catch any exact source/context key accidentally omitted from the catalog."""
	inventory = {
		(row["source"], row["context"])
		for row in (json.loads(line) for line in KOREAN_SOURCE.read_text(encoding="utf-8").splitlines())
	}
	with KOREAN_CATALOG.open(encoding="utf-8", newline="") as catalog_file:
		catalog = {
			(row[0], row[2] if len(row) == 3 else ""): row[1]
			for row in csv.reader(catalog_file)
			if len(row) in (2, 3)
		}
	overrides = {
		(item["source"], item["context"]): item["translation"]
		for item in json.loads(KOREAN_CONTEXT_OVERRIDES.read_text(encoding="utf-8"))
	}

	expected = inventory | set(overrides)
	missing = expected - set(catalog)
	unexpected = set(catalog) - expected
	override_mismatches = {key for key, translation in overrides.items() if catalog.get(key) != translation}

	assert not missing, f"{len(missing)} source/context pairs are missing from ko.csv"
	assert not unexpected, f"{len(unexpected)} catalog keys lack source or override provenance"
	assert (
		not override_mismatches
	), f"{len(override_mismatches)} context override translations differ from ko.csv"


def test_korean_runtime_catalog_uses_canonical_erp_terms():
	"""Catch drift from terminology Korean ERP and MES operators expect."""
	with KOREAN_CATALOG.open(encoding="utf-8", newline="") as catalog_file:
		translations = {row[0]: row[1] for row in csv.reader(catalog_file) if len(row) == 2}

	assert {
		source: translations.get(source)
		for source in (
			"Account",
			"Amount",
			"Batch",
			"Batch No",
			"Communication",
			"Cost Center",
			"Employee",
			"Item",
			"Journal Entry",
			"Landed Cost Voucher",
			"Maintenance",
			"Operation",
			"Payment Entry",
			"Pick List",
			"Purchase Invoice",
			"Purchase Order",
			"Purchase Receipt",
			"Quality Inspection",
			"Raw Printing Settings",
			"Receipt",
			"Sales Invoice",
			"Sales Order",
			"Serial and Batch Bundle",
			"Stock Entry",
			"WIP Work Orders",
			"Work Order",
		)
	} == {
		"Account": "계정",
		"Amount": "금액",
		"Batch": "로트",
		"Batch No": "로트번호",
		"Communication": "커뮤니케이션",
		"Cost Center": "원가부문",
		"Employee": "사원",
		"Item": "품목",
		"Journal Entry": "분개전표",
		"Landed Cost Voucher": "매입부대비용전표",
		"Maintenance": "설비보전",
		"Operation": "작업",
		"Payment Entry": "입출금전표",
		"Pick List": "피킹리스트",
		"Purchase Invoice": "매입전표",
		"Purchase Order": "발주서",
		"Purchase Receipt": "입고전표",
		"Quality Inspection": "품질검사",
		"Raw Printing Settings": "Raw 인쇄 설정",
		"Receipt": "입고",
		"Sales Invoice": "매출전표",
		"Sales Order": "수주서",
		"Serial and Batch Bundle": "일련번호·로트 묶음",
		"Stock Entry": "재고수불전표",
		"WIP Work Orders": "진행 중 작업지시서",
		"Work Order": "작업지시서",
	}


def test_korean_runtime_catalog_covers_reported_static_and_existing_gaps():
	"""Keep static Workspace, CRM, and administrator labels in the reviewed overlay."""
	with KOREAN_CATALOG.open(encoding="utf-8", newline="") as catalog_file:
		translations = {
			(row[0], row[2] if len(row) == 3 else ""): row[1]
			for row in csv.reader(catalog_file)
			if len(row) in (2, 3)
		}

	expected = {
		("Appointment", ""): "예약",
		("Total Warehouses", ""): "총 창고 수",
		("Stock Value by Item Group", ""): "품목군별 재고금액",
		("Desktop", ""): "데스크톱",
		("Permission Manager", ""): "권한 관리자",
		("Login Activity", ""): "로그인 활동",
		("System Users", ""): "시스템 사용자",
		("Website Users", ""): "웹사이트 사용자",
		("Failed Login Attempts", ""): "로그인 실패 횟수",
		("Supplier Addresses And Contacts", ""): "공급처 주소 및 담당자",
		("Campaign Naming By", ""): "캠페인명 부여 기준",
		("Enable Opportunity Creation from Contact Us", ""): "문의하기 양식의 영업기회 생성 활성화",
		("Allow Lead Duplication based on Emails", ""): "이메일 기준 잠재고객 중복 허용",
		("Close Replied Opportunity After Days", ""): "답변한 영업기회 종료 대기일수",
		(
			"Auto close Opportunity Replied after the no. of days mentioned above",
			"",
		): "위에서 지정한 일수가 지나면 답변한 영업기회를 자동으로 종료합니다.",
		("Default Quotation Validity Days", ""): "기본 견적서 유효일수",
		(
			"All the Comments and Emails will be copied from one document to another "
			"newly created document(Lead -> Opportunity -> Quotation) throughout the "
			"CRM documents.",
			"",
		): (
			"CRM 문서 전반에서 한 문서의 모든 댓글과 이메일을 새로 생성한 문서"
			"(잠재고객 → 영업기회 → 견적서)로 복사합니다."
		),
		(
			"Update the modified timestamp on new communications received in Lead & "
			"Opportunity.",
			"",
		): "잠재고객 및 영업기회에 새 커뮤니케이션이 수신되면 수정일시를 갱신합니다.",
		("Enable Frappe CRM Data Synchronization", ""): "Frappe CRM 데이터 동기화 활성화",
	}

	assert {key: translations.get(key) for key in expected} == expected


def test_korean_runtime_catalog_uses_gettext_context_for_ui_actions():
	"""Keep identical English actions distinct when their actual UI roles differ."""
	with KOREAN_CATALOG.open(encoding="utf-8", newline="") as catalog_file:
		translations = {
			(row[0], row[2] if len(row) == 3 else ""): row[1]
			for row in csv.reader(catalog_file)
			if len(row) in (2, 3)
		}

	assert {
		key: translations.get(key)
		for key in (
			("Submit", ""),
			("Submit", "Button in web form"),
			("Submit", "Primary action of prompt dialog"),
			("Submit", "Submit password for Email Account"),
			("From", ""),
			("From", "Email Sender"),
			("Discard", "Discard Email"),
			("To", ""),
			("To", "Email Recipients"),
			("Change", ""),
			("Change", "Coins"),
			("Minutes", ""),
			("Minutes", "Duration"),
			("Open", ""),
			("Open", "Access"),
			("Convert to Ledger", ""),
			("Convert to Ledger", "Warehouse"),
			(
				"For the new {0} to take effect, would you like to clear the current {1}?",
				"",
			),
			(
				"For the new {0} to take effect, would you like to clear the current {1}?",
				"due_date",
			),
			("CC", ""),
			("CC", "Email Recipients"),
			("BCC", ""),
			("BCC", "Email Recipients"),
		)
	} == {
		("Submit", ""): "확정",
		("Submit", "Button in web form"): "제출",
		("Submit", "Primary action of prompt dialog"): "확인",
		("Submit", "Submit password for Email Account"): "확인",
		("From", ""): "보낸 사람",
		("From", "Email Sender"): "발신자",
		("Discard", "Discard Email"): "이메일 폐기",
		("To", ""): "받는 사람",
		("To", "Email Recipients"): "수신자",
		("Change", ""): "변경",
		("Change", "Coins"): "거스름돈",
		("Minutes", ""): "회의록",
		("Minutes", "Duration"): "분",
		("Open", ""): "진행 중",
		("Open", "Access"): "열기",
		("Convert to Ledger", ""): "원장으로 전환",
		("Convert to Ledger", "Warehouse"): "원장으로 전환",
		(
			"For the new {0} to take effect, would you like to clear the current {1}?",
			"",
		): "새로운 {0}를 적용하려면 현재 {1}를 지우시겠습니까?",
		(
			"For the new {0} to take effect, would you like to clear the current {1}?",
			"due_date",
		): "새로운 {0}를 적용하려면 현재 {1}를 지우시겠습니까?",
		("CC", ""): "참조",
		("CC", "Email Recipients"): "참조",
		("BCC", ""): "숨은 참조",
		("BCC", "Email Recipients"): "숨은 참조",
	}


def test_korean_csv_and_po_agree_where_catalogs_overlap():
	"""Prevent a compiled MO from overriding reviewed runtime Korean with stale text."""
	with KOREAN_CATALOG.open(encoding="utf-8", newline="") as catalog_file:
		csv_translations = {
			(row[0], row[2] if len(row) == 3 else ""): row[1]
			for row in csv.reader(catalog_file)
			if len(row) in (2, 3)
		}
	with KOREAN_PO.open("rb") as po_file:
		po_catalog = read_po(po_file)

	mismatches = []
	fuzzy = []
	for message in po_catalog:
		key = (message.id, message.context or "")
		if message.id and key in csv_translations and message.string != csv_translations[key]:
			mismatches.append(key)
		if message.id and key in csv_translations and "fuzzy" in message.flags:
			fuzzy.append(key)

	assert not mismatches, f"{len(mismatches)} CSV/PO translations disagree"
	assert not fuzzy, f"{len(fuzzy)} reviewed PO translations remain fuzzy"


def test_korean_po_covers_every_current_mes_source():
	"""Keep the compiled MES catalog synchronized with every current POT message."""
	with KOREAN_POT.open("rb") as pot_file:
		pot_catalog = read_po(pot_file)
	with KOREAN_PO.open("rb") as po_file:
		po_catalog = read_po(po_file)

	pot_keys = {
		(message.id, message.context or "")
		for message in pot_catalog
		if message.id and isinstance(message.id, str)
	}
	po_translations = {
		(message.id, message.context or ""): message.string
		for message in po_catalog
		if message.id and isinstance(message.id, str)
	}
	missing = pot_keys - set(po_translations)
	untranslated = {key for key in pot_keys if not po_translations.get(key)}

	assert not missing, f"{len(missing)} current MES POT messages are absent from ko.po"
	assert not untranslated, f"{len(untranslated)} current MES POT messages are untranslated"


def test_korean_po_covers_literal_newline_extractor_variants():
	"""Keep Bench from reporting JavaScript escaped-newline variants as missing."""
	with KOREAN_PO.open("rb") as po_file:
		po_catalog = read_po(po_file)
	messages = {message.id: message.string for message in po_catalog if message.id}
	expected = {
		(
			"Enter the Operation, the table will fetch the Operation details like Hourly Rate, "
			"Workstation automatically.\\n\\n After that, set the Operation Time in minutes "
			"and the table will calculate the Operation Costs based on the Hourly Rate and "
			"Operation Time."
		): (
			"공정을 입력하면 시간당 단가, 작업장 등의 공정 상세를 자동으로 가져옵니다."
			"\\n\\n 그런 다음 공정시간을 분 단위로 설정하면 시간당 단가와 공정시간을 "
			"기준으로 공정원가를 계산합니다."
		),
		(
			"Select whether to get items from a Sales Order or a Material Request. For now "
			"select <b>Sales Order</b>.\\n A Production Plan can also be created manually "
			"where you can select the Items to manufacture."
		): (
			"수주서 또는 자재요청서 중 품목을 불러올 문서를 선택하세요. 현재는 "
			"<b>수주서</b>를 선택하세요.\\n 생산품목을 직접 선택하여 생산계획을 "
			"수동으로 생성할 수도 있습니다."
		),
		(
			"For comparison, use >5, <10 or =324.\\n"
			"For ranges, use 5:10 (for values between 5 & 10)."
		): (
			"비교에는 >5, <10 또는 =324를 사용해 주세요.\\n"
			"범위에는 5:10(5와 10 사이 값)을 사용해 주세요."
		),
	}

	assert {source: messages.get(source) for source in expected} == expected


def test_translation_quality_validator_is_available():
	"""Fail when catalog quality gates cannot run in CI or before deployment."""
	assert QUALITY_VALIDATOR.is_file(), f"missing quality validator: {QUALITY_VALIDATOR}"


def test_translation_quality_validator_exposes_row_validation():
	"""Fail when CI cannot validate actual source/translation/context rows."""
	validator = load_quality_validator()
	assert hasattr(validator, "validate_rows")


def test_translation_quality_validator_rejects_placeholder_loss():
	"""Catch translations that would crash or misstate formatted ERP messages."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Warehouse {0} has {qty} items", "{0} 창고에 품목이 있습니다"]])

	assert issues == ["row 1: placeholder mismatch ({qty})"]


def test_translation_quality_validator_rejects_same_context_inconsistency():
	"""Catch one ERP concept translated two ways in the same semantic context."""
	validator = load_quality_validator()
	rows = [
		["Stock Entry", "재고 이동", "Stock"],
		["Stock Entry", "재고 전표", "Stock"],
	]

	issues = validator.validate_rows(rows)

	assert issues == ["row 2: inconsistent translation for 'Stock Entry' [Stock]"]


def test_translation_quality_validator_rejects_duplicate_semantic_keys():
	"""Catch duplicate source/context keys that Frappe would silently overwrite."""
	validator = load_quality_validator()
	rows = [
		["Work Order", "작업지시서", "Manufacturing"],
		["Work Order", "작업지시서", "Manufacturing"],
	]

	issues = validator.validate_rows(rows)

	assert issues == ["row 2: duplicate translation key 'Work Order' [Manufacturing]"]


def test_translation_quality_validator_allows_context_specific_meanings():
	"""Preserve different Korean meanings when gettext context is genuinely different."""
	validator = load_quality_validator()
	rows = [
		["Entry", "전표", "Accounting"],
		["Entry", "입력", "Form Action"],
	]

	assert validator.validate_rows(rows) == []


def test_translation_quality_validator_rejects_printf_placeholder_changes():
	"""Catch legacy Frappe messages whose named printf values were renamed."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["%(company)s has %d open entries", "%(회사)s에 미결 전표가 있습니다"]])

	assert issues == ["row 1: placeholder mismatch (%(company)s, %d)"]


def test_translation_quality_validator_allows_literal_percent_prose():
	"""Do not mistake ordinary percentage labels and sentences for printf tokens."""
	validator = load_quality_validator()
	rows = [
		["% Finished Item Quantity", "완제품 수량 %"],
		["Check 0% rate", "세율 0% 확인"],
		["{0}% of invoice value", "청구 금액의 {0}%"],
	]

	assert validator.validate_rows(rows) == []


def test_translation_quality_validator_rejects_jinja_placeholder_loss():
	"""Catch print and notification templates that lose Jinja expressions."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Invoice {{ doc.name }}", "매출전표"]])

	assert issues == ["row 1: placeholder mismatch ({{ doc.name }})"]


def test_translation_quality_validator_rejects_empty_format_placeholder_loss():
	"""Catch positional format calls that use anonymous empty braces."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Account {} is missing", "계정과목이 없습니다"]])

	assert issues == ["row 1: placeholder mismatch ({})"]


def test_translation_quality_validator_rejects_javascript_placeholder_changes():
	"""Catch JavaScript template values whose dollar marker was lost."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Type ${type}", "유형 {type}"]])

	assert issues == ["row 1: placeholder mismatch (${type})"]


def test_translation_quality_validator_rejects_markup_loss():
	"""Catch translated Desk messages that drop structural HTML markup."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Open <b>{0}</b>", "{0} 열기"]])

	assert issues == ["row 1: markup mismatch (<b>, </b>)"]


def test_translation_quality_validator_rejects_html_entity_loss():
	"""Catch print and Desk text that changes encoded spaces or symbols."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Open&nbsp;&#8594;", "열기 →"]])

	assert issues == ["row 1: HTML entity mismatch (&nbsp;, &#8594;)"]


def test_translation_quality_validator_allows_localized_html_ampersand():
	"""Allow a lexical English ampersand to become a natural Korean conjunction."""
	validator = load_quality_validator()

	assert validator.validate_rows([["Sales &amp; Purchase", "판매 및 구매"]]) == []


def test_translation_quality_validator_protects_bom_inside_messages():
	"""Catch BOM mistranslations even when the acronym appears in a longer label."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Default BOM", "기본 봄"]])

	assert issues == ["row 1: protected term missing (BOM)"]


def test_translation_quality_validator_protects_plural_boms():
	"""Catch rewritten BOM acronyms when an English message uses the plural form."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Update all BOMs", "모든 자재명세서 업데이트"]])

	assert issues == ["row 1: protected term missing (BOM)"]


def test_translation_quality_validator_protects_product_and_technical_terms():
	"""Catch altered product names and standard integration acronyms."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Frappe API URL", "프레임워크 연동 주소"]])

	assert issues == [
		"row 1: protected term missing (Frappe)",
		"row 1: protected term missing (API)",
		"row 1: protected term missing (URL)",
	]


def test_translation_quality_validator_rejects_empty_translations():
	"""Catch catalog rows that Frappe would silently treat as untranslated."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["Work Order", ""]])

	assert issues == ["row 1: empty translation"]


def test_translation_quality_validator_rejects_malformed_rows():
	"""Catch CSV rows that Frappe would reject or silently skip at runtime."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["source only"], ["source", "번역", "context", "extra"]])

	assert issues == [
		"row 1: expected 2 or 3 columns, got 1",
		"row 2: expected 2 or 3 columns, got 4",
	]


def test_translation_quality_validator_rejects_newline_loss():
	"""Catch collapsed multi-line instructions whose UI structure would break."""
	validator = load_quality_validator()

	issues = validator.validate_rows([["First line\nSecond line", "첫째 줄 둘째 줄"]])

	assert issues == ["row 1: newline mismatch (expected 1, got 0)"]


def test_translation_quality_validator_rejects_escaped_newline_loss():
	"""Catch literal newline escapes that Frappe expands after loading CSV."""
	validator = load_quality_validator()

	issues = validator.validate_rows([[r"First\nSecond", "첫째 둘째"]])

	assert issues == [r"row 1: escaped newline mismatch (expected 1, got 0)"]


def test_translation_quality_validator_rejects_runtime_newline_collisions():
	"""Catch distinct CSV rows that Frappe normalizes to one conflicting key."""
	validator = load_quality_validator()
	rows = [
		["First\nSecond", "첫째\n둘째"],
		[r"First\nSecond", r"첫 번째\n두 번째"],
	]

	issues = validator.validate_rows(rows)

	assert issues == [r"row 2: runtime-normalized inconsistent translation for 'First\\nSecond' []"]


def test_translation_quality_validator_rejects_edge_whitespace_loss():
	"""Catch spaces and indentation that position fragments inside composed UI text."""
	validator = load_quality_validator()

	issues = validator.validate_rows([[" Amount ", "금액"]])

	assert issues == ["row 1: edge whitespace mismatch"]


def test_translation_quality_validator_rejects_unicode_escape_changes():
	"""Catch JavaScript Unicode escapes altered into different runtime bytes."""
	validator = load_quality_validator()

	issues = validator.validate_rows([[r"Updated \u{1F389}", "업데이트됨 🎉"]])

	assert issues == [r"row 1: escape mismatch (\u{1F389})"]


def test_translation_quality_validator_allows_localized_unicode_apostrophe():
	"""Allow an escaped English apostrophe to disappear in natural Korean grammar."""
	validator = load_quality_validator()

	assert validator.validate_rows([[r"You haven\u2019t saved", "아직 저장하지 않았습니다"]]) == []


def test_translation_quality_validator_rejects_url_changes():
	"""Catch help links silently redirected or removed during translation."""
	validator = load_quality_validator()

	issues = validator.validate_rows(
		[["Read https://docs.frappe.io/erpnext for details", "자세한 내용은 문서를 확인해 주세요"]]
	)

	assert issues == ["row 1: URL mismatch (https://docs.frappe.io/erpnext)"]


def test_translation_quality_cli_blocks_invalid_catalog(tmp_path):
	"""Fail the build when any real catalog row violates a quality gate."""
	bad_catalog = tmp_path / "ko.csv"
	bad_catalog.write_text("Default BOM,기본 봄\n", encoding="utf-8")

	result = subprocess.run(
		[sys.executable, str(QUALITY_VALIDATOR), str(bad_catalog)],
		capture_output=True,
		check=False,
		text=True,
	)

	assert result.returncode == 1
	assert "row 1: protected term missing (BOM)" in result.stdout


def test_translation_quality_cli_reports_all_issues(tmp_path):
	"""Show every bad row in one run so a catalog review can fix a complete batch."""
	bad_catalog = tmp_path / "ko.csv"
	bad_catalog.write_text(
		"Default BOM,기본 봄\nWarehouse {0},창고\n",
		encoding="utf-8",
	)

	result = subprocess.run(
		[sys.executable, str(QUALITY_VALIDATOR), str(bad_catalog)],
		capture_output=True,
		check=False,
		text=True,
	)

	assert result.returncode == 1
	assert result.stdout.splitlines() == [
		"row 1: protected term missing (BOM)",
		"row 2: placeholder mismatch ({0})",
	]
