# -*- coding: utf-8 -*-
import base64
import tempfile
import binascii
import xlrd
from xlrd import open_workbook
from odoo import models, fields, api, _
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, format_date
from odoo.exceptions import Warning, UserError
import threading


class HrEmployeeImport(models.TransientModel):
	_name = 'hr.employee.import'
	_description = 'All About Hr Employee Import'
	
	file = fields.Binary(string="Select Excel File", required=True)

	def get_country(self,country_name):
		if country_name:
			country = self.env['res.country'].search([('name','=',country_name)],limit=1)
			return country.id if country else False
		else:
			return False

	def get_category(self,cat_name):
		if cat_name:
			category = self.env['employee.category'].search([('name','=',cat_name)],limit=1)
			if not category:
				category = self.env['employee.category'].create({'name':cat_name})
				return category.id
			else:
				return category.id

	def get_job(self,job_name):
		if job_name:
			job = self.env['hr.job'].search([('name','=',job_name)],limit=1)
			return job.id if job else False
		else:
			return False

	def get_comp(self,company_name):
		if company_name:
			job = self.env['res.company'].search([('name','=',company_name)],limit=1)
			return job.id if job else False
		else:
			return False

	def get_dep(self,dep_name):
		if dep_name:
			dep = self.env['hr.department'].search([('name','=',dep_name)],limit=1)
			return dep.id if dep else False
		else:
			return False
	
	# def get_integer(self,args):
	#     if args:
	#         try:
	#             return int(args)
	#         except Exception as e :
	#             return False
	#     else:
	#         return False
	
	# def get_option(self,args):
	#     if args == 'Yes':
	#         return 'y'
	#     elif args == 'No':
	#         return 'n'
	#     else:
	#         return False
		
	# def get_job_iqama(self,args):
	#     if args:
	#         job_iqama = self.env['job.iqama'].search([('name','=',args)],limit=1)
	#         if not job_iqama:
	#             job_iqama = self.env['job.iqama'].create({'name':args})
	#             return job_iqama.id
	#         else:
	#             return job_iqama.id
	
	# def get_english_option(self,English_Speaking_Skills):
	#     if English_Speaking_Skills == 'Intermediate':
	#         return 'intermediate'
	#     elif English_Speaking_Skills == 'Excellent':
	#         return 'excellent'
	#     else:
	#         return False
		
	# def _get_id(self,name,type):
	#     if name:
	#         object = False
	#         if type=='JOB':
	#             object = 'hr.job'
	#         elif type=='DEP':
	#             object = 'hr.department'
	#         elif type=='WT':
	#             object = 'employee.shift'
	#         elif type == 'F-REL':
	#             object = 'family.relationship'
	#         elif type == 'EDU':
	#             object = 'education.degree'
	#         elif type == 'COU':
	#             object = 'course.course'
	#         object_id = self.env[object].search([('name','=',name)],limit=1)
	#         if not object_id:
	#             new = self.env[object].create({'name':name})
	#             return new.id
	#         else:
	#             return object_id.id
	#     else:
	#         return False

	def imoport_file(self):
		if self.file:
			try:
				book = open_workbook(file_contents=base64.decodestring(self.file))
				sheet = book.sheet_by_index(0)
				sheet.row_slice
				sheet_index = (len(sheet.row(0)))
				skip_rows = 2
				TotalCol = len(sheet.col(0))
				rows = 0
				EmployeeObj = self.env['hr.employee']
				CategoryObj = self.env['employee.category']
				
			except Exception as e:
				raise Warning(_(e))
			for i in range(TotalCol):
				if i >= 1:

					if sheet_index == 38:
						company_check = sheet.cell_value(rows,37)
						if company_check == "ReadyMix":
							code = sheet.cell_value(rows,0)
							employee_name = sheet.cell_value(rows,2)
							Job_Position = sheet.cell_value(rows,3)
							prof_office_work = sheet.cell_value(rows,4)
							Nationality = sheet.cell_value(rows,5)
							joning_date = sheet.cell_value(rows,6)
							Date_of_Birth = sheet.cell_value(rows,7)
							kingdom_entry_date = sheet.cell_value(rows,8)
							iqama_no = sheet.cell_value(rows,9)
							issue_date_iqama = sheet.cell_value(rows,10)
							expiry_date_iqama = sheet.cell_value(rows,11)
							expiry_date_iqama_hijri = sheet.cell_value(rows,12)
							passport_no = sheet.cell_value(rows,13)
							expiry_date_passport = sheet.cell_value(rows,14)
							insur_sub_no = sheet.cell_value(rows,15)
							worker_no = sheet.cell_value(rows,16)
							# establish_no = sheet.cell_value(rows,17)
							border_no = sheet.cell_value(rows,18)
							# employer_no = sheet.cell_value(rows,19)
							sponser_name = sheet.cell_value(rows,20)
							status = sheet.cell_value(rows,21)
							employee_category = sheet.cell_value(rows,22)
							payment_type = sheet.cell_value(rows,35)
							account_no = sheet.cell_value(rows,36)
							company_id = sheet.cell_value(rows,37)


							join_date = False
							if joning_date:
								if isinstance(joning_date, float):
									join_date = xlrd.xldate.xldate_as_datetime(joning_date, book.datemode)
									if join_date:
										join_date = join_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
								elif isinstance(join_date, str):
									join_date = join_date


							if code:
								employee_id = EmployeeObj.search([('pin','=',int(code))],limit=1)

								vals = {


									'pin': int(code) or False,
									'name': employee_name or False,
									'job_id': self.get_job(Job_Position),
									'prof_office_work': prof_office_work or False,
									'prof_office_work': prof_office_work or False,
									'country_id': self.get_country(Nationality),
									'join_date': join_date or False,
									'birthday': Date_of_Birth or False,
									'kingdom_entry_date': kingdom_entry_date or False,
									'iqama_no': iqama_no or False,
									'issue_date_iqama': issue_date_iqama or False,
									'expiry_date_iqama': expiry_date_iqama or False,
									'expiry_date_iqama_hijri': expiry_date_iqama_hijri or False,
									'passport_id': passport_no or False,
									'expiry_date_passport': expiry_date_passport or False,
									'insur_sub_no': insur_sub_no or False,
									'worker_no': worker_no or False,
									# 'establish_no': establish_no or False,
									'border_no': border_no or False,
									# 'employer_no': employer_no or False,
									'sponser_name': sponser_name or False,
									'status': status or False,
									'employee_category':self.get_category(employee_category),
									'payment_type': payment_type or False,
									'account_no': account_no or False,
									'company_id':self.get_comp(company_id),

									}

					if sheet_index == 16:
						company_check = sheet.cell_value(rows,15)
						if company_check == "Emdad Gulf":
							id_no = sheet.cell_value(rows,0)
							code = sheet.cell_value(rows,1)
							employee_name = sheet.cell_value(rows,2)
							department = sheet.cell_value(rows,3)
							Job_Position = sheet.cell_value(rows,4)
							Nationality = sheet.cell_value(rows,5)
							gender = sheet.cell_value(rows,6)
							profession = sheet.cell_value(rows,7)
							passport_no = sheet.cell_value(rows,8)
							expiry_date_passport = sheet.cell_value(rows,9)
							issue_date_iqama = sheet.cell_value(rows,10)
							expiry_date_iqama = sheet.cell_value(rows,11)
							Date_of_Birth = sheet.cell_value(rows,12)
							kingdom_status = sheet.cell_value(rows,13)
							expiry_date_iqama_hijri = sheet.cell_value(rows,14)
							company_id = sheet.cell_value(rows,15)

							if gender:
								gender = gender.lower()

							if code:
								employee_id = EmployeeObj.search([('pin','=',int(code))],limit=1)

								vals = {
									'identification_id': int(id_no) or False,
									'pin': int(code) or False,
									'name': employee_name or False,
									'job_id': self.get_job(Job_Position),
									'profession': profession or False,
									'country_id': self.get_country(Nationality),
									'department_id': self.get_dep(department),
									'birthday': Date_of_Birth or False,
									'kingdom_status': kingdom_status or False,
									'issue_date_iqama': issue_date_iqama or False,
									'expiry_date_iqama': expiry_date_iqama or False,
									'expiry_date_iqama_hijri': expiry_date_iqama_hijri or False,
									'passport_id': passport_no or False,
									'expiry_date_passport': expiry_date_passport or False,
									'gender': gender or False,
									'company_id':self.get_comp(company_id),

									}


					if employee_id:
						employee_id.write(vals)
						# employee_id._onchange_first_name()
						# employee_id.onchange_emergency_contact()
						# employee_id._create_employee_partner()
						# employee_id.scfhs_license_exp = Date_of_Expiration
					else:
						employee_id = EmployeeObj.create(vals)
						# employee_id._onchange_first_name()
						# employee_id.onchange_emergency_contact()
						# employee_id._create_employee_partner()
						# employee_id.scfhs_license_exp = Date_of_Expiration

				rows += 1

			return self.env['bus.bus'].sendone((self._cr.dbname, 'res.partner', self.env.user.partner_id.id),{'type': 'simple_notification', 'title': _('Info'), 'message': 'Data Import Successfully', 'sticky': True})
		else:
			raise UserError(_("File not found"))