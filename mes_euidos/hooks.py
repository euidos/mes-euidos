app_name = "mes_euidos"
app_title = "MES Euidos"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = """ERP made simple"""
app_icon = "fa fa-th"
app_color = "#e74c3c"
app_email = "hello@frappe.io"
app_license = "GNU General Public License (v3)"
source_link = "https://github.com/frappe/erpnext"
app_logo_url = "/assets/mes_euidos/images/mes_euidos-logo.svg"
app_home = "/desk"

add_to_apps_screen = [
	{
		"name": app_name,
		"logo": "/assets/mes_euidos/images/mes_euidos-logo.svg",
		"title": app_title,
		"route": app_home,
		"has_permission": "mes_euidos.check_app_permission",
	}
]

develop_version = "15.x.x-develop"

app_include_js = "mes_euidos.bundle.js"
app_include_css = "mes_euidos.bundle.css"
web_include_css = "mes_euidos-web.bundle.css"
email_css = "email_erpnext.bundle.css"

app_include_icons = [
	"/assets/mes_euidos/icons/pos-icons.svg",
]

web_include_icons = [
	"/assets/mes_euidos/icons/pos-icons.svg",
]

doctype_js = {
	"Address": "public/js/address.js",
	"Communication": "public/js/communication.js",
	"Event": "public/js/event.js",
	"Newsletter": "public/js/newsletter.js",
	"Contact": "public/js/contact.js",
}
doctype_list_js = {
	"Code List": [
		"edi/doctype/code_list/code_list_import.js",
	],
	"Common Code": [
		"edi/doctype/code_list/code_list_import.js",
	],
}

page_js = {"print": "public/js/print.js"}

extend_doctype_class = {"Address": "mes_euidos.accounts.custom.address.ERPNextAddress"}

override_whitelisted_methods = {"frappe.www.contact.send_message": "mes_euidos.templates.utils.send_message"}

welcome_email = "mes_euidos.setup.utils.welcome_email"

# setup wizard
setup_wizard_requires = "assets/mes_euidos/js/setup_wizard.js"
setup_wizard_stages = "mes_euidos.setup.setup_wizard.setup_wizard.get_setup_stages"

# pg-port: MariaDB-compat SQL functions must exist before schema sync /
# fixtures touch the DB, and must survive restores and upgrades
before_install = "mes_euidos.setup.install.before_install"
after_migrate = ["mes_euidos.setup.install.setup_pg_compat"]
after_install = "mes_euidos.setup.install.after_install"

after_app_install = "mes_euidos.setup.install.after_app_install"
after_app_uninstall = "mes_euidos.setup.install.after_app_uninstall"

boot_session = "mes_euidos.startup.boot.boot_session"
notification_config = "mes_euidos.startup.notifications.get_notification_config"
get_help_messages = "mes_euidos.utilities.activation.get_help_messages"
leaderboards = "mes_euidos.startup.leaderboard.get_leaderboards"
filters_config = "mes_euidos.startup.filters.get_filters_config"
additional_print_settings = "mes_euidos.controllers.print_settings.get_print_settings"

on_session_creation = "mes_euidos.portal.utils.create_customer_or_supplier"

treeviews = [
	"Account",
	"Cost Center",
	"Warehouse",
	"Item Group",
	"Customer Group",
	"Supplier Group",
	"Sales Person",
	"Territory",
	"Department",
]

demo_master_doctypes = [
	"item_group",
	"item",
	"customer_group",
	"supplier_group",
	"customer",
	"supplier",
]
demo_transaction_doctypes = [
	"purchase_order",
	"sales_order",
]

jinja = {
	"methods": [
		"mes_euidos.stock.serial_batch_bundle.get_serial_or_batch_nos",
	],
}

# website
webform_list_context = "mes_euidos.controllers.website_list_for_contact.get_webform_list_context"

calendars = ["Task", "Work Order", "Sales Order", "Holiday List", "ToDo"]

website_generators = ["BOM", "Sales Partner"]

