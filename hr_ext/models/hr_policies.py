# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrPolicies(models.Model):
    _name = 'hr.policies'
    _description = 'hr policies and grading'

    name = fields.Char("Tittle")

    max_salary = fields.Float("Max salary")
    min_salary = fields.Float("Min salary")

    sick_leave = fields.Char()
    marriage_leave = fields.Float('Marriage')
    paternity_leave = fields.Float('Paternity (Male)')
    death_leave = fields.Float()
    paid_maternity_leave = fields.Float('Paid Maternity (Female)')
    unpaid_maternity_leave = fields.Float('Un Paid Maternity (Female)')
    muslim_widow = fields.Float('Muslim Widow')
    non_muslim_widow = fields.Float('Non-Muslim Widow')
    exams = fields.Char('Examination')
    hajj = fields.Float('Hajj')
    annual = fields.Float('Annual')

    insurance_class = fields.Selection([('vip', 'VIP'), ('a', 'A'), ('b', 'B'), ('c', 'C')])

    air_ticket = fields.Selection([('1', 'Once in a year'), ('2', 'Once in 2 Years')], string='Air Ticket for Expats')
    class_air_ticket = fields.Selection([('business', 'Business'), ('economy', 'Economy')],
                                        string='Class of Travel for Expats')

    re_entry_for_annual_vacation = fields.Selection([('multiple', 'Multiple ERE'), ('single', 'Single ERE')],
                                                    string='Exit Re-entry for Annual Vacation')
    notice_period = fields.Selection([('2', '2 Months'), ('3', '3 Months')], string='Notice Period for all')
    schooling_assistance = fields.Selection([('40000', 'SAR.40,000/- per kid per year upto 2 kids'),('30000', 'SAR.30,000/- per kid per year upto 2 kids'),('20000', 'SAR.20,000/- per kid per year upto 2 kids'), ('not', 'Not Applicable')], string='Schooling Assistance')
