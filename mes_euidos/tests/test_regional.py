import unittest

import frappe

import mes_euidos
from mes_euidos.tests.utils import ERPNextTestSuite


@mes_euidos.allow_regional
def test_method():
	return "original"


class TestInit(ERPNextTestSuite):
	def test_regional_overrides(self):
		frappe.flags.country = "Maldives"
		self.assertEqual(test_method(), "original")