website_context = {
	"favicon": "/assets/mes_euidos/images/mes_euidos-favicon.svg",
	"splash_image": "/assets/mes_euidos/images/mes_euidos-logo.svg",
}

# nosemgrep
website_route_rules = [
	{"from_route": "/orders", "to_route": "Sales Order"},
	{
		"from_route": "/orders/<path:name>",
		"to_route": "order",
		"defaults": {"doctype": "Sales Order", "parents": [{"label": "Orders", "route": "orders"}]},
	},
	{"from_route": "/invoices", "to_route": "Sales Invoice"},
	{
		"from_route": "/invoices/<path:name>",
		"to_route": "order",
		"defaults": {
			"doctype": "Sales Invoice",
			"parents": [{"label": "Invoices", "route": "invoices"}],
		},
	},
	{"from_route": "/supplier-quotations", "to_route": "Supplier Quotation"},
	{
		"from_route": "/supplier-quotations/<path:name>",
		"to_route": "order",
		"defaults": {
			"doctype": "Supplier Quotation",
			"parents": [{"label": "Supplier Quotation", "route": "supplier-quotations"}],
		},
	},
	{"from_route": "/purchase-orders", "to_route": "Purchase Order"},
	{
		"from_route": "/purchase-orders/<path:name>",
		"to_route": "order",
		"defaults": {
			"doctype": "Purchase Order",
			"parents": [{"label": "Purchase Order", "route": "purchase-orders"}],
		},
	},
	{
		"from_route": "/purchase-orders/<path:name>",
		"to_route": "order",
		"defaults": {
			"doctype": "Purchase Order",
			"parents": [{"label": "Purchase Order", "route": "purchase-orders"}],
		},
	},
	{"from_route": "/purchase-invoices", "to_route": "Purchase Invoice"},
	{
		"from_route": "/purchase-invoices/<path:name>",
		"to_route": "order",
		"defaults": {
			"doctype": "Purchase Invoice",
			"parents": [{"label": "Purchase Invoice", "route": "purchase-invoices"}],
		},
	},
	{"from_route": "/quotations", "to_route": "Quotation"},
	{
		"from_route": "/quotations/<path:name>",
		"to_route": "order",
		"defaults": {
			"doctype": "Quotation",
			"parents": [{"label": "Quotations", "route": "quotations"}],
		},
	},
	{"from_route": "/shipments", "to_route": "Delivery Note"},
	{
		"from_route": "/shipments/<path:name>",
		"to_route": "order",
		"defaults": {
			"doctype": "Delivery Note",
			"parents": [{"label": "Shipments", "route": "shipments"}],
		},
	},
	{"from_route": "/rfq", "to_route": "Request for Quotation"},
	{
		"from_route": "/rfq/<path:name>",
		"to_route": "rfq",
		"defaults": {
			"doctype": "Request for Quotation",
			"parents": [{"label": "Request for Quotation", "route": "rfq"}],
		},
	},
	{"from_route": "/addresses", "to_route": "Address"},
	{
		"from_route": "/addresses/<path:name>",
		"to_route": "addresses",
		"defaults": {"doctype": "Address", "parents": [{"label": "Addresses", "route": "addresses"}]},
	},
	{"from_route": "/boms", "to_route": "BOM"},
	{"from_route": "/timesheets", "to_route": "Timesheet"},
	{"from_route": "/material-requests", "to_route": "Material Request"},
	{
		"from_route": "/material-requests/<path:name>",
		"to_route": "material_request_info",
		"defaults": {
			"doctype": "Material Request",
			"parents": [{"label": "Material Request", "route": "material-requests"}],
		},
	},
	{"from_route": "/project", "to_route": "Project"},
	{"from_route": "/tasks", "to_route": "Task"},
	{"from_route": "/banking/<path:app_path>", "to_route": "banking"},
]

standard_navbar_items = [
	{
		"item_label": "Delete Demo Data",
		"item_type": "Action",
		"action": "mes_euidos.demo.clear_demo();",
		"is_standard": 1,
		"condition": "eval: frappe.boot.sysdefaults.demo_company && frappe.boot.sysdefaults.demo_company.length > 0",
		"icon": "trash",
	},
]

