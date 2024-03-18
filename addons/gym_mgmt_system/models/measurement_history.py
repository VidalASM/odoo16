# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Shahul Faiz (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models


class MeasurementHistory(models.Model):
    _name = "measurement.history"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Measurement History"

    _rec_name = "member"

    def _get_default_weight_uom(self):
        """ to get default weight uom """
        return self.env[
            'product.template']._get_weight_uom_name_from_ir_config_parameter()

    member = fields.Many2one('res.partner', string='Socio', tracking=True, required=True, domain="[('gym_member', '!=',False)]")
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
    ], string="Género", required=True)
    age = fields.Integer(string='Edad', tracking=True, required=True)
    weight = fields.Float('Peso', digits='Stock Weight', store=True)
    weight_uom_name = fields.Char(string='Etiqueta de unidad de medida de peso', default=_get_default_weight_uom)
    height = fields.Float('Talla', digits='Stock Height', store=True)
    height_uom_name = fields.Char(string='Etiqueta de unidad de medida de peso', default='cm')
    # bmi = fields.Float('IMC', store=True, compute='compute_display_name')
    # bmr = fields.Float('TMB', store=True, compute='compute_display_name')
    bmi = fields.Float('IMC', store=True)
    bmr = fields.Float('TMB', store=True)
    neck = fields.Float('Cuello', store=True)
    biceps = fields.Float('Biceps', store=True)
    calf = fields.Float('Pantorrilla', store=True)
    hips = fields.Float('Caderas', store=True)
    chest = fields.Float('Pecho', store=True)
    waist = fields.Float('Cintura', store=True)
    thighs = fields.Float('Muslos', store=True)
    date = fields.Date(string='Fecha', help='Date from which measurement active.')
    # inbody
    weight_lower_limit = fields.Float('Lower Limit (Weight Normal Range)', digits='Stock Weight', store=True)
    weight_upper_limit = fields.Float('Upper Limit (Weight Normal Range)', digits='Stock Weight', store=True)
    tbw = fields.Float('TBW (Total Body Water)', digits='Stock Weight', store=True)
    tbw_lower_limit = fields.Float('Lower Limit (TBW Normal Range)', digits='Stock Weight', store=True)
    tbw_upper_limit = fields.Float('Upper Limit (TBW Normal Range)', digits='Stock Weight', store=True)
    protein = fields.Float('Protein', digits='Stock Weight', store=True)
    protein_lower_limit = fields.Float('Lower Limit (Protein Normal Range)', digits='Stock Weight', store=True)
    protein_upper_limit = fields.Float('Upper Limit (Protein Normal Range)', digits='Stock Weight', store=True)
    minerals = fields.Float('Minerals', digits='Stock Weight', store=True)
    minerals_lower_limit = fields.Float('Lower Limit (Minerals Normal Range)', digits='Stock Weight', store=True)
    minerals_upper_limit = fields.Float('Upper Limit (Minerals Normal Range)', digits='Stock Weight', store=True)
    bfm = fields.Float('BFM (Body Fat Mass)', digits='Stock Weight', store=True)
    bfm_lower_limit = fields.Float('Lower Limit (BFM Normal Range)', digits='Stock Weight', store=True)
    bfm_upper_limit = fields.Float('Upper Limit (BFM Normal Range)', digits='Stock Weight', store=True)
    ffm = fields.Float('FFM (Fat Free Mass)', digits='Stock Weight', store=True)
    ffm_lower_limit = fields.Float('Lower Limit (FFM Normal Range)', digits='Stock Weight', store=True)
    ffm_upper_limit = fields.Float('Upper Limit (FFM Normal Range)', digits='Stock Weight', store=True)
    smm = fields.Float('SMM (Skeletal Muscle Mass)', digits='Stock Weight', store=True)
    smm_lower_limit = fields.Float('Lower Limit (SMM Normal Range)', digits='Stock Weight', store=True)
    smm_upper_limit = fields.Float('Upper Limit (SMM Normal Range)', digits='Stock Weight', store=True)

    bmi_lower_limit = fields.Float('Lower Limit (BMI Normal Range)', digits='Stock Weight', store=True)
    bmi_upper_limit = fields.Float('Upper Limit (BMI Normal Range)', digits='Stock Weight', store=True)
    pbf = fields.Float('PBF (Percent Body Fat)', digits='Stock Weight', store=True)
    pbf_lower_limit = fields.Float('Lower Limit (PBF Normal Range)', digits='Stock Weight', store=True)
    pbf_upper_limit = fields.Float('Upper Limit (PBF Normal Range)', digits='Stock Weight', store=True)
    ffm_right_arm = fields.Float('FFM of Right Arm', digits='Stock Weight', store=True)
    ffm_right_arm_per = fields.Float('FFM% of Right Arm', digits='Stock Weight', store=True)
    ffm_left_arm = fields.Float('FFM of Left Arm', digits='Stock Weight', store=True)
    ffm_left_arm_per = fields.Float('FFM% of Left Arm', digits='Stock Weight', store=True)
    ffm_trunk = fields.Float('FFM of Trunk', digits='Stock Weight', store=True)
    ffm_trunk_per = fields.Float('FFM% of Trunk', digits='Stock Weight', store=True)
    ffm_right_leg = fields.Float('FFM of Right Leg', digits='Stock Weight', store=True)
    ffm_right_leg_per = fields.Float('FFM% of Right Leg', digits='Stock Weight', store=True)
    ffm_left_leg = fields.Float('FFM of Left Leg', digits='Stock Weight', store=True)
    ffm_left_leg_per = fields.Float('FFM% of Left Leg', digits='Stock Weight', store=True)
    bfm_right_arm = fields.Float('BFM of Right Arm', digits='Stock Weight', store=True)
    bfm_right_arm_per = fields.Float('BFM% of Right Arm', digits='Stock Weight', store=True)
    bfm_left_arm = fields.Float('BFM of Left Arm', digits='Stock Weight', store=True)
    bfm_left_arm_per = fields.Float('BFM% of Left Arm', digits='Stock Weight', store=True)
    bfm_trunk = fields.Float('BFM of Trunk', digits='Stock Weight', store=True)
    bfm_trunk_per = fields.Float('BFM% of Trunk', digits='Stock Weight', store=True)
    bfm_right_leg = fields.Float('BFM of Right Leg', digits='Stock Weight', store=True)
    bfm_right_leg_per = fields.Float('BFM% of Right Leg', digits='Stock Weight', store=True)
    bfm_left_leg = fields.Float('BFM of Left Leg', digits='Stock Weight', store=True)
    bfm_left_leg_per = fields.Float('BFM% of Left Leg', digits='Stock Weight', store=True)
    inbody_score = fields.Float('InBody Score', digits='Stock Weight', store=True)
    target_score = fields.Float('Target Weight', digits='Stock Weight', store=True)
    weight_control = fields.Float('Weight Control', digits='Stock Weight', store=True)
    bfm_control = fields.Float('BFM Control', digits='Stock Weight', store=True)
    ffm_control = fields.Float('FFM Control', digits='Stock Weight', store=True)
    
    whr = fields.Float('WHR (Waist-Hip Ratio)', digits='Stock Weight', store=True)
    whr_lower = fields.Float('Lower Limit (WHR Normal Range)', digits='Stock Weight', store=True)
    whr_upper = fields.Float('Upper Limit (WHR Normal Range)', digits='Stock Weight', store=True)
    vfl = fields.Float('VFL (Visceral Fat Level)', digits='Stock Weight', store=True)
    obesity = fields.Float('Obesity Degree', digits='Stock Weight', store=True)
    obesity_lower = fields.Float('Lower Limit (Obesity Degree Normal Range)', digits='Stock Weight', store=True)
    obesity_upper = fields.Float('Upper Limit (Obesity Degree Normal Range)', digits='Stock Weight', store=True)
    impedance_20_ra = fields.Float('20kHz-RA Impedance', digits='Stock Weight', store=True)
    impedance_20_la = fields.Float('20kHz-LA Impedance', digits='Stock Weight', store=True)
    impedance_20_tr = fields.Float('20kHz-TR Impedance', digits='Stock Weight', store=True)
    impedance_20_rl = fields.Float('20kHz-RL Impedance', digits='Stock Weight', store=True)
    impedance_20_ll = fields.Float('20kHz-LL Impedance', digits='Stock Weight', store=True)
    impedance_100_ra = fields.Float('100kHz-RA Impedance', digits='Stock Weight', store=True)
    impedance_100_la = fields.Float('100kHz-LA Impedance', digits='Stock Weight', store=True)
    impedance_100_tr = fields.Float('100kHz-TR Impedance', digits='Stock Weight', store=True)
    impedance_100_rl = fields.Float('100kHz-RL Impedance', digits='Stock Weight', store=True)
    impedance_100_ll = fields.Float('100kHz-LL Impedance', digits='Stock Weight', store=True)
    mca = fields.Float('Measured Circumference of Abdomen', digits='Stock Weight', store=True)
    growth = fields.Float('Growth Score', digits='Stock Weight', store=True)
    obesityc = fields.Float('Obesity Degree of a Child', digits='Stock Weight', store=True)
    obesityc_lower = fields.Float('Lower Limit (Obesity Degree of a Child Normal Range)', digits='Stock Weight', store=True)
    obesityc_upper = fields.Float('Upper Limit (Obesity Degree of a Child Normal Range)', digits='Stock Weight', store=True)
    systolic = fields.Float('Systolic', digits='Stock Weight', store=True)
    diastolic = fields.Float('Diastolic', digits='Stock Weight', store=True)
    pulse = fields.Float('Pulse', digits='Stock Weight', store=True)
    ma_pressure = fields.Float('Mean Artery Pressure', digits='Stock Weight', store=True)
    pulse_pressure = fields.Float('Pulse Pressure', digits='Stock Weight', store=True)
    rate_pressure = fields.Float('Rate Pressure Product', digits='Stock Weight', store=True)
    smi = fields.Float('SMI', digits='Stock Weight', store=True)
    calorie = fields.Float('Recommended Calorie Intake', digits='Stock Weight', store=True)
    bmr_lower = fields.Float('Lower Limit (BMR Normal Range)', digits='Stock Weight', store=True)
    bmr_upper = fields.Float('Upper Limit (BMR Normal Range)', digits='Stock Weight', store=True)
    systolic2 = fields.Float('Systolic2', digits='Stock Weight', store=True)
    diastolic2 = fields.Float('Diastolic2', digits='Stock Weight', store=True)
    pulse2 = fields.Float('Pulse2', digits='Stock Weight', store=True)
    ma2_pressure = fields.Float('Mean Artery Pressure2', digits='Stock Weight', store=True)
    pulse2_pressure = fields.Float('Pulse Pressure2', digits='Stock Weight', store=True)
    rate2_pressure = fields.Float('Rate Pressure Product2', digits='Stock Weight', store=True)
    smm_wt = fields.Float('SMM/WT', digits='Stock Weight', store=True)
    ffmi = fields.Float('FFMI (Fat Free Mass Index)', digits='Stock Weight', store=True)
    fmi = fields.Float('FMI (Fat Mass Index)', digits='Stock Weight', store=True)

    @api.depends('weight', 'height')
    def compute_display_name(self):
        """ based on weight and height ,calculate the bmi and bmr"""
        if self.weight and self.height:
            self.bmi = (self.weight / self.height / self.height) * 10000

            if self.gender == "male":
                self.bmr = 66.47 + (13.75 * self.weight) + \
                           (5.003 * self.height) - (6.755 * self.age)

            if self.gender == "female":
                self.bmr = 655.1 + (9.563 * self.weight) + \
                           (1.85 * self.height) - (6.755 * self.age)
