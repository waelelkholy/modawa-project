# -*- coding: utf-8 -*-

import base64
import tempfile
import binascii
import xlrd
from xlrd import open_workbook
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EmployeeProvisionImport(models.TransientModel):
    _name = "employee.provision.import"
    _description = "Employee Provision File"

    file = fields.Binary(string="Select Excel File")
    
    def _check_gender(self,gender):
        if gender == 'Male':
            return 'male'
        elif gender == 'Female':
            return 'female'
        elif gender == 'Other':
            return 'other'
        else:
            return False
        
    def _check_marital_status(self,marital_status):
        if marital_status == 'Single':
            return 'single'
        elif marital_status == 'Married':
            return 'married'
        elif marital_status == 'Legal Cohabitant':
            return 'cohabitant'
        elif marital_status == 'Widower':
            return 'widower'
        elif marital_status == 'Divorced':
            return 'divorced'
        else :
            return False

    def _select_certificate(self,certificate):
        if isinstance(certificate, str):
            if certificate.find('Bachelor') == 0:
                return 'bachelor'
            elif certificate.find('Master') == 0:
                return 'master'
            elif certificate.find('Doctor') == 0:
                return 'doctor'
            elif certificate == '-':
                return False
            else :
                return 'other'
    
    def imoport_file(self):
        if self.file:
            try:
                book = open_workbook(file_contents=base64.decodestring(self.file))
                sheet = book.sheet_by_index(0)
                wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
                sheet.row_slice
                skip_rows = 2
                TotalCol = len(sheet.col(0))
                rows = 0
                HrEmployeeObj = self.env['hr.employee']
            except Exception as e:
                raise Warning(_(e))
            active_model = self._context.get('active_model')
            lines = []
            unfetched = 0
            for i in range(TotalCol):
                if i >= skip_rows:
                    code = sheet.cell_value(rows,0)
                    name = sheet.cell_value(rows,1)
                    hr_status = sheet.cell_value(rows,2)
                    nationality = sheet.cell_value(rows,3)
                    average_ticket = sheet.cell_value(rows,4)
                    gender = sheet.cell_value(rows,5)
                    maritial_status = sheet.cell_value(rows,6)
                    date_of_join = False
                    if not sheet.cell_value(rows,7) == '-':
                        date_of_join = xlrd.xldate.xldate_as_datetime(sheet.cell_value(rows,7), book.datemode)
                    certificate_level = sheet.cell_value(rows,8)
                    dependends = sheet.cell_value(rows,9)
                    baisc_salary = sheet.cell_value(rows,10)
                    hra = sheet.cell_value(rows,11)
                    transporation = sheet.cell_value(rows,12)
                    employee_id = False
                    country_id = False
                    if code:
                        employee_id = self.env['hr.employee'].search([('emp_id','=',int(code))],limit=1)
                    if nationality:
                        country_id = self.env['res.country'].search([('name','=',nationality)],limit=1)
                    status = False
                    if hr_status == 'Active':
                        status = True
                    if isinstance(average_ticket, float):
                        average_ticket=average_ticket
                    else:
                        average_ticket=0
                    vals = {
                    'name':name,
                    'active':status,
                    'country_id':country_id.id if country_id else False,
                    'average_tickets':float(average_ticket),
                    'gender':self._check_gender(gender),
                    'marital': self._check_marital_status(maritial_status),
                    'hire_date': date_of_join,
                    'certificate':self._select_certificate(certificate_level),
                    'certificate_name':certificate_level,
                    'children':int(dependends),
                    'basic_salary':float(baisc_salary),
                    'hra_monthly':float(hra),
                    'transportation_allowance':float(transporation),
                    }
                    if employee_id:
                        employee_id.write(vals)
                rows+=1
        else:
            raise UserError(_("File not found"))