standard_portal_menu_items = [
	{"title": "Projects", "route": "/project", "reference_doctype": "Project", "role": "Customer"},
	{
		"title": "Request for Quotations",
		"route": "/rfq",
		"reference_doctype": "Request for Quotation",
		"role": "Supplier",
	},
	{
		"title": "Supplier Quotation",
		"route": "/supplier-quotations",
		"reference_doctype": "Supplier Quotation",
		"role": "Supplier",
	},
	{
		"title": "Purchase Orders",
		"route": "/purchase-orders",
		"reference_doctype": "Purchase Order",
		"role": "Supplier",
	},
	{
		"title": "Purchase Invoices",
		"route": "/purchase-invoices",
		"reference_doctype": "Purchase Invoice",
		"role": "Supplier",
	},
	{
		"title": "Quotations",
		"route": "/quotations",
		"reference_doctype": "Quotation",
		"role": "Customer",
	},
	{
		"title": "Orders",
		"route": "/orders",
		"reference_doctype": "Sales Order",
		"role": "Customer",
	},
	{
		"title": "Invoices",
		"route": "/invoices",
		"reference_doctype": "Sales Invoice",
		"role": "Customer",
	},
	{
		"title": "Shipments",
		"route": "/shipments",
		"reference_doctype": "Delivery Note",
		"role": "Customer",
	},
	{"title": "Issues", "route": "/issues", "reference_doctype": "Issue", "role": "Customer"},
	{"title": "Addresses", "route": "/addresses", "reference_doctype": "Address", "role": "Customer"},
	{
		"title": "Timesheets",
		"route": "/timesheets",
		"reference_doctype": "Timesheet",
		"role": "Customer",
	},
	{"title": "Newsletter", "route": "/newsletters", "reference_doctype": "Newsletter"},
	{
		"title": "Material Request",
		"route": "/material-requests",
		"reference_doctype": "Material Request",
		"role": "Customer",
	},
	{"title": "Appointment Booking", "route": "/book_appointment"},
]

sounds = [
	{"name": "incoming-call", "src": "/assets/mes_euidos/sounds/incoming-call.mp3", "volume": 0.2},
	{"name": "call-disconnect", "src": "/assets/mes_euidos/sounds/call-disconnect.mp3", "volume": 0.2},
	{"name": "numpad-touch", "src": "/assets/mes_euidos/sounds/numpad-touch.mp3", "volume": 0.8},
]

has_upload_permission = {"Employee": "mes_euidos.setup.doctype.employee.employee.has_upload_permission"}

has_website_permission = {
	"Sales Order": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
	"Quotation": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
	"Sales Invoice": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
	"Supplier Quotation": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
	"Purchase Order": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
	"Purchase Invoice": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
	"Material Request": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
	"Delivery Note": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
	"Issue": "mes_euidos.support.doctype.issue.issue.has_website_permission",
	"Timesheet": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
	"Project": "mes_euidos.controllers.website_list_for_contact.has_website_permission",
}


period_closing_doctypes = [
	"Sales Invoice",
	"Purchase Invoice",
	"Journal Entry",
	"Bank Clearance",
	"Stock Entry",
	"Dunning",
	"Invoice Discounting",
	"Payment Entry",
	"Period Closing Voucher",
	"Process Deferred Accounting",
	"Asset",
	"Asset Capitalization",
	"Asset Repair",
	"Delivery Note",
	"Landed Cost Voucher",
	"Purchase Receipt",
	"Stock Reconciliation",
	"Subcontracting Receipt",
]

