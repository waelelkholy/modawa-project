# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import itertools
from operator import itemgetter
import operator
from io import BytesIO
import xlwt
from xlwt import easyxf
import base64

class dev_stock_card(models.TransientModel):
	_name ='dev.stock.card'
	_description = 'Stock Card Report'

	location_id = fields.Many2one('stock.location',string='Location', domain="[('usage','=','internal')]", required=True)
	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date')
	filter_by = fields.Selection([('product','Product'),('category','Product Category')],string='Filter By', default='product')
	category_id = fields.Many2one('product.category',string='Category')
	all_products = fields.Boolean('All Products')
	product_ids = fields.Many2many('product.product',string='Products')
	company_id = fields.Many2one('res.company', required=True, default = lambda self:self.env.user.company_id)
	excel_file = fields.Binary('Excel File')

	# get all and specific product on onchange all_products Boolean
	@api.onchange('all_products')
	def onchange_all_product_button(self):
		if self.all_products:
			products = self.env['product.product'].search([])
			self.product_ids = products.ids
		else:
			self.product_ids = False

	# get products ids
	def get_product_ids(self):
		product_pool = self.env['product.product']
		if self.filter_by and self.filter_by == 'product':
			return self.product_ids.ids
		elif self.filter_by and self.filter_by == 'category':
			product_ids = product_pool.search([('type', '=', 'product'), ('categ_id', 'child_of', self.category_id.id)])
			print(3343434434)
			return product_ids.ids
		else:
			product_ids = product_pool.search([('type', '=', 'product')])
			return product_ids.ids


	# get in lines of products
	def in_lines(self,product_ids):
		start_date = str(self.start_date) + ' 00:00:00'
		end_date = str(self.end_date) + ' 23:59:59'

		state = ('draft', 'cancel')
		query = """select DATE(sm.date) as date, sm.price_unit as price, sm.id as id,sm.origin as origin, sm.reference as ref, pt.name as product,\
				  sm.product_uom_qty as in_qty, sm.product_uom as m_uom,pt.uom_po_id as p_uom, pp.id as product_id from stock_move as sm \
				  JOIN product_product as pp ON pp.id = sm.product_id \
				  JOIN product_template as pt ON pp.product_tmpl_id = pt.id \
				  where sm.date >= %s and sm.date <= %s \
				  and sm.location_dest_id = %s and sm.product_id in %s \
				  and sm.state not in %s and sm.company_id = %s
				  """

		params = (start_date, end_date, self.location_id.id, tuple(product_ids), state, self.company_id.id)
		self.env.cr.execute(query, params)
		result = self.env.cr.dictfetchall()
		for res in result:
			product_name_str = str(res.get('product'))
			temp = product_name_str.split(":")[1]
			product_name = temp.replace("}"," ").replace("'", " ")
			res.update({
				'product' : product_name
			})
			f_date = ' '
			if res.get('date'):
				data_date = datetime.strptime(str(res.get('date')),'%Y-%m-%d')
				f_date = data_date.strftime('%d-%m-%Y')
			if res.get('m_uom') and res.get('p_uom') and res.get('in_qty'):
				if res.get('m_uom') != res.get('p_uom'):
					move_uom = self.env['uom.uom'].browse(res.get('m_uom'))
					product_uom = self.env['uom.uom'].browse(res.get('p_uom'))
					qty = move_uom._compute_quantity(res.get('in_qty'), product_uom)
					res.update({
						'uom': product_uom.name,
						'default_code': self.env['product.product'].browse(res.get('product_id')).default_code,
						'in_qty': qty,
						'date': f_date,
						'price': res.get('price'),
						'id': res.get('id')
					})
			res.update({
				'uom': self.env['uom.uom'].browse(res.get('p_uom')).name,
				'default_code': self.env['product.product'].browse(res.get('product_id')).default_code,
				'out_qty': 0.0,
				'date': f_date,
				'price': res.get('price'),
				'id': res.get('id')
			})
		return result

	# get out lines of products
	def out_lines(self, product_ids):
		state = ('draft', 'cancel')
		start_date = str(self.start_date) + ' 00:00:00'
		end_date = str(self.end_date) + ' 23:59:59'
		move_type = 'outgoing'
		m_type = ''
		if self.location_id:
			m_type = 'and sm.location_id = %s'

		query = """select DATE(sm.date) as date, sm.price_unit as price, sm.id as id, sm.origin as origin, sm.reference as ref, pt.name as product,\
					  sm.product_uom_qty as out_qty,sm.product_uom as m_uom,pt.uom_id as p_uom, pp.id as product_id \
					  from stock_move as sm JOIN product_product as pp ON pp.id = sm.product_id \
					  JOIN product_template as pt ON pp.product_tmpl_id = pt.id \
					  where sm.date >= %s and sm.date <= %s \
					  and sm.location_id = %s and sm.product_id in %s \
					  and sm.state not in %s and sm.company_id = %s
					  """

		params = (start_date, end_date, self.location_id.id, tuple(product_ids), state, self.company_id.id)

		self.env.cr.execute(query, params)
		result = self.env.cr.dictfetchall()
		for res in result:
			product_name_str = str(res.get('product'))
			temp = product_name_str.split(":")[1]
			product_name = temp.replace("}", " ").replace("'", " ")
			res.update({
				'product': product_name
			})
			f_date = ' '
			if res.get('date'):
				data_date = datetime.strptime(str(res.get('date')),'%Y-%m-%d')
				f_date = data_date.strftime('%d-%m-%Y')
			if res.get('m_uom') and res.get('p_uom') and res.get('out_qty'):
				if res.get('m_uom') != res.get('p_uom'):
					move_uom = self.env['uom.uom'].browse(res.get('m_uom'))
					product_uom = self.env['uom.uom'].browse(res.get('p_uom'))
					qty = move_uom._compute_quantity(res.get('out_qty'), product_uom)
					res.update({
						'out_uom': self.env['uom.uom'].browse(res.get('p_uom')).name,
						'default_code': self.env['product.product'].browse(res.get('product_id')).default_code,
						'out_qty': qty,
						'date': f_date,
						'price': res.get('price'),
						'id': res.get('id')
					})
			res.update({
				'out_uom': self.env['uom.uom'].browse(res.get('p_uom')).name,
				'default_code': self.env['product.product'].browse(res.get('product_id')).default_code,
				'in_qty': 0.0,
				'date': f_date,
				'price': res.get('price'),
				'id': res.get('id')

			})
		return result

	# get opening qty of product
	def get_opening_quantity(self,product):
		product = self.env['product.product'].browse(product)
		#        date = datetime.strptime(str(self.start_date), '%Y-%m-%d %H:%M:%S')

		date = self.start_date - timedelta(days=1)
		date = self.start_date.strftime('%Y-%m-%d')
		qty = product.with_context(to_date=date, location_id=self.location_id.id).qty_available
		return qty

	# get the product line
	def get_lines(self):
		product_ids = self.get_product_ids()
		print(product_ids,44444)
		result = []
		if product_ids:
			in_lines = self.in_lines(product_ids)
			out_lines = self.out_lines(product_ids)
			lst = in_lines + out_lines
			new_lst = sorted(lst, key=itemgetter('product'))
			groups = itertools.groupby(new_lst, key=operator.itemgetter('product'))
			result = [{'product': k, 'values': [x for x in v]} for k, v in groups]
			for res in result:
				l_data = res.get('values')
				new_lst = sorted(l_data, key=itemgetter('date'))
				res['values'] = new_lst
		return result

	# method for print pdf report
	def print_pdf(self):
		data={}
		data['form'] = self.read()[0]
		return self.env.ref('stock_card_report.print_stock_card_report').report_action(self, data=None)

	# get date
	def get_date(self):
		#        s_date = datetime.strptime(str(self.start_date), '%Y-%m-%d %H:%M:%S').date()
		start_date = self.start_date.strftime('%m-%d-%Y')
		#        e_date = datetime.strptime(str(self.end_date), '%Y-%m-%d %H:%M:%S').date()
		end_date = self.end_date.strftime('%m-%d-%Y')

		data = {'start_date':start_date , 'end_date':end_date}
		return data

	# method for add style in excel report
	def get_style(self):
		main_header_style = easyxf('font:height 300;'
								   'align: horiz center;font: color black; font:bold True;'
								   "borders: top thin,left thin,right thin,bottom thin")

		header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
							  'align: horiz right;font: color black; font:bold True;'
							  "borders: top thin,left thin,right thin,bottom thin")

		left_header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
								   'align: horiz left;font: color black; font:bold True;'
								   "borders: top thin,left thin,right thin,bottom thin")


		text_left = easyxf('font:height 200; align: horiz left;')

		text_right = easyxf('font:height 200; align: horiz right;', num_format_str='0.00')

		text_left_bold = easyxf('font:height 200; align: horiz right;font:bold True;')

		text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;', num_format_str='0.00')
		text_center = easyxf('font:height 200; align: horiz center;'
							 "borders: top thin,left thin,right thin,bottom thin")

		return [main_header_style, left_header_style,header_style, text_left, text_right, text_left_bold, text_right_bold, text_center]

	# method for create excel header
	def create_excel_header(self,worksheet,main_header_style,text_left,text_center,left_header_style,text_right,header_style):
		worksheet.write_merge(0, 1, 1, 3, 'Stock Card', main_header_style)
		row = 2
		col=1
		start_date = datetime.strptime(str(self.start_date), '%Y-%m-%d')
		start_date = datetime.strftime(start_date, "%d-%m-%Y ")

		end_date = datetime.strptime(str(self.end_date), '%Y-%m-%d')
		end_date = datetime.strftime(end_date, "%d-%m-%Y ")

		date = start_date + ' To ' + end_date
		worksheet.write_merge(row, row, col, col+2, date, text_center)

		row += 2
		worksheet.write(row, 0, 'Location', left_header_style)
		worksheet.write_merge(row, row, 1, 2, self.location_id.display_name, text_left)
		row += 1
		worksheet.write(row, 0, 'Company', left_header_style)
		worksheet.write_merge(row, row, 1, 2, self.company_id.name, text_left)
		row += 2

		worksheet.write(row, 0, 'Date', left_header_style)
		# worksheet.write(row,1, 'Old Code', left_header_style)
		worksheet.write(row, 1, 'Internal Reference', left_header_style)
		worksheet.write(row, 2, 'Origin', left_header_style)
		worksheet.write(row, 3, 'Price', left_header_style)
		worksheet.write(row, 4, 'In Qty', header_style)
		worksheet.write(row, 5, 'In Qty UOM', header_style)
		worksheet.write(row, 6, 'Out Qty', header_style)
		worksheet.write(row, 7, 'Out Qty UOM', header_style)
		worksheet.write(row, 8, 'Balance', header_style)
		worksheet.write(row, 9, 'Value', header_style)
		lines = self.get_lines()
		p_group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ivory;'
							   'align: horiz left;font: color black; font:bold True;'
							   "borders: top thin,left thin,right thin,bottom thin")

		group_style = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
							 'align: horiz left;font: color black; font:bold True;'
							 "borders: top thin,left thin,right thin,bottom thin")

		group_style_right = easyxf('font:height 200;pattern: pattern solid, fore_color ice_blue;'
								   'align: horiz right;font: color black; font:bold True;'
								   "borders: top thin,left thin,right thin,bottom thin", num_format_str='0.00')


		row+=1
		print(lines,444)
		for line in lines:
			worksheet.write_merge(row, row, 0, 8, str(line.get('product')), p_group_style)
			row += 1
			line_data = line.get('values')
			product_codes = list(set([d['default_code'] for d in line_data]))
			for code in product_codes:
				count = 0
				balance = 0
				t_in_qty = t_out_qty = 0
				line_list = []
				for line in line_data:
					if code == line.get('default_code'):
						line_list.append(line)
				for val in line_list:
					count += 1
					if count == 1:
						worksheet.write_merge(row, row, 0, 7, 'Opening Quantity', group_style)
						op_qty = self.get_opening_quantity(val.get('product_id'))
						balance = op_qty
						# worksheet.write(row,3, '', group_style_right)
						worksheet.write(row, 8, op_qty, group_style_right)
						worksheet.write(row, 9, '', group_style_right)
						row += 1
					balance += val.get('in_qty') - val.get('out_qty')
					t_in_qty += val.get('in_qty')
					t_out_qty += val.get('out_qty')
					worksheet.write(row, 0, val.get('date'), text_left)
					product = self.env['product.product'].browse(val.get('product_id'))
					# worksheet.write(row, 1, product.old_code, group_style_right)
					worksheet.write(row, 1, product.default_code, group_style_right)
					worksheet.write(row, 2, val.get('origin') or val.get('ref'), text_left)
					if val.get('id'):
						price = 0
						sm = self.env['stock.move'].browse(val.get('id'))
						if sm and sm.account_move_ids:
							for i in sm.account_move_ids[0].line_ids:
								price = price + i.debit
								if val.get('in_qty'):
									price = price / val.get('in_qty')
								if val.get('out_qty'):
									price = price / val.get('out_qty')
						worksheet.write(row, 3, price, text_right)
					worksheet.write(row, 4, val.get('in_qty'), text_right)
					worksheet.write(row, 5, val.get('uom'), text_right)
					worksheet.write(row, 6, val.get('out_qty'), text_right)
					worksheet.write(row, 7, val.get('out_uom'), text_right)
					worksheet.write(row, 8, balance, text_right)
					worksheet.write(row, 9, balance * price, text_right)
					row += 1
				worksheet.write_merge(row, row, 0, 3, 'Total', group_style_right)
				worksheet.write(row, 4, t_in_qty, group_style_right)
				worksheet.write(row, 5, '', group_style_right)
				worksheet.write(row, 6, t_out_qty, group_style_right)
				worksheet.write(row, 7, '', group_style_right)
				worksheet.write(row, 8, balance, group_style_right)
				worksheet.write(row, 9, '', group_style_right)
				row += 1
		row += 1
		return worksheet, row

	# method for excel report
	def action_generate_excel(self):
		excel_style = self.get_style()
		main_header_style = excel_style[0]
		left_header_style = excel_style[1]
		header_style = excel_style[2]
		text_left = excel_style[3]
		text_right = excel_style[4]
		text_left_bold = excel_style[5]
		text_right_bold = excel_style[6]
		text_center = excel_style[7]

		workbook = xlwt.Workbook()
		filename = 'Stock Card Report.xls'
		worksheet = workbook.add_sheet('Stock Card', cell_overwrite_ok=True)
		for i in range(0,10):
			worksheet.col(i).width = 150 * 30

		worksheet,row = self.create_excel_header(worksheet,main_header_style,text_left,text_center,left_header_style,text_right,header_style)

		fp = BytesIO()
		workbook.save(fp)
		fp.seek(0)
		excel_file = base64.b64encode(fp.read())
		fp.close()
		self.write({'excel_file': excel_file})

		if self.excel_file:
			active_id = self.ids[0]
			return {
				'type': 'ir.actions.act_url',
				'url': 'web/content/?model=dev.stock.card&download=true&field=excel_file&id=%s&filename=%s' % (
					active_id, filename),
				'target': 'new',
			}