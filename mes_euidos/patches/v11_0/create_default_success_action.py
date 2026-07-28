import frappe

from mes_euidos.setup.install import create_default_success_action


def execute():
	frappe.reload_doc("core", "doctype", "success_action")
	create_default_success_action()