doc_events = {
	"*": {
		"validate": [
			"mes_euidos.support.doctype.service_level_agreement.service_level_agreement.apply",
			"mes_euidos.setup.doctype.transaction_deletion_record.transaction_deletion_record.check_for_running_deletion_job",
		],
	},
	tuple(period_closing_doctypes): {
		"validate": "mes_euidos.accounts.doctype.accounting_period.accounting_period.validate_accounting_period_on_doc_save",
	},
	"Stock Entry": {
		"on_submit": "mes_euidos.stock.doctype.material_request.material_request.update_completed_and_requested_qty",
		"on_cancel": "mes_euidos.stock.doctype.material_request.material_request.update_completed_and_requested_qty",
	},
	"User": {
		"after_insert": "frappe.contacts.doctype.contact.contact.update_contact",
		"validate": "mes_euidos.setup.doctype.employee.employee.validate_employee_role",
		"on_update": "mes_euidos.portal.utils.set_default_role",
	},
	"Communication": {
		"on_update": [
			"mes_euidos.support.doctype.service_level_agreement.service_level_agreement.on_communication_update",
			"mes_euidos.support.doctype.issue.issue.set_first_response_time",
		],
		"after_insert": [
			"mes_euidos.crm.utils.link_communications_with_prospect",
			"mes_euidos.crm.utils.update_modified_timestamp",
		],
	},
	"Event": {
		"after_insert": "mes_euidos.crm.utils.link_events_with_prospect",
	},
	"Contact Us Settings": {
		"on_update": "mes_euidos.crm.utils.disable_opportunity_creation_on_contact_us_disabled",
	},
	"Sales Invoice": {
		"on_submit": [
			"mes_euidos.regional.italy.utils.sales_invoice_on_submit",
		],
		"on_cancel": [
			"mes_euidos.regional.italy.utils.sales_invoice_on_cancel",
		],
		"on_trash": "mes_euidos.regional.check_deletion_permission",
	},
	"Purchase Invoice": {
		"validate": [
			"mes_euidos.regional.united_arab_emirates.utils.update_grand_total_for_rcm",
			"mes_euidos.regional.united_arab_emirates.utils.validate_returns",
		],
	},
	"Payment Entry": {
		"on_trash": "mes_euidos.regional.check_deletion_permission",
	},
	"Address": {
		"validate": [
			"mes_euidos.regional.italy.utils.set_state_code",
		],
	},
	"Contact": {
		"on_trash": "mes_euidos.support.doctype.issue.issue.update_issue",
		"after_insert": "mes_euidos.telephony.doctype.call_log.call_log.link_existing_conversations",
		"validate": ["mes_euidos.crm.utils.update_lead_phone_numbers"],
	},
	"Email Unsubscribe": {
		"after_insert": "mes_euidos.crm.doctype.email_campaign.email_campaign.unsubscribe_recipient"
	},
	"Integration Request": {
		"validate": "mes_euidos.accounts.doctype.payment_request.payment_request.validate_payment"
	},
}

# function should expect the variable and doc as arguments
naming_series_variables_list = ["FY", "TFY", "ABBR", "MM", "DD", "YY", "YYYY", "JJJ", "WW"]
naming_series_variables = {
	variable: "mes_euidos.accounts.utils.parse_naming_series_variable"
	for variable in naming_series_variables_list
}

# On cancel event Payment Entry will be exempted and all linked submittable doctype will get cancelled.
# to maintain data integrity we exempted payment entry. it will un-link when sales invoice get cancelled.
# if payment entry not in auto cancel exempted doctypes it will cancel payment entry.
auto_cancel_exempted_doctypes = [
	"Payment Entry",
]

