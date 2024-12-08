from odoo import models, fields

class TPNForm(models.Model):
    _name = 'tpn.form'
    _description = 'Total Parenteral Nutrition Neonatal Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Adding chatter

    portal_user_id = fields.Many2one(
        'res.users',
        string="Portal User",
        help="User linked to the portal for this form.",
        default=lambda self: self.env.user
    )

    # General Information
    name = fields.Char(
        string="Patient Name",
        required=True,
        tracking=True  # Enable field tracking
    )
    hospital_no = fields.Char(
        string="Hospital No.",
        required=True,
        tracking=True
    )
    nationality = fields.Char(
        string="Nationality",
        tracking=True
    )
    treating_physician = fields.Char(
        string="Treating Physician",
        tracking=True
    )
    ward = fields.Char(
        string="Ward",
        tracking=True
    )
    age = fields.Integer(
        string="Age (days)",
        tracking=True
    )
    weight = fields.Float(
        string="Weight (kg)",
        tracking=True
    )
    height = fields.Float(
        string="Height (cm)",
        tracking=True
    )
    diagnosis = fields.Text(
        string="Diagnosis",
        tracking=True
    )
    tpn_indications = fields.Text(
        string="TPN Indications",
        tracking=True
    )

    # Prescription Details
    tpn_day = fields.Integer(
        string="Day(s) of TPN",
        tracking=True
    )
    tpn_route = fields.Selection(
        [('central', 'Central'), ('peripheral', 'Peripheral')],
        string="TPN Route",
        tracking=True
    )

    # Nutritional Fields
    dextrose_mg_kg_min = fields.Float(
        string="Dextrose (mg/kg/min)",
        tracking=True
    )
    dextrose_gm_day = fields.Float(
        string="Dextrose (gm/day)",
        tracking=True
    )
    amino_acids_gm_kg_day = fields.Float(
        string="Amino Acids (gm/kg/day)",
        tracking=True
    )
    fat_emulsion_gm_kg_day = fields.Float(
        string="Fat Emulsion 20% (gm/kg/day)",
        tracking=True
    )
    total_fluid_intake = fields.Float(
        string="Total Fluid Intake (ml/kg/day)",
        tracking=True
    )
    total_volume_tpn = fields.Float(
        string="Total Volume of TPN (ml/day)",
        tracking=True
    )

    # Additives
    sodium = fields.Float(
        string="Sodium (mmol/day)",
        tracking=True
    )
    potassium = fields.Float(
        string="Potassium (mmol/day)",
        tracking=True
    )
    calcium = fields.Float(
        string="Calcium (mmol/day)",
        tracking=True
    )
    magnesium = fields.Float(
        string="Magnesium (mmol/day)",
        tracking=True
    )
    phosphate = fields.Float(
        string="Phosphate (mmol/day)",
        tracking=True
    )
    chloride = fields.Float(
        string="Chloride (mmol/day)",
        tracking=True
    )
    acetate = fields.Float(
        string="Acetate",
        tracking=True
    )
    fat_soluble_vitamins = fields.Float(
        string="Fat Soluble Vitamins (ml/day)",
        tracking=True
    )
    water_soluble_vitamins = fields.Float(
        string="Water Soluble Vitamins (ml/day)",
        tracking=True
    )
    trace_elements = fields.Float(
        string="Trace Elements (ml/day)",
        tracking=True
    )
    heparin = fields.Float(
        string="Heparin (units/ml)",
        tracking=True
    )

    # Pharmacy Information
    base_solution_dextrose = fields.Float(
        string="Base Solution - Dextrose (ml)",
        tracking=True
    )
    base_solution_amino = fields.Float(
        string="Base Solution - Amino Acids (ml)",
        tracking=True
    )
    base_solution_water = fields.Float(
        string="Base Solution - Sterile Water (ml)",
        tracking=True
    )
    additives_sodium_chloride = fields.Float(
        string="Additive - Sodium Chloride (ml)",
        tracking=True
    )
    additives_potassium_chloride = fields.Float(
        string="Additive - Potassium Chloride (ml)",
        tracking=True
    )
    additives_calcium_gluconate = fields.Float(
        string="Additive - Calcium Gluconate (ml)",
        tracking=True
    )
    additives_magnesium_sulfate = fields.Float(
        string="Additive - Magnesium Sulfate (ml)",
        tracking=True
    )
    additives_sodium_phosphate = fields.Float(
        string="Additive - Sodium Phosphate (ml)",
        tracking=True
    )
    additives_vitamins = fields.Float(
        string="Additive - Vitamins Mixture (ml)",
        tracking=True
    )
    additives_trace_elements = fields.Float(
        string="Additive - Trace Elements (ml)",
        tracking=True
    )

    # Calculations
    tpn_rate = fields.Float(
        string="TPN Rate (ml/hr)",
        tracking=True
    )
    total_tpn_fluid_rate = fields.Float(
        string="Total TPN Fluid Rate (ml/hr)",
        tracking=True
    )
    non_protein_calories = fields.Float(
        string="Non-Protein Calories (kcal/day)",
        tracking=True
    )
    nitrogen_ratio = fields.Float(
        string="Nitrogen Ratio",
        tracking=True
    )

    # Prescription and Pharmacy Info
    prescriber_name = fields.Char(
        string="Prescriber Name",
        tracking=True
    )
    prescriber_id = fields.Char(
        string="Prescriber ID",
        tracking=True
    )
    nurse_name = fields.Char(
        string="Nurse Name",
        tracking=True
    )
    pharmacy_technician = fields.Char(
        string="Technician Name",
        tracking=True
    )
    notes = fields.Text(
        string="Notes",
        tracking=True
    )