from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime, date

class PortalTPNForm(http.Controller):

    @http.route(['/my/tpn_forms'], type='http', auth="user", website=True)
    def list_tpn_forms(self, **kwargs):
        user = request.env.user
        tpn_forms = request.env['tpn.form'].sudo().search([('portal_user_id', '=', user.id)])
        _logger.info("TPN Forms for user %s: %s", user.id, tpn_forms)
        return request.render('hospital_ext.portal_tpn_form_list', {
            'tpn_forms': tpn_forms,
        })

    @http.route(['/my/tpn_forms/<int:form_id>'], type='http', auth="user", website=True)
    def view_tpn_form(self, form_id, **kwargs):
        """View detailed TPN form for the current user."""
        tpn_form = request.env['tpn.form'].sudo().browse(form_id)
        if not tpn_form.exists() or tpn_form.portal_user_id.id != request.env.user.id:
            return request.redirect('/my')  # Prevent unauthorized access
        messages = tpn_form.message_ids.sudo()
        tracking_values = request.env['mail.tracking.value'].sudo().search([
            ('mail_message_id', 'in', messages.ids)
        ])
        return request.render('hospital_ext.portal_tpn_form_view', {
            'tpn_form': tpn_form,
            'messages': messages,
            'tracking_values': tracking_values,
        })

    @http.route(['/my/tpn_form/<int:form_id>/post_message'], type='http', auth="user", methods=['POST'], website=True)
    def post_message(self, form_id, **post):
        tpn_form = request.env['tpn.form'].sudo().browse(form_id)
        if tpn_form.exists():
            body = post.get('message_body')
            if body:
                tpn_form.message_post(body=body)
        return request.redirect('/my/tpn_form/%s' % form_id)

    @http.route('/portal/add_tpn_form', auth='user', website=True)
    def add_tpn_form(self, **kw):
        # This is the method that will render the form to add a new TPN form
        return request.render('hospital_ext.portal_tpn_add_form', {})

    @http.route('/portal/save_tpn_form', auth='user', methods=['POST'], website=True)
    def save_tpn_form(self, **kw):
        print("====================")
        # Handle form submission and create a new TPN form record
        tpn_form_obj = request.env['tpn.form'].sudo()

        # General Information
        name = kw.get('name')
        hospital_no = kw.get('hospital_no')
        nationality = kw.get('nationality')
        treating_physician = kw.get('treating_physician')
        ward = kw.get('ward')
        age = kw.get('age')
        weight = kw.get('weight')
        height = kw.get('height')
        diagnosis = kw.get('diagnosis')
        tpn_indications = kw.get('tpn_indications')

        # Prescription Details
        # date = fields.date.today()
        tpn_day = kw.get('tpn_day')
        tpn_route = kw.get('tpn_route')

        # Nutritional Fields
        dextrose_mg_kg_min = kw.get('dextrose_mg_kg_min')
        dextrose_gm_day = kw.get('dextrose_gm_day')
        amino_acids_gm_kg_day = kw.get('amino_acids_gm_kg_day')
        amino_acids_gm_day = kw.get('amino_acids_gm_day')
        fat_emulsion_gm_kg_day = kw.get('fat_emulsion_gm_kg_day')
        fat_emulsion_gm_day = kw.get('fat_emulsion_gm_day')
        total_fluid_intake = kw.get('total_fluid_intake')
        total_fluid_intake_ml_hr = kw.get('total_fluid_intake_ml_hr')
        total_fluid_intake_ml_day = kw.get('total_fluid_intake_ml_day')
        total_volume_tpn = kw.get('total_volume_tpn')

        # Additives
        sodium = kw.get('sodium')
        # sodium_range = kw.get('sodium_range')
        sodium_notes = kw.get('sodium_notes')

        potassium = kw.get('potassium')
        # potassium_range = kw.get('potassium_range')
        potassium_notes = kw.get('potassium_notes')

        calcium = kw.get('calcium')
        # calcium_range = kw.get('calcium_range')
        calcium_notes = kw.get('calcium_notes')

        magnesium = kw.get('magnesium')
        # magnesium_range = kw.get('magnesium_range')
        magnesium_notes = kw.get('magnesium_notes')

        phosphate = kw.get('phosphate')
        # phosphate_range = kw.get('phosphate_range')
        phosphate_notes = kw.get('phosphate_notes')

        chloride = kw.get('chloride')
        # chloride_range = kw.get('chloride_range')
        chloride_notes = kw.get('chloride_notes')

        acetate = kw.get('acetate')
        # acetate_range = kw.get('acetate_range')
        acetate_notes = kw.get('acetate_notes')

        fat_soluble_vitamins = kw.get('fat_soluble_vitamins')
        # fat_soluble_vitamins_range = kw.get('fat_soluble_vitamins_range')
        fat_soluble_vitamins_notes = kw.get('fat_soluble_vitamins_notes')

        water_soluble_vitamins = kw.get('water_soluble_vitamins')
        # water_soluble_vitamins_range = kw.get('water_soluble_vitamins_range')
        water_soluble_vitamins_notes = kw.get('water_soluble_vitamins_notes')

        trace_elements = kw.get('trace_elements')
        # trace_elements_range = kw.get('trace_elements_range')
        trace_elements_notes = kw.get('trace_elements_notes')

        heparin = kw.get('heparin')
        # heparin_range = kw.get('heparin_range')
        heparin_notes = kw.get('heparin_notes')

        # Pharmacy Information
        base_solution_dextrose = kw.get('base_solution_dextrose')
        base_solution_amino = kw.get('base_solution_amino')
        base_solution_water = kw.get('base_solution_water')
        additives_sodium_chloride = kw.get('additives_sodium_chloride')
        additives_potassium_chloride = kw.get('additives_potassium_chloride')
        additives_calcium_gluconate = kw.get('additives_calcium_gluconate')
        additives_magnesium_sulfate = kw.get('additives_magnesium_sulfate')
        additives_sodium_phosphate = kw.get('additives_sodium_phosphate')
        additives_vitamins = kw.get('additives_vitamins')
        additives_trace_elements = kw.get('additives_trace_elements')

        # Calculations
        tpn_rate = kw.get('tpn_rate')
        total_tpn_fluid_rate = kw.get('total_tpn_fluid_rate')
        non_protein_calories = kw.get('non_protein_calories')
        nitrogen_ratio = kw.get('nitrogen_ratio')

        # Prescription and Pharmacy Info
        prescriber_name = kw.get('prescriber_name')
        prescriber_id = kw.get('prescriber_id')
        nurse_name = kw.get('nurse_name')
        pharmacy_technician = kw.get('pharmacy_technician')
        notes = kw.get('notes')

        # Create the record
        tpn_form_obj.create({
            'name': name,
            'hospital_no': hospital_no,
            'nationality': nationality,
            'treating_physician': treating_physician,
            'ward': ward,
            'age': age,
            'weight': weight,
            'height': height,
            'diagnosis': diagnosis,
            'tpn_indications': tpn_indications,
            # 'date': date_field,
            'tpn_day': tpn_day,
            'tpn_route': tpn_route,
            'dextrose_mg_kg_min': dextrose_mg_kg_min,
            'dextrose_gm_day': dextrose_gm_day,
            'amino_acids_gm_kg_day': amino_acids_gm_kg_day,
            'amino_acids_gm_day': amino_acids_gm_day,
            'fat_emulsion_gm_kg_day': fat_emulsion_gm_kg_day,
            'fat_emulsion_gm_day': fat_emulsion_gm_day,
            'total_fluid_intake': total_fluid_intake,
            'total_fluid_intake_ml_hr': total_fluid_intake_ml_hr,
            'total_fluid_intake_ml_day': total_fluid_intake_ml_day,
            'total_volume_tpn': total_volume_tpn,
            'sodium': sodium,
            # 'sodium_range': sodium_range,
            'sodium_notes': sodium_notes,
            'potassium': potassium,
            # 'potassium_range': potassium_range,
            'potassium_notes': potassium_notes,
            'calcium': calcium,
            # 'calcium_range': calcium_range,
            'calcium_notes': calcium_notes,
            'magnesium': magnesium,
            # 'magnesium_range': magnesium_range,
            'magnesium_notes': magnesium_notes,
            'phosphate': phosphate,
            # 'phosphate_range': phosphate_range,
            'phosphate_notes': phosphate_notes,
            'chloride': chloride,
            # 'chloride_range': chloride_range,
            'chloride_notes': chloride_notes,
            'acetate': acetate,
            # 'acetate_range': acetate_range,
            'acetate_notes': acetate_notes,
            'fat_soluble_vitamins': fat_soluble_vitamins,
            # 'fat_soluble_vitamins_range': fat_soluble_vitamins_range,
            'fat_soluble_vitamins_notes': fat_soluble_vitamins_notes,
            'water_soluble_vitamins': water_soluble_vitamins,
            # 'water_soluble_vitamins_range': water_soluble_vitamins_range,
            'water_soluble_vitamins_notes': water_soluble_vitamins_notes,
            'trace_elements': trace_elements,
            # 'trace_elements_range': trace_elements_range,
            'trace_elements_notes': trace_elements_notes,
            'heparin': heparin,
            # 'heparin_range': heparin_range,
            'heparin_notes': heparin_notes,
            'base_solution_dextrose': base_solution_dextrose,
            'base_solution_amino': base_solution_amino,
            'base_solution_water': base_solution_water,
            'additives_sodium_chloride': additives_sodium_chloride,
            'additives_potassium_chloride': additives_potassium_chloride,
            'additives_calcium_gluconate': additives_calcium_gluconate,
            'additives_magnesium_sulfate': additives_magnesium_sulfate,
            'additives_sodium_phosphate': additives_sodium_phosphate,
            'additives_vitamins': additives_vitamins,
            'additives_trace_elements': additives_trace_elements,
            'tpn_rate': tpn_rate,
            'total_tpn_fluid_rate': total_tpn_fluid_rate,
            'non_protein_calories': non_protein_calories,
            'nitrogen_ratio': nitrogen_ratio,
            'prescriber_name': prescriber_name,
            'prescriber_id': prescriber_id,
            'nurse_name': nurse_name,
            'pharmacy_technician': pharmacy_technician,
            'notes': notes,
        })
        # Redirect to a success page after saving
        return request.redirect('/my')  # Redirect to the success page or show a confirmation message

    @http.route('/portal/edit_tpn_form/<int:form_id>', type='http', auth='user', website=True)
    def edit_tpn_form(self, form_id, **kwargs):
        """
        Render the edit form for a specific TPN record.
        """
        # Fetch the TPN form record by ID
        tpn_form = request.env['tpn.form'].sudo().browse(form_id)

        # Check if the record exists and is accessible
        if not tpn_form.exists():
            return request.not_found()

        # Render the edit form template with the TPN form data
        if tpn_form.state != 'approve':
            return request.render('hospital_ext.portal_tpn_edit_form', {
                'form_data': tpn_form
            })
        else:
            messages = tpn_form.message_ids.sudo()
            tracking_values = request.env['mail.tracking.value'].sudo().search([
                ('mail_message_id', 'in', messages.ids)
            ])
            return request.render('hospital_ext.portal_tpn_form_view', {
                'tpn_form': tpn_form,
                'messages': messages,
                'tracking_values': tracking_values,
            })



    @http.route('/portal/update_tpn_form', auth='user', methods=['POST'], website=True)
    def update_tpn_form(self, **kw):
        """
        Handle the form submission to update the TPN record.
        """
        print(33333333333333333)
        # Extract the form ID and updated data from the POST request
        form_id = int(kw.get('form_id'))
        name = kw.get('name')
        hospital_no = kw.get('hospital_no')
        ward = kw.get('ward')

        # Fetch the TPN form record by ID
        tpn_form = request.env['tpn.form'].sudo().browse(form_id)

        # Check if the record exists and is accessible
        if not tpn_form.exists():
            return request.not_found()

        # Update the TPN form record
        if kw:
            # Update fields based on the form submission
            tpn_form.write({
                'name': kw.get('name'),
                'hospital_no': kw.get('hospital_no'),
                'nationality': kw.get('nationality'),
                'treating_physician': kw.get('treating_physician'),
                'ward': kw.get('ward'),
                'age': kw.get('age'),
                'weight': kw.get('weight'),
                'height': kw.get('height'),
                'diagnosis': kw.get('diagnosis'),
                'tpn_indications': kw.get('tpn_indications'),
                'tpn_day': kw.get('tpn_day'),
                'tpn_route': kw.get('tpn_route'),
                'dextrose_mg_kg_min': kw.get('dextrose_mg_kg_min'),
                'dextrose_gm_day': kw.get('dextrose_gm_day'),
                'amino_acids_gm_kg_day': kw.get('amino_acids_gm_kg_day'),
                'amino_acids_gm_day': kw.get('amino_acids_gm_day'),
                'fat_emulsion_gm_kg_day': kw.get('fat_emulsion_gm_kg_day'),
                'fat_emulsion_gm_day': kw.get('fat_emulsion_gm_day'),
                'total_fluid_intake': kw.get('total_fluid_intake'),
                'total_fluid_intake_ml_hr': kw.get('total_fluid_intake_ml_hr'),
                'total_fluid_intake_ml_day': kw.get('total_fluid_intake_ml_day'),
                'total_volume_tpn': kw.get('total_volume_tpn'),
                'sodium': kw.get('sodium'),
                # 'sodium_range': kw.get('sodium_range'),
                'sodium_notes': kw.get('sodium_notes'),
                'potassium': kw.get('potassium'),
                # 'potassium_range': kw.get('potassium_range'),
                'potassium_notes': kw.get('potassium_notes'),
                'calcium': kw.get('calcium'),
                # 'calcium_range': kw.get('calcium_range'),
                'calcium_notes': kw.get('calcium_notes'),
                'magnesium': kw.get('magnesium'),
                # 'magnesium_range': kw.get('magnesium_range'),
                'magnesium_notes': kw.get('magnesium_notes'),
                'phosphate': kw.get('phosphate'),
                # 'phosphate_range': kw.get('phosphate_range'),
                'phosphate_notes': kw.get('phosphate_notes'),
                'chloride': kw.get('chloride'),
                # 'chloride_range': kw.get('chloride_range'),
                'chloride_notes': kw.get('chloride_notes'),
                'acetate': kw.get('acetate'),
                # 'acetate_range': kw.get('acetate_range'),
                'acetate_notes': kw.get('acetate_notes'),
                'fat_soluble_vitamins': kw.get('fat_soluble_vitamins'),
                # 'fat_soluble_vitamins_range': kw.get('fat_soluble_vitamins_range'),
                'fat_soluble_vitamins_notes': kw.get('fat_soluble_vitamins_notes'),
                'water_soluble_vitamins': kw.get('water_soluble_vitamins'),
                # 'water_soluble_vitamins_range': kw.get('water_soluble_vitamins_range'),
                'water_soluble_vitamins_notes': kw.get('water_soluble_vitamins_notes'),
                'trace_elements': kw.get('trace_elements'),
                # 'trace_elements_range': kw.get('trace_elements_range'),
                'trace_elements_notes': kw.get('trace_elements_notes'),
                'heparin': kw.get('heparin'),
                # 'heparin_range': kw.get('heparin_range'),
                'heparin_notes': kw.get('heparin_notes'),
                'base_solution_dextrose': kw.get('base_solution_dextrose'),
                'base_solution_amino': kw.get('base_solution_amino'),
                'base_solution_water': kw.get('base_solution_water'),
                'additives_sodium_chloride': kw.get('additives_sodium_chloride'),
                'additives_potassium_chloride': kw.get('additives_potassium_chloride'),
                'additives_calcium_gluconate': kw.get('additives_calcium_gluconate'),
                'additives_magnesium_sulfate': kw.get('additives_magnesium_sulfate'),
                'additives_sodium_phosphate': kw.get('additives_sodium_phosphate'),
                'additives_vitamins': kw.get('additives_vitamins'),
                'additives_trace_elements': kw.get('additives_trace_elements'),
                'tpn_rate': kw.get('tpn_rate'),
                'total_tpn_fluid_rate': kw.get('total_tpn_fluid_rate'),
                'non_protein_calories': kw.get('non_protein_calories'),
                'nitrogen_ratio': kw.get('nitrogen_ratio'),
                'prescriber_name': kw.get('prescriber_name'),
                'prescriber_id': kw.get('prescriber_id'),
                'nurse_name': kw.get('nurse_name'),
                'pharmacy_technician': kw.get('pharmacy_technician'),
                'notes': kw.get('notes'),
            })

        # Redirect back to the TPN form list
        return request.redirect('/my')