scheduler_events = {
	"cron": {
		"0/15 * * * *": [
			"mes_euidos.manufacturing.doctype.bom_update_log.bom_update_log.resume_bom_cost_update_jobs",
			"mes_euidos.stock.doctype.repost_item_valuation.repost_item_valuation.run_parallel_reposting",
		],
		# Hourly but offset by 30 minutes
		"30 * * * *": [
			"mes_euidos.accounts.doctype.gl_entry.gl_entry.rename_gle_sle_docs",
		],
		# Daily but offset by 45 minutes
		"45 0 * * *": [],
	},
	"hourly": [
		"mes_euidos.projects.doctype.project.project.hourly_reminder",
	],
	"hourly_long": [],
	"hourly_maintenance": [
		"mes_euidos.crm.doctype.appointment.appointment.handle_expired_unverified_appointments",
		"mes_euidos.stock.doctype.repost_item_valuation.repost_item_valuation.repost_entries",
		"mes_euidos.utilities.bulk_transaction.retry",
		"mes_euidos.projects.doctype.project.project.collect_project_status",
		"mes_euidos.projects.doctype.project.project.project_status_update_reminder",
		"mes_euidos.erpnext_integrations.doctype.plaid_settings.plaid_settings.automatic_synchronization",
		"mes_euidos.utilities.doctype.video.video.update_youtube_data",
		"mes_euidos.accounts.doctype.bank_transaction_rule.bank_transaction_rule.scheduler_run_rule_evaluation",
	],
	"daily": [],
	"daily_long": [],
	"daily_maintenance": [
		"mes_euidos.support.doctype.issue.issue.auto_close_tickets",
		"mes_euidos.crm.doctype.opportunity.opportunity.auto_close_opportunity",
		"mes_euidos.controllers.accounts_controller.update_invoice_status",
		"mes_euidos.accounts.doctype.fiscal_year.fiscal_year.auto_create_fiscal_year",
		"mes_euidos.projects.doctype.task.task.set_tasks_as_overdue",
		"mes_euidos.stock.doctype.serial_no.serial_no.update_maintenance_status",
		"mes_euidos.buying.doctype.supplier_scorecard.supplier_scorecard.refresh_scorecards",
		"mes_euidos.setup.doctype.company.company.cache_companies_monthly_sales_history",
		"mes_euidos.assets.doctype.asset.asset.update_maintenance_status",
		"mes_euidos.assets.doctype.asset.asset.make_post_gl_entry",
		"mes_euidos.crm.doctype.contract.contract.update_status_for_contracts",
		"mes_euidos.projects.doctype.project.project.update_project_sales_billing",
		"mes_euidos.projects.doctype.project.project.send_project_status_email_to_users",
		"mes_euidos.quality_management.doctype.quality_review.quality_review.review",
		"mes_euidos.support.doctype.service_level_agreement.service_level_agreement.check_agreement_status",
		"mes_euidos.crm.doctype.email_campaign.email_campaign.send_email_to_leads_or_contacts",
		"mes_euidos.crm.doctype.email_campaign.email_campaign.set_email_campaign_status",
		"mes_euidos.selling.doctype.quotation.quotation.set_expired_status",
		"mes_euidos.buying.doctype.supplier_quotation.supplier_quotation.set_expired_status",
		"mes_euidos.accounts.doctype.process_statement_of_accounts.process_statement_of_accounts.send_auto_email",
		"mes_euidos.accounts.utils.auto_create_exchange_rate_revaluation_daily",
		"mes_euidos.accounts.utils.run_ledger_health_checks",
		"mes_euidos.assets.doctype.asset_maintenance_log.asset_maintenance_log.update_asset_maintenance_log_status",
		"mes_euidos.stock.reorder_item.reorder_item",
		"mes_euidos.accounts.doctype.process_subscription.process_subscription.create_subscription_process",
		"mes_euidos.setup.doctype.email_digest.email_digest.send",
		"mes_euidos.manufacturing.doctype.bom_update_tool.bom_update_tool.auto_update_latest_price_in_all_boms",
		"mes_euidos.crm.utils.open_leads_opportunities_based_on_todays_event",
		"mes_euidos.assets.doctype.asset.depreciation.post_depreciation_entries",
	],
	"weekly": [
		"mes_euidos.accounts.utils.auto_create_exchange_rate_revaluation_weekly",
		"mes_euidos.stock.doctype.stock_reposting_settings.stock_reposting_settings.repost_incorrect_valuation_entries",
	],
	"monthly_long": [
		"mes_euidos.accounts.deferred_revenue.process_deferred_accounting",
		"mes_euidos.accounts.utils.auto_create_exchange_rate_revaluation_monthly",
	],
}

