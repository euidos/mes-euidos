# Korean ERP/MES translation contract

## Non-negotiable rules

- `BOM` is always `BOM`, never `봄` or `자재 명세서` in a UI label.
- Translate the semantic key, not the isolated English word:
  `source + gettext context + business domain + UI role`.
- The same semantic key always receives the same Korean translation.
- Different semantic keys may translate the same English source differently.
- Labels/buttons use concise noun phrases. Guidance and errors use concise
  polite Korean (`확인해 주세요`, `처리할 수 없습니다`).
- Preserve placeholders, HTML, URLs, code, identifiers, newlines, and number
  formats exactly.
- Preserve product/framework names: `Frappe`, `ERPNext`, `MES`, `ERP`, `API`,
  `URL`, `JSON`, `CSV`, `PDF`, `OAuth`, `LDAP`.
- Never invent Korean phonetic spellings for an acronym when Korean ERP/MES
  operators normally use the acronym.
- Existing PO translations are suggestions only. Correct awkward or
  semantically wrong translations.

## Canonical business terminology

| English concept | Canonical Korean | Context notes |
|---|---|---|
| Item | 품목 | Not `항목` in stock, buying, selling, or manufacturing |
| Item Code | 품목코드 | |
| Item Name | 품목명 | |
| Item Group | 품목군 | |
| Item Variant | 파생 품목 | |
| Product | 제품 | Use `품목` where the source refers to an ERP item master |
| Service | 서비스 | |
| Batch / Lot | 로트 | Keep literal `Batch` only in developer/technical text |
| Batch No | 로트번호 | |
| Serial No | 일련번호 | |
| Serial and Batch Bundle | 일련번호·로트 묶음 | |
| Warehouse | 창고 | |
| Source Warehouse | 출고창고 | |
| Target Warehouse | 입고창고 | |
| Stock | 재고 | |
| Stock Entry | 재고수불전표 | Purpose-specific prose may use 입고·출고·이동 |
| Pick List | 피킹리스트 | Warehouse picking document; never `선택 목록` |
| Landed Cost Voucher | 매입부대비용전표 | |
| Stock Ledger | 재고수불부 | |
| Stock Balance | 재고현황 | |
| Stock Quantity | 재고수량 | |
| Actual Qty | 현재고 | Quantity context |
| Projected Qty | 예상재고 | |
| Reserved Qty | 예약수량 | |
| Available Qty | 가용재고 | |
| Valuation Rate | 평가단가 | |
| Incoming Rate | 입고단가 | |
| Reorder Level | 발주점 | |
| Safety Stock | 안전재고 | |
| Inventory Dimension | 재고 관리항목 | |
| Material Request | 자재요청서 | |
| Material Transfer | 자재이동 | |
| Material Issue | 자재출고 | |
| Material Receipt | 자재입고 | |
| Supplier | 공급처 | Use `거래처` only when customer/supplier are intentionally combined |
| Customer | 고객 | Use `판매처` where the UI is explicitly counterpart-oriented |
| Party | 거래처 | Accounting counterpart |
| Contact | 담당자 | Use `연락처` for contact information, not a person/master |
| Address | 주소 | |
| Quotation | 견적서 | |
| Sales Order | 수주서 | |
| Delivery Note | 출고전표 | Use `납품서` only for a customer-facing document |
| Sales Invoice | 매출전표 | Never equate it automatically with 세금계산서 |
| Purchase Order | 발주서 | |
| Purchase Receipt | 입고전표 | |
| Purchase Invoice | 매입전표 | |
| Receipt | 영수증/입고/반입 | POS·고객 증빙=`영수증`; 구매=`입고전표`; 재고=`입고`; 자산이동=`반입` |
| Vendor Invoice | 공급처 청구서 | Use `매입전표` only when it is the Purchase Invoice DocType |
| Purchase | 구매 | |
| Sales | 판매 | Use `매출` for accounting amount/results |
| Selling | 영업/판매 | Select by module meaning |
| Buying | 구매 | |
| Return | 반품 | `돌아가기` only for navigation |
| Credit Note | 매출취소전표 | Accounting context |
| Debit Note | 매입취소전표 | Accounting context |
| Price List | 가격표 | |
| Rate | 단가 | Use `비율` for ratios, tax rates, exchange rates, or percentages |
| Amount | 금액 | Never `양` |
| Quantity / Qty | 수량 | |
| Discount | 할인 | |
| Margin | 마진 | Use `이익` where the meaning is actual profit |
| Territory | 영업지역 | |
| Sales Person | 영업담당자 | |
| Sales Partner | 영업협력사 | |
| Lead | 잠재고객 | |
| Opportunity | 영업기회 | |
| Campaign | 캠페인 | |
| Appointment | 예약 | CRM/customer scheduling context |
| Account | 계정과목 | Use `계정` for login/user/bank account contexts |
| Chart of Accounts | 계정과목표 | |
| General Ledger | 총계정원장 | |
| Ledger | 원장 | |
| Journal Entry | 분개전표 | |
| Payment Entry | 입출금전표 | Use 수납/지급 when direction is known |
| Voucher | 전표 | |
| Posting Date | 전표일자 | |
| Fiscal Year | 회계연도 | |
| Cost Center | 원가부문 | |
| Accounting Dimension | 회계 관리항목 | |
| Debit | 차변 | |
| Credit | 대변 | |
| Receivable | 미수금 | |
| Payable | 미지급금 | |
| Outstanding Amount | 미결제금액 | |
| Advance Payment | 선급금/선수금 | Select by payment direction |
| Accrued Expense | 미지급비용 | |
| Deferred Revenue | 이연수익 | |
| Deferred Expense | 이연비용 | |
| Exchange Rate | 환율 | |
| Currency | 통화 | |
| Reporting Currency | 보고통화 | |
| Bank Reconciliation | 은행계정조정 | |
| Mode of Payment | 결제수단 | |
| Payment Terms | 결제조건 | |
| Tax | 세금 | Use `세액` when referring to the amount |
| Tax Rate | 세율 | |
| Tax Category | 과세구분 | |
| Withholding Tax | 원천징수세 | |
| Budget | 예산 | |
| Asset | 자산 | |
| Fixed Asset | 고정자산 | |
| Available for Use Date | 사용개시일 | Fixed-asset accounting term |
| Depreciation | 감가상각 | |
| Gross Profit | 매출총이익 | |
| Profit and Loss | 손익 | |
| Balance Sheet | 재무상태표 | |
| Cash Flow | 현금흐름 | |
| BOM | BOM | Protected acronym |
| Bill of Materials | BOM | User-facing manufacturing context |
| Production Plan | 생산계획 | |
| Work Order | 작업지시서 | |
| Job Card | 작업실적 | MES execution/result record |
| Operation | 공정 | Use `작업` only for a generic action |
| Routing | 공정경로 | |
| Workstation | 작업장 | |
| Production Item | 생산품목 | |
| Raw Material | 원재료 | |
| Sub-assembly | 반제품 | |
| Finished Good | 완제품 | |
| Work In Progress / WIP | 재공품 | Preserve WIP in a combined label if operators need it |
| WIP Warehouse | 재공품창고 | |
| Manufacture | 생산 | Use `제조` for industry/category prose |
| Manufacturing | 생산관리 | Use `제조` where it describes the industrial activity |
| Production | 생산 | |
| Process | 공정 | Use `처리` for system processes |
| Yield | 수율 | |
| Capacity | 생산능력 | |
| Downtime | 비가동시간 | |
| Scrap | 스크랩 | Use `불량` only where rejected output is meant |
| Rework | 재작업 | |
| Backflush | 백플러시 | Explain in prose when useful; do not invent a different function |
| Subcontracting | 외주가공 | |
| Subcontractor | 외주처 | |
| Quality Inspection | 품질검사 | |
| Inspection Criteria | 검사기준 | |
| Accepted Qty | 합격수량 | |
| Rejected Qty | 불합격수량 | |
| Non Conformance | 부적합 | |
| Quality Feedback | 품질 피드백 | |
| Maintenance | 설비보전 | Use `유지보수` for software/system maintenance |
| Asset Maintenance | 설비보전 | |
| Preventive Maintenance | 예방보전 | |
| Breakdown | 고장 | |
| Project | 프로젝트 | |
| Task | 작업 | Use `과제` only in project-planning context if natural |
| Timesheet | 작업시간표 | |
| Issue | 문의/이슈 | Customer support=`문의`, software tracker=`이슈` |
| Service Level Agreement / SLA | 서비스 수준 협약(SLA) | Preserve SLA in later short labels |
| Employee | 사원 | |
| Department | 부서 | |
| Designation | 직급/직책 | Select from field semantics |
| Attendance | 근태 | Use `출석` only outside HR |
| Leave | 휴가 | |
| Payroll | 급여 | |
| Salary Slip | 급여명세서 | |
| Expense Claim | 경비청구서 | |

