# -*- encoding: utf-8 -*-

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    report_days = fields.Integer(string="Generate Report For(Next Days)", help="Number of days product will be expire in stock")
    include_expire_stock = fields.Boolean(string="Include Expire Stock", help="Past and Future product stock expire report form select Include Expire Stock.")
    report_type = fields.Selection([
        ('all', 'All'),
        ('location', 'location'),
        ], string='Report Type', default='all', help="Filter based on location wise and all stock product expiration report")
    location_ids = fields.Many2many("stock.location", string="Filter by Locations", help="Check Product Stock for Expiration from selected Locations only. if its blank it checks in all Locations")
    notification_user_ids = fields.Many2many("res.users", string="Notification to", help="Product stock expiration mail goes to Selected users")

class StockSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    report_days = fields.Integer(related='company_id.report_days', readonly=False)
    include_expire_stock = fields.Boolean(related='company_id.include_expire_stock', readonly=False)
    report_type = fields.Selection(related='company_id.report_type', readonly=False)
    location_ids = fields.Many2many("stock.location", related='company_id.location_ids', readonly=False)
    notification_user_ids = fields.Many2many("res.users", related='company_id.notification_user_ids', readonly=False)