email_brand_image = "assets/mes_euidos/images/mes_euidos-logo.jpg"

default_mail_footer = """
	<span>
		Sent via
		<a class="text-muted" href="https://frappe.io/mes_euidos?source=via_email_footer" target="_blank">
			ERPNext
		</a>
	</span>
"""

get_translated_dict = {("doctype", "Global Defaults"): "frappe.geo.country_info.get_translated_dict"}

bot_parsers = [
	"mes_euidos.utilities.bot.FindItemBot",
]

get_site_info = "mes_euidos.utilities.get_site_info"

payment_gateway_enabled = "mes_euidos.accounts.utils.create_payment_gateway_account"

communication_doctypes = ["Customer", "Supplier"]

advance_payment_receivable_doctypes = ["Sales Order"]
advance_payment_payable_doctypes = ["Purchase Order"]

invoice_doctypes = ["Sales Invoice", "Purchase Invoice"]

bank_reconciliation_doctypes = [
	"Payment Entry",
	"Journal Entry",
	"Purchase Invoice",
	"Sales Invoice",
]

accounting_dimension_doctypes = [
	"GL Entry",
	"Payment Ledger Entry",
	"Sales Invoice",
	"Purchase Invoice",
	"Payment Entry",
	"Asset",
	"Stock Entry",
	"Budget",
	"Delivery Note",
	"Sales Invoice Item",
	"Purchase Invoice Item",
	"Purchase Order Item",
	"Sales Order Item",
	"Journal Entry Account",
	"Journal Entry Template Account",
	"Material Request Item",
	"Delivery Note Item",
	"Purchase Receipt Item",
	"Stock Entry Detail",
	"Payment Entry Deduction",
	"Sales Taxes and Charges",
	"Purchase Taxes and Charges",
	"Shipping Rule",
	"Landed Cost Item",
	"Asset Value Adjustment",
	"Asset Repair",
	"Asset Capitalization",
	"Loyalty Program",
	"Stock Reconciliation",
	"POS Profile",
	"Opening Invoice Creation Tool",
	"Opening Invoice Creation Tool Item",
	"Subscription",
	"Subscription Plan",
	"POS Invoice",
	"POS Invoice Item",
	"Purchase Order",
	"Purchase Receipt",
	"Sales Order",
	"Subcontracting Order",
	"Subcontracting Order Item",
	"Subcontracting Receipt",
	"Subcontracting Receipt Item",
	"Account Closing Balance",
	"Supplier Quotation",
	"Supplier Quotation Item",
	"Payment Reconciliation",
	"Payment Reconciliation Allocation",
	"Payment Request",
	"Asset Movement Item",
	"Asset Depreciation Schedule",
	"Advance Taxes and Charges",
]

subscription_doctypes = ["Sales Invoice", "Purchase Invoice", "Payment Request", "POS Invoice"]

get_matching_queries = (
	"mes_euidos.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.get_matching_queries"
)

get_amounts_not_reflected_in_system_for_bank_reconciliation_statement = "mes_euidos.accounts.report.bank_reconciliation_statement.bank_reconciliation_statement.get_amounts_not_reflected_in_system_for_bank_reconciliation_statement"

get_payment_entries_for_bank_clearance = (
	"mes_euidos.accounts.doctype.bank_clearance.bank_clearance.get_payment_entries_for_bank_clearance"
)

get_entries_for_bank_clearance_summary = "mes_euidos.accounts.report.bank_clearance_summary.bank_clearance_summary.get_entries_for_bank_clearance_summary"

get_entries_for_bank_reconciliation_statement = "mes_euidos.accounts.report.bank_reconciliation_statement.bank_reconciliation_statement.get_entries_for_bank_reconciliation_statement"