## Canonical Frappe/UI terminology

| English concept | Canonical Korean | Context notes |
|---|---|---|
| DocType | DocType | Framework administrator term |
| Document | 문서 | |
| Document Type | DocType/문서 유형 | Framework metadata=`DocType`; business-document selector=`문서 유형` |
| Child Table | 하위 테이블 | |
| Link Field | 연결 필드 | |
| Custom Field | 사용자 정의 필드 | |
| Naming Series | 번호 부여 규칙 | |
| Print Format | 인쇄 양식 | |
| Raw Printing | Raw 인쇄 | Frappe direct-printer feature; never literal `원시 인쇄` |
| Letter Head | 문서 머리글 | |
| Report | 보고서 | |
| Dashboard | 대시보드 | |
| Workspace | 작업공간 | |
| Web Form | 웹 양식 | |
| Workflow | 워크플로 | |
| Assignment | 담당자 지정 | Use `할당` for generic resource allocation |
| Role | 역할 | |
| Permission | 권한 | |
| User | 사용자 | |
| Administrator | 관리자 | |
| Notification | 알림 | |
| Email Queue | 이메일 대기열 | |
| Communication | 커뮤니케이션 | Frappe email/comment record; prose may say `연락 기록`, never network `통신` |
| From / To | 보낸 사람 / 받는 사람 | Email-recipient context may use `발신자` / `수신자` |
| CC / BCC | 참조 / 숨은 참조 | Use the same Korean in Communication fields and compose UI |
| Worker | 워커 | Background job/process; never employee `근로자` |
| Audit Trail | 변경 이력 | |
| Version | 버전 | |
| Comment | 댓글 | Use `비고` for a notes field |
| Attachment | 첨부파일 | |
| Draft | 작성 중 | |
| Submitted | 확정됨 | |
| Submit | 확정/제출/확인 | ERP document=`확정`; web form=`제출`; generic dialog or password=`확인` |
| Cancel | 취소 | |
| Cancelled | 취소됨 | |
| Discard | 변경사항 버리기/변경 취소/이메일 폐기 | Select by toolbar, web form, or email context |
| Amend | 수정본 생성 | Accounting prose may say 수정전표 생성 |
| Save | 저장 | |
| Delete | 삭제 | |
| Duplicate | 복제 | Use `중복` when describing duplicate data |
| Enable | 활성화 | |
| Disable | 비활성화 | |
| Enabled | 활성 | |
| Disabled | 비활성 | |
| Mandatory | 필수 | |
| Read Only | 읽기 전용 | |
| Default | 기본값 | Adjective labels may use `기본` |
| Status | 상태 | |
| Open | 진행 중 | Use `열기` only as a verb/button |
| Closed | 종료 | |
| Pending | 대기 | |
| Completed | 완료 | |
| Failed | 실패 | |
| Approved | 승인됨 | |
| Rejected | 반려됨 | Quality inspection result may use 불합격 |
| Apply | 적용 | |
| Clear | 지우기 | Use `초기화` when resetting filters/forms |
| Refresh | 새로고침 | |
| Update | 업데이트 | Use `수정` for editing master data |
| Create | 생성 | Use `등록` for entering a business document/master |
| Add | 추가 | |
| Remove | 제거 | |
| View | 보기 | |
| Preview | 미리보기 | |
| Download | 다운로드 | |
| Upload | 업로드 | |
| Import | 가져오기 | Data/technical menus may use `Import` only when already established |
| Export | 내보내기 | |
| Filter | 필터 | |
| Sort | 정렬 | |
| Search | 검색 | |
| Select | 선택 | |
| Unselect | 선택 해제 | |
| Previous | 이전 | |
| Next | 다음 | |
| Back | 뒤로 | |
| Retry | 다시 시도 | |
| Warning | 경고 | |
| Error | 오류 | |
| Success | 완료 | Use `성공` only when it is the actual result state |

## Review questions for every ambiguous string

1. Which DocType/module and field type uses it?
2. Is it a master-data noun, business document, action, status, or sentence?
3. Would a Korean accounting, purchasing, warehouse, or production operator
   understand it without knowing English ERPNext?
4. Does the same semantic key already have a canonical translation?
5. Are all variables and markup preserved exactly?
