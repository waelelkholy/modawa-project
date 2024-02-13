# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError


class ForwardNextMonth(models.TransientModel):
    _name = "forward.next.month"
    _description = "Forward Next Month"
    
    no_month = fields.Integer(string="No Of Months", default=1)
    
    def action_confirm(self):
        """
        it'll move forward entries with given month.
        """
        active_id = self._context.get('active_id',False)
        if active_id:
            loan_id = self.env['hr.loan'].browse(int(active_id))
            LoanLine = self.env['hr.loan.line'].search([('loan_id','=',loan_id.id),('status','=','pending')], order = 'date asc',limit=1) #order = 'date desc'
            date_start = datetime.now().date()
            LoanDate = datetime.strptime(str(LoanLine[0].date), '%Y-%m-%d')
            # for i in range(1, int(self.no_month) + 1):
            for line in LoanLine:
                # if datetime.strptime(str(line.date), '%Y-%m-%d').date().month == date_start.month \
                #     and datetime.strptime(str(line.date), '%Y-%m-%d').date().year == date_start.year:
                line.status = 'hold'
                self.env['hr.loan.line'].create({
                    'date': LoanDate + relativedelta(months=1),
                    'amount': line.amount,
                    'employee_id': loan_id.employee_id.id,
                    'loan_id': loan_id.id,
                    'loan_type_id' : loan_id.loan_type_id.id,
                    'installment_type':loan_id.installment_type,
                    'desciption' : str(line.desciption) + '-' + str(LoanDate + relativedelta(months=1))})
                date_start = date_start + relativedelta(months=1)
                LoanDate = LoanDate + relativedelta(months=1)