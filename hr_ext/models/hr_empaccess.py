# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class HrEmployeesAccessManagement(models.Model):
    _name = 'hr.emp.access.mgt'
    _description = "Employee Access Management"
    _rec_name = "access_type"

    access_type = fields.Many2one('hr.access.type', string="Access Type")
    approved_by = fields.Many2one('hr.employee', string="Approved by")
    access_emp = fields.Many2one('hr.employee', string="Ref")

class HrAssetType(models.Model):
    _name = 'hr.access.type'
    _description = "Employee Asset Type"

    # hracc = fields.Many2one('hr.emp.access.mgt',string="Access Ref")
    name = fields.Char("Name", required=1)