# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Education(models.Model):
    _name = 'hr.education'
    _description = "Education"

    education_type = fields.Many2one('hr.education.type', string="Education Type", required=1)
    name = fields.Char(string='Type', related="education_type.type")
    institute_name = fields.Char("Institute Name ", required=1)
    # relation = fields.Char("Relation")
    education_emp = fields.Many2one('hr.employee', string="Education Ref")
    upload_file = fields.Binary(string="Upload File")
    file_name = fields.Char(string="File Name")


class EducationType(models.Model):
    _name = 'hr.education.type'
    _description = "Education Type"
    _rec_name = "type"

    type = fields.Char("Type", required=1)
