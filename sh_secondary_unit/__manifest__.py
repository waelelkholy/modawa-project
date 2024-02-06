# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.
{
    "name": "All In One Secondary Unit Of Measure | Sale Order Secondary Unit | Purchase Order Secondary Unit | Invoice Secondary Unit | Inventory Secondary Unit",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
    "license": "OPL-1",
    "summary": "sales secondary uom purchase secondary unit of measure request for quotation multiple uom account double uom warehouse multiple unit Stock secondary unit of measure Odoo",
    "description": """
Do you have more than one unit of measure in product ?
Yes! so, you are at right palce.
We have created beautiful module to manage secondary unit of product in sales,
purchase,inventory operations and accounting.
It will help you to get easily secondary unit value.
so you don't need to waste your time to calculate that value.
you can also show that value in pdf reports
so your customer/vendor also easily understand that.
""",
    "version": "16.0.6",
    "depends": [
        "sale_management",
        "account",
        "purchase",
        "stock",
    ],
    "application": True,
    "data": [
        "security/sh_secondary_unit_group.xml",
        "views/product_template_views.xml",
        "views/product_product_views.xml",
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_move_views.xml",
        "views/account_move_views.xml",
        "views/stock_scrap_views.xml",
        "report/sale_order_templates.xml",
        "report/purchase_order_templates.xml",
        "report/account_move_templates.xml",
        "report/stock_picking_templates.xml",
        "report/stock_picking_deliveryslip_templates.xml",
        "report/invoice_report_view.xml",
    ],
    "auto_install": False,
    "installable": True,
    "price": 25,
    "currency": "EUR",
    "images": ['static/description/background.png', ],
    "live_test_url": "https://www.youtube.com/watch?v=KrX_zvlWRdI&feature=youtu.be",
}
