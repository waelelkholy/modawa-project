# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class EmergencyContact(models.Model):
    _name = 'hr.emergency.contact'
    _description = "Emergency Contact"

    name = fields.Char("Contact Person Name", required=1)
    contact = fields.Char("Contact Number ")
    relation = fields.Char("Relation")
    emergency_employee = fields.Many2one('hr.employee', string="Emergency Ref")