# -*- coding: utf-8 -*-

from odoo import _, api, fields, models,tools
from odoo.exceptions import UserError, ValidationError
from datetime import  datetime,date,time
from dateutil.relativedelta import relativedelta
import datetime
import calendar
from pytz import timezone

class HrPayslip(models.Model):
    # Private attributes
    _inherit = 'hr.payslip'
    
    # Business methods
    # Get End Date
    def _get_end_date(self,start_date):
        """return the end date of provision"""
        return self.date_to
        # if isinstance(start_date,date):
        #     month = self.date_from.strftime("%m")
        #     year = self.date_from.strftime("%Y")
        #     last_day = calendar.monthrange(int(year),int(month))[1]
        #     return datetime.datetime(int(year),int(month),last_day).date()
        # else:
        #     return False
    
    def _type_eos(self,employee_id,config_id,start_date,end_date,amount):
        """return calculation for es provision"""
        vals = {'data':[]}
        hire_date = employee_id.hire_date
        LessCond = config_id.eos_config_line.filtered(lambda l: l.sign == 'l')
        GreatCond = config_id.eos_config_line.filtered(lambda l: l.sign == 'g')
        less_year = hire_date + relativedelta(years=LessCond.year)
        if start_date < less_year and end_date >= less_year:
            f_cond_amount = (amount / (2 if LessCond.salary == 'half' else 1))
            s_cond_amount = (amount / (1 if GreatCond.salary == 'full' else 2))
            f_monthly = f_cond_amount / 12
            s_monthly = s_cond_amount / 12
            post_date = start_date
            break_month = less_year.strftime("%m")
            while post_date < end_date:
                if int(post_date.strftime("%m")) == int(break_month):
                    break_date = less_year.strftime("%d")
                    break_year = less_year.strftime("%Y")
                    last_day_of_month = calendar.monthrange(int(break_year),int(break_month))[1]
                    break_daily_amount = (f_monthly / last_day_of_month)
                    new_daily_amount = (s_monthly / last_day_of_month)
                    data_f = {
                        'start_date':post_date,
                        'amount':(break_daily_amount * (int(break_date) - 1)),
                        'end_date':self._get_end_date(post_date)
                    }
                    vals['data'].append(data_f)
                    data_s = {
                        'start_date':less_year,
                        'amount':(new_daily_amount * ((last_day_of_month - int(break_date)) + 1)),
                        'end_date':self._get_end_date(less_year)
                    }
                    vals['data'].append(data_s)
                elif post_date < less_year:
                    data = {
                        'start_date':post_date,
                        'amount':f_monthly,
                        'end_date':self._get_end_date(post_date)
                    }
                    vals['data'].append(data)
                elif post_date > less_year:
                    data = {
                        'start_date':post_date,
                        'amount':s_monthly,
                        'end_date':self._get_end_date(post_date)
                    }
                    vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date':start_date})
        elif start_date >= less_year:
            monthly_amount = (amount / (1 if GreatCond.salary == 'full' else 2)) / 12
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date':post_date,
                    'amount':monthly_amount,
                    'end_date':self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date':start_date})
        else:
            monthly_amount = (amount / (2 if LessCond.salary == 'half' else 1)) / 12
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date':post_date,
                    'amount':monthly_amount,
                    'end_date':self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date':start_date})
        return vals
    
    # Type Tickets
    def _type_tickets(self,employee_id,config_id,start_date,end_date,amount):
        """return values for ticket provision"""
        vals = {'data':[]}
        if employee_id.hire_date <= start_date:
            monthly_amount = amount / 12
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date':post_date,
                    'amount':monthly_amount,
                    'end_date':self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date':start_date})
        return vals
    
    # Type Vacation
    def _type_vacation(self,employee_id,config_id,start_date,end_date,amount):
        """return vacation values for provision """
        vals = {'data':[]}
        if employee_id.hire_date <= start_date:
            monthly_amount = (amount / 30) * (self.contract_id.level.annual /12)
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date':post_date,
                    'amount':monthly_amount,
                    'end_date':self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date':start_date})
        else:
            working_days = (int(end_date.day) - int(employee_id.hire_date.day)) + 1
            monthly_amount = (amount / 30) * (((self.contract_id.level.annual / 12)/30) * working_days)
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date': post_date,
                    'amount': monthly_amount,
                    'end_date': self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date': end_date})
        return vals
    
    # Car Policy
    def _type_car_policy(self,employee_id,config_id,start_date,end_date,amount):
        """return type car policy values for provision """
        vals = {'data':[]}
        if employee_id.hire_date <= start_date:
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date':post_date,
                    'amount':amount,
                    'end_date':self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date':start_date})
        return  vals
    
    # Create Provision
    def _create_provision(self,datas,employee_id,config_id,name):
        """ create provision"""
        if isinstance(datas,dict):
            provision_id = self.env['account.provision'].search([('employee_id','=',employee_id.id),('provision_type_id','=',config_id.id),('state','=','running')],limit=1)
            lineObj = self.env['account.provision.line']
            analytic_id = self.env['account.analytic.account'].search([('id','=',employee_id.contract_id.analytic_account_id.id)],limit=1)
            if not provision_id:
                provision_id = self.env['account.provision'].create({
                        'name':name,
                        'provision_type_id':config_id.id,
                        'employee_id':employee_id.id,
                        'cost_center':analytic_id.id if analytic_id else False,
                        'post_date':datas['post_date'],
                        'state':'running'
                    })
            provision_id.update({
                'cost_center':employee_id.contract_id.analytic_account_id.id
            })
            for data in datas['data']:
                line_id = lineObj.create({
                        'date':data['start_date'],
                        'value':data['amount'],
                        'end_date':data.get('end_date'),
                        'provision_id':provision_id.id,
                    })
                line_id.create_move()
    
    # Check Allocation type and Create provision
    def _check_allocation_type(self):
        if self.employee_id:
            if not self.employee_id.hire_date:
                raise UserError(_('Please Configure Hire Date in Employee : %s')%(self.employee_id.name))
            #EOS
            eos_config_id = self.env['provision.configuration'].search([('type','=','EOS'),('struct_id','=',self.struct_id.id)],limit=1)
            if eos_config_id and eos_config_id.journal_id and eos_config_id.debit_account_id and eos_config_id.credit_account_id:
                amount = 0.0
                amount = sum([line.total for x in eos_config_id.salary_rule_ids for line in self.line_ids if line.salary_rule_id.id == x.id])
                if amount > 0.0:
                    provision = self._type_eos(self.employee_id,eos_config_id,self.date_from,self.date_to,amount)
                    name = self.employee_id.name + ' - ' + eos_config_id.name  #' ' + self.date_from.strftime("%Y") + ' / ' + self.date_to.strftime("%Y") + 
                    self._create_provision(provision,self.employee_id,eos_config_id,name)
            # Vaction
            vac_config_id = self.env['provision.configuration'].search([('type','=','Vacation'),('struct_id','=',self.struct_id.id)],limit=1)
            if vac_config_id and vac_config_id.journal_id and vac_config_id.debit_account_id and vac_config_id.credit_account_id:
                amount = 0.0
                amount = sum([line.total for x in vac_config_id.salary_rule_ids for line in self.line_ids if line.salary_rule_id.id == x.id])
                if amount > 0.0:
                    provision = self._type_vacation(self.employee_id,vac_config_id,self.date_from,self.date_to,amount)
                    name = self.employee_id.name + ' - ' + vac_config_id.name #' ' + self.date_from.strftime("%Y") + ' / ' + self.date_to.strftime("%Y") +
                    self._create_provision(provision,self.employee_id,vac_config_id,name)
            # Ticket
            # tik_config_id = self.env['provision.configuration'].search([('type','=','Tickets'),('struct_id','=',self.struct_id.id)],limit=1)
            # if tik_config_id and tik_config_id.journal_id and tik_config_id.debit_account_id and tik_config_id.credit_account_id:
            #     amount = 0.0
            #     amount = sum([line.total for x in tik_config_id.salary_rule_ids for line in self.line_ids if line.salary_rule_id.id == x.id])
            #     if amount > 0.0:
            #         provision = self._type_tickets(self.employee_id,tik_config_id,self.date_from,self.date_to,amount)
            #         name = self.employee_id.name + ' - ' + tik_config_id.name #' ' + self.date_from.strftime("%Y") + ' / ' + self.date_to.strftime("%Y") +
            #         self._create_provision(provision,self.employee_id,tik_config_id,name)
            
            # Car Policy
            car_config_id = self.env['provision.configuration'].search([('type','=','Car Policy')],limit=1)
            if car_config_id and car_config_id.journal_id and car_config_id.debit_account_id and car_config_id.credit_account_id:
                amount = 0.0
                if self.employee_id.monthly_charges and self.employee_id.percentages:
                    amount = (self.employee_id.monthly_charges * self.employee_id.percentages) / 100
                if amount > 0.0:
                    provision = self._type_car_policy(self.employee_id,car_config_id,self.date_from,self.date_to,amount)
                    name = self.employee_id.name + ' - ' + car_config_id.name #' ' + self.date_from.strftime("%Y") + ' / ' + self.date_to.strftime("%Y") +
                    self._create_provision(provision,self.employee_id,car_config_id,name)
                    
    #override to check and change stages
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for rec in self:
            rec._check_allocation_type()
        return res