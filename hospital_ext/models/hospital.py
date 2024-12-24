from email.policy import default

from odoo import models, fields, api
from datetime import datetime, date

class TPNForm(models.Model):
    _name = 'tpn.form'
    _description = 'Total Parenteral Nutrition Neonatal Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Adding chatter

    seq_no = fields.Char(string='Reference', required=True, readonly=True, default=lambda self: self._get_default_sequence())

    @api.model
    def _get_default_sequence(self):
        return self.env['ir.sequence'].next_by_code('tpm.tpm') or '/'

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
    date = fields.Date(default=date.today())
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
    amino_acids_gm_day = fields.Float(
        string="Amino Acids (gm/day)",
        tracking=True
    )
    fat_emulsion_gm_kg_day = fields.Float(
        string="Fat Emulsion 20% (gm/kg/day)",
        tracking=True
    )
    fat_emulsion_gm_day = fields.Float(
        string="Fat Emulsion 20% (gm/day)",
        tracking=True
    )
    total_fluid_intake = fields.Float(
        string="Total Fluid Intake (ml/kg/day)",
        tracking=True
    )
    total_fluid_intake_ml_hr = fields.Float(
        string="Total Fluid Intake (ml/hour)",
        tracking=True
    )
    total_fluid_intake_ml_day = fields.Float(
        string="Total Fluid Intake (ml/day)",
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
    sodium_range = fields.Html(
        string="Sodium Range",
        tracking=True,
        default="<p>2-4 Mmol/kg/day</p>",
    )
    sodium_notes = fields.Html(
        string="Sodium Notes",
        tracking=True
    )

    potassium = fields.Float(
        string="Potassium (mmol/day)",
        tracking=True
    )
    potassium_range = fields.Html(
        string="Potassium Range",
        tracking=True,
        default="<p>2-4 Mmol/kg/day</p>",
    )
    potassium_notes = fields.Html(
        string="Potassium Notes",
        tracking=True
    )

    calcium = fields.Float(
        string="Calcium (mmol/day)",
        tracking=True
    )
    calcium_range = fields.Html(
        string="Calcium Range",
        tracking=True,
        default="<p>0.7-1.4 Mmol/kg/day</p>",
    )
    calcium_notes = fields.Html(
        string="Calcium Notes",
        tracking=True,
        default="<p>Give as Calcium Gluconate <br/>PHARMACY: check Ca/PO4 compatibility</p>",
    )

    magnesium = fields.Float(
        string="Magnesium (mmol/day)",
        tracking=True
    )
    magnesium_range = fields.Html(
        string="Magnesium Range",
        tracking=True,
        default="<p>0.15-0.25 Mmol/kg/day</p>",
    )
    magnesium_notes = fields.Html(
        string="Magnesium Notes",
        tracking=True
    )
    phosphate = fields.Float(
        string="Phosphate (mmol/day)",
        tracking=True
    )
    phosphate_range = fields.Html(
        string="Phosphate Range",
        tracking=True,
        default="<p>0.5-1.5 Mmol/kg/day</p>",
    )
    phosphate_notes = fields.Html(
        string="Phosphate Notes",
        tracking=True,
        default="<p>Na PO4(1 ml = 3 Mmol PO4 & 4 Mmol Na)<br/>KP04(1mL= 3 Mmol PO4 & 4 4 Mmol Na)</p>",
    )

    chloride = fields.Float(
        string="Chloride (mmol/day)",
        tracking=True
    )
    chloride_range = fields.Html(
        string="Chloride Range",
        tracking=True,
        default="<p>2-4 Mmol/kg/day</p>",
    )
    chloride_notes = fields.Html(
        string="Chloride Notes",
        tracking=True
    )

    acetate = fields.Float(
        string="Acetate",
        tracking=True
    )
    acetate_range = fields.Html(
        string="Acetate Range",
        tracking=True,
        default="<p>As needed</p>",
    )
    acetate_notes = fields.Html(
        string="Acetate Notes",
        tracking=True,
        default="<p>Acetate and CI should be in 1:1, unless it is<br/>indicated</p>",
    )

    fat_soluble_vitamins = fields.Float(
        string="Fat Soluble Vitamins (ml/day)",
        tracking=True
    )
    fat_soluble_vitamins_range = fields.Html(
        string="Fat Soluble Vitamins Range",
        tracking=True,
        default="<p><b>Neonates,</b> <2.5kg: 4mL/kg<br/><b>Children,</b> >2.5kg: 10mL/day<br/> Based on manufacture doing</p>",
    )
    fat_soluble_vitamins_notes = fields.Html(
        string="Fat Soluble Vitamins Notes",
        tracking=True,
        default="<p>-Max dose 10 mL/day<br/>(ImL contains 20 mcg Vit K1)<br/>- Use this brand for age of 11 years.</p>",
    )

    water_soluble_vitamins = fields.Float(
        string="Water Soluble Vitamins (ml/day)",
        tracking=True
    )
    water_soluble_vitamins_range = fields.Html(
        string="Water Soluble Vitamins Range",
        tracking=True,
        default="<p><b>>10Kg:</b> 10mL/day <br/> <b><10Kg:</b> 1mL/kg <br/> Based on Manufacture doing</p>",
    )
    water_soluble_vitamins_notes = fields.Html(
        string="Water Soluble Vitamins Notes",
        tracking=True,
        default="<p>Contains: Vit. BI, B2, nicotinamide, B6,<br/>pantothenic acid, C, biotin, folic acid & B12</p>"
    )

    trace_elements = fields.Float(
        string="Trace Elements (ml/day)",
        tracking=True
    )
    trace_elements_range = fields.Html(
        string="Trace Elements Range",
        tracking=True,
        default="<p>0.1 mL/kg <br/> Based on Manufacture doing</p>",
    )
    trace_elements_notes = fields.Html(
        string="Trace Elements Notes",
        tracking=True,
        default="<p>Contains: zine, cooper, manganese & chromium<br/>Caution: in renal dyst., biliary tract obstruction</p>"
    )

    heparin = fields.Float(
        string="Heparin (units/ml)",
        tracking=True
    )
    heparin_range = fields.Html(
        string="Heparin Range",
        tracking=True,
        default="<p>0.5-1 unit/ each mL of TPN </p>",
    )
    heparin_notes = fields.Html(
        string="Heparin Notes",
        tracking=True,
        default="<p>USED FOR PERIPHERAL TPN, Check PT/PTT,<br/>avoid in case of HIT or thromboctpenia</p>"
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