regional_overrides = {
	"France": {"mes_euidos.tests.test_regional.test_method": "mes_euidos.regional.france.utils.test_method"},
	"United Arab Emirates": {
		"mes_euidos.controllers.taxes_and_totals.update_itemised_tax_data": "mes_euidos.regional.united_arab_emirates.utils.update_itemised_tax_data",
		"mes_euidos.accounts.doctype.purchase_invoice.purchase_invoice.make_regional_gl_entries": "mes_euidos.regional.united_arab_emirates.utils.make_regional_gl_entries",
	},
	"Saudi Arabia": {
		"mes_euidos.controllers.taxes_and_totals.update_itemised_tax_data": "mes_euidos.regional.united_arab_emirates.utils.update_itemised_tax_data"
	},
	"Italy": {
		"mes_euidos.controllers.taxes_and_totals.update_itemised_tax_data": "mes_euidos.regional.italy.utils.update_itemised_tax_data",
		"mes_euidos.controllers.accounts_controller.validate_regional": "mes_euidos.regional.italy.utils.sales_invoice_validate",
	},
}
user_privacy_documents = [
	{
		"doctype": "Lead",
		"match_field": "email_id",
		"personal_fields": ["phone", "mobile_no", "fax", "website", "lead_name"],
	},
	{
		"doctype": "Opportunity",
		"match_field": "contact_email",
		"personal_fields": ["contact_mobile", "contact_display", "customer_name"],
	},
]


# ERPNext doctypes for Global Search
global_search_doctypes = {
	"Default": [
		{"doctype": "Customer", "index": 0},
		{"doctype": "Supplier", "index": 1},
		{"doctype": "Item", "index": 2},
		{"doctype": "Warehouse", "index": 3},
		{"doctype": "Account", "index": 4},
		{"doctype": "Employee", "index": 5},
		{"doctype": "BOM", "index": 6},
		{"doctype": "Sales Invoice", "index": 7},
		{"doctype": "Sales Order", "index": 8},
		{"doctype": "Quotation", "index": 9},
		{"doctype": "Work Order", "index": 10},
		{"doctype": "Purchase Order", "index": 11},
		{"doctype": "Purchase Receipt", "index": 12},
		{"doctype": "Purchase Invoice", "index": 13},
		{"doctype": "Delivery Note", "index": 14},
		{"doctype": "Stock Entry", "index": 15},
		{"doctype": "Material Request", "index": 16},
		{"doctype": "Delivery Trip", "index": 17},
		{"doctype": "Pick List", "index": 18},
		{"doctype": "Payment Entry", "index": 22},
		{"doctype": "Lead", "index": 23},
		{"doctype": "Opportunity", "index": 24},
		{"doctype": "Item Price", "index": 25},
		{"doctype": "Purchase Taxes and Charges Template", "index": 26},
		{"doctype": "Sales Taxes and Charges", "index": 27},
		{"doctype": "Asset", "index": 28},
		{"doctype": "Project", "index": 29},
		{"doctype": "Task", "index": 30},
		{"doctype": "Timesheet", "index": 31},
		{"doctype": "Issue", "index": 32},
		{"doctype": "Serial No", "index": 33},
		{"doctype": "Batch", "index": 34},
		{"doctype": "Branch", "index": 35},
		{"doctype": "Department", "index": 36},
		{"doctype": "Designation", "index": 38},
		{"doctype": "Maintenance Schedule", "index": 45},
		{"doctype": "Maintenance Visit", "index": 46},
		{"doctype": "Warranty Claim", "index": 47},
	],
}

ignore_links_on_delete = [
	"Tax Withholding Entry",
]

additional_timeline_content = {"*": ["mes_euidos.telephony.doctype.call_log.call_log.get_linked_call_logs"]}


extend_bootinfo = [
	"mes_euidos.support.doctype.service_level_agreement.service_level_agreement.add_sla_doctypes",
	"mes_euidos.startup.boot.bootinfo",
]


default_log_clearing_doctypes = {
	"Repost Item Valuation": 60,
}

export_python_type_annotations = True

fields_for_group_similar_items = ["qty", "amount"]

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
ignore_translatable_strings_from = ["frappe"]
repost_allowed_doctypes = [
	"Sales Invoice",
	"Purchase Invoice",
	"Journal Entry",
	"Payment Entry",
	"Purchase Receipt",
]
