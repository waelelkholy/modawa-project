# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from ummalqura.hijri_date import HijriDate
from odoo.exceptions import UserError, ValidationError
from mailmerge import MailMerge
import os
from num2words import num2words
import base64
from odoo.tools import config
from os.path import dirname
from datetime import date

class ReferenceLetterBank(models.Model):
    _name = 'reference.letter.bank'
    _description = 'Reference Letter bank'
    _rec_name = 'ref_no'

    ref_no = fields.Char(string="Internal Reference No.", default='New')
    document_date = fields.Date(string="Document Date")
    date_ar = fields.Char(string="Date in Arabic")
    since_date = fields.Date(string="Since Date")
    bank_name_ar = fields.Char(string="Bank Name in Arabic")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee",required=1)
    basic_salary = fields.Float(string="Basic Salary")
    housing_allowance = fields.Float(string="Housing Allowance")
    trans_allowance = fields.Float(string="Transportation Allowance")
    total_salary = fields.Float(string="Total Salary", compute="_compute_total_salary")
    file_1 = fields.Binary("Download Document One")
    file_2 = fields.Binary("Download Document Two")
    file_name_1 = fields.Char()
    file_name_2 = fields.Char()

    @api.constrains('basic_salary', 'housing_allowance', 'trans_allowance')
    def _check_amount(self):
        if self.basic_salary <= 0 or self.housing_allowance <= 0 or self.trans_allowance <= 0:
            raise ValidationError(_('The Amount neither be Zero nor be negative'))

    # @api.one
    @api.depends('basic_salary', 'housing_allowance', 'trans_allowance')
    def _compute_total_salary(self):
        self.total_salary = self.basic_salary + self.housing_allowance + self.trans_allowance

    @api.model
    def create(self, vals):
        vals['ref_no'] = self.env['ir.sequence'].next_by_code('reference_letter.bank') or _('New')
        result = super(ReferenceLetterBank, self).create(vals)
        return result

    @api.onchange('document_date')
    def date_in_arabic(self):
        if self.document_date:
            self.date_ar = 'هـ' + HijriDate.get_hijri_date(self.document_date)



    def print_document_one(self):
        def is_empty(attr):
            if attr:
                return attr
            else:
                return ' '

        path_working_dir = dirname(os.path.dirname(__file__))
        template = path_working_dir + "/documents/document_1.docx"
        document = MailMerge(template)
        document.merge(t_allowance=str(is_empty(self.trans_allowance)),
                       h_allowance = str(is_empty(self.housing_allowance)),
                       basic_salary = str(is_empty(self.basic_salary)),
                       emp_p = str(is_empty(self.employee_id.passport_id)),
                       date_ar = str(is_empty(self.date_ar)),
                       date_en = str(is_empty(self.since_date)),
                       emp_nationality = str(is_empty(self.employee_id.country_id.name)),
                       bank_name_ar = str(is_empty(self.bank_name_ar)),
                       emp_name = str(is_empty(self.employee_id.name)),
                       date = str(is_empty(self.document_date)),
                       ref_no = str(is_empty(self.ref_no)),
                       emp_iqama_no = str(is_empty(self.employee_id.emp_iqama.iqama_name))
                       )

        doc_path = os.path.join(config['data_dir'], 'document_data_1.docx')

        document.write(doc_path)
        data_file = open(config['data_dir'] + "/document_data_1.docx", "rb")
        out = data_file.read()
        data_file.close()
        name = self.ref_no + "_" + self.employee_id.name +'_' + 'Doc_1.docx'
        self.file_name_1 = name
        self.file_1 = base64.b64encode(out)

    def print_document_two(self):
        def is_empty(attr):
            if attr:
                return attr
            else:
                return ' '

        path_working_dir = dirname(os.path.dirname(__file__))
        template = path_working_dir + "/documents/document_2.docx"
        document = MailMerge(template)
        document.merge(em_name=str(is_empty(self.employee_id.name)),
                       b_name_ar=str(is_empty(self.bank_name_ar)),
                       em_nat=str(is_empty(self.employee_id.country_id.name)),
                       d_ar=str(is_empty(self.date_ar)),
                       em_pro=str(is_empty(self.employee_id.emp_iqama.job_pos)),
                       iqama_n=str(is_empty(self.employee_id.emp_iqama.iqama_name)),
                       d_en=str(is_empty(self.since_date)),
                       emp_sal=str(is_empty(self.total_salary)),
                       r_no=str(is_empty(self.ref_no)),
                       d=str(is_empty(self.document_date)),
                       )

        doc_path = os.path.join(config['data_dir'], 'document_data_2.docx')

        document.write(doc_path)
        data_file = open(config['data_dir'] + "/document_data_2.docx", "rb")
        out = data_file.read()
        data_file.close()
        name = self.ref_no + "_" + self.employee_id.name +'_' + 'Doc_2.docx'
        self.file_name_2 = name
        self.file_2 = base64.b64encode(out)





