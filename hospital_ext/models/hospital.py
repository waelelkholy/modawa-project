from odoo import models, fields

class TPNForm(models.Model):
    _name = 'tpn.form'
    _description = 'Total Parenteral Nutrition Neonatal Form'

    portal_user_id = fields.Many2one('res.users', string="Portal User", help="User linked to the portal for this form.",default=lambda self: self.env.user)

    # General Information
    name = fields.Char(string="Patient Name", required=True)
    hospital_no = fields.Char(string="Hospital No.", required=True)
    nationality = fields.Char(string="Nationality")
    treating_physician = fields.Char(string="Treating Physician")
    ward = fields.Char(string="Ward")
    age = fields.Integer(string="Age (days)")
    weight = fields.Float(string="Weight (kg)")
    height = fields.Float(string="Height (cm)")
    diagnosis = fields.Text(string="Diagnosis")
    tpn_indications = fields.Text(string="TPN Indications")

    # Prescription Details
    tpn_day = fields.Integer(string="Day(s) of TPN")
    tpn_route = fields.Selection(
        [('central', 'Central'), ('peripheral', 'Peripheral')], 
        string="TPN Route"
    )

    # Nutritional Fields
    dextrose_mg_kg_min = fields.Float(string="Dextrose (mg/kg/min)")
    dextrose_gm_day = fields.Float(string="Dextrose (gm/day)")
    amino_acids_gm_kg_day = fields.Float(string="Amino Acids (gm/kg/day)")
    fat_emulsion_gm_kg_day = fields.Float(string="Fat Emulsion 20% (gm/kg/day)")
    total_fluid_intake = fields.Float(string="Total Fluid Intake (ml/kg/day)")
    total_volume_tpn = fields.Float(string="Total Volume of TPN (ml/day)")

    # Additives
    sodium = fields.Float(string="Sodium (mmol/day)")
    potassium = fields.Float(string="Potassium (mmol/day)")
    calcium = fields.Float(string="Calcium (mmol/day)")
    magnesium = fields.Float(string="Magnesium (mmol/day)")
    phosphate = fields.Float(string="Phosphate (mmol/day)")
    chloride = fields.Float(string="Chloride (mmol/day)")
    acetate = fields.Float(string="Acetate")
    fat_soluble_vitamins = fields.Float(string="Fat Soluble Vitamins (ml/day)")
    water_soluble_vitamins = fields.Float(string="Water Soluble Vitamins (ml/day)")
    trace_elements = fields.Float(string="Trace Elements (ml/day)")
    heparin = fields.Float(string="Heparin (units/ml)")

    # Pharmacy Information
    base_solution_dextrose = fields.Float(string="Base Solution - Dextrose (ml)")
    base_solution_amino = fields.Float(string="Base Solution - Amino Acids (ml)")
    base_solution_water = fields.Float(string="Base Solution - Sterile Water (ml)")
    additives_sodium_chloride = fields.Float(string="Additive - Sodium Chloride (ml)")
    additives_potassium_chloride = fields.Float(string="Additive - Potassium Chloride (ml)")
    additives_calcium_gluconate = fields.Float(string="Additive - Calcium Gluconate (ml)")
    additives_magnesium_sulfate = fields.Float(string="Additive - Magnesium Sulfate (ml)")
    additives_sodium_phosphate = fields.Float(string="Additive - Sodium Phosphate (ml)")
    additives_vitamins = fields.Float(string="Additive - Vitamins Mixture (ml)")
    additives_trace_elements = fields.Float(string="Additive - Trace Elements (ml)")

    # Calculations
    tpn_rate = fields.Float(string="TPN Rate (ml/hr)")
    total_tpn_fluid_rate = fields.Float(string="Total TPN Fluid Rate (ml/hr)")
    non_protein_calories = fields.Float(string="Non-Protein Calories (kcal/day)")
    nitrogen_ratio = fields.Float(string="Nitrogen Ratio")

    # Prescription and Pharmacy Info
    prescriber_name = fields.Char(string="Prescriber Name")
    prescriber_id = fields.Char(string="Prescriber ID")
    nurse_name = fields.Char(string="Nurse Name")
    pharmacy_technician = fields.Char(string="Technician Name")
    notes = fields.Text(string="Notes")