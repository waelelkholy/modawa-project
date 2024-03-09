# -*- coding: utf-8 -*-
{
	"name": "Founder Stock Card Report",
	'version': '15.0.1',
	'summary': 'Print Card Report in PDF/EXCEl',
	'description':"""
		Odoo application will help to print Stock Card PDF and generate Excel Report.
		
		'======================================================='\n
		'======================================================='
		
		Odoo Version 15.0
	
		'======================================================='
		""",
	"depends": ['stock'],
	'category': 'Warehouse',
	'author': 'Awais ali',
	'website': "https://www.upwork.com/freelancers/~018ff6830780ff04b4",
	'data': [
		'security/ir.model.access.csv',
		'wizard/dev_stock_card_view.xml',
		'report/header.xml',
		'report/stock_card_report.xml',
		'report/report_menu.xml',
		],
	'images': [],
	'installable': True,
	'application': True,
	'license': 'OPL-1',
	"price": 50,
	"currency": 'EUR',
}