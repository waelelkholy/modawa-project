# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrGrading(models.Model):
    _name = 'hr.grading'
    _description = 'Hr Grading for Hr'

    name = fields.Char('Grade Name')
    level_id = fields.Many2one('hr.policies')
