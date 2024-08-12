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
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta


class MeasurementHistory(models.Model):
    _name = "measurement.history"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Measurement History"

    _rec_name = "member"

    def _get_default_weight_uom(self):
        """ to get default weight uom """
        return self.env[
            'product.template']._get_weight_uom_name_from_ir_config_parameter()

    active = fields.Boolean(default="True")
    is_attend = fields.Boolean(string='Asistió', default=False)
    postpone_ids = fields.One2many(comodel_name='postpone.meeting', inverse_name='meeting_id', string='Postergaciones', readonly=True)
    member = fields.Many2one('res.partner', string='Socio', tracking=True, required=True, domain="[('gym_member', '!=',False)]")
    membership = fields.Many2one('gym.membership', string='Membresía', tracking=True, required=False)
    order_id = fields.Many2one('sale.order', string='Orden de Venta', tracking=True, required=False)
    date_start = fields.Datetime('Inicio de la cita', required=True)
    date_end = fields.Datetime(string='Finaliza')
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user, required=True)
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
    c_fmax = fields.Char(string='FMAX')
    c_fwork = fields.Char(string='FWORK')
    c_objetivo = fields.Char(string='OBJETIVO')
    c_observacion = fields.Char(string='OBSERVACION')
    c_f = fields.Char(string='F')
    c_t = fields.Char(string='T')
    c_nivel = fields.Selection(string='NIVEL', selection=[('n1', 'Novato 1'), ('n2', 'Novato 2'),('i', 'Intermedio'),('a', 'Avanzado'),])
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
    
    @api.onchange('member')
    def onchange_member(self):
        for rec in self:
            rec.gender = rec.member.gender
            rec.age = rec.member.age
            last_membership = self.env['gym.membership'].search([('member', '=', rec.member.id), ('state', '=', 'confirm')], order='id desc', limit=1)
            rec.membership = last_membership.id if last_membership else False
            return {'domain': {'membership': [('member', '=', rec.member.id)], 'order_id': [('partner_id', '=', rec.member.id)]}}
    
    @api.onchange('membership')
    def onchange_membership(self):
        for rec in self:
            rec.order_id = rec.membership.sale_order_id
    
    @api.onchange('date_start')
    def onchange_date_start(self):
        for rec in self:
            if rec.date_start:
                rec.date_end = rec.date_start + timedelta(minutes=20)
                rec.date = rec.date_start.date()

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
                
    #Funcion para marcar la asistencia de una cita con especialista.
    def toggle_is_attend(self):
        self.is_attend = not self.is_attend

class PostponeMeeting(models.Model):
    _name = ('postpone.meeting')

    cause = fields.Char(string='Motivo')
    date_postpone = fields.Date(string='Fecha registrada')
    start_date = fields.Datetime('Hora de la cita anterior')
    start_date_new = fields.Datetime('Hora de la cita reprogramada')
    meeting_id = fields.Many2one(comodel_name='measurement.history', string='Cita',ondelete='cascade')
    user_id = fields.Many2one(related="meeting_id.user_id",string="Por")
        
class MeetingPostponeWizard(models.TransientModel):
    _name = "meeting.wizard"

    #Esta funcion nos retorna el id de la cita.
    def _default_session(self):
        return self.env['measurement.history'].browse(self._context.get('active_id'))

    #Declaración de variables
    meeting_id = fields.Many2one(comodel_name='measurement.history', string='Cita', default=_default_session, readonly=True)
    user_id = fields.Many2one(comodel_name='res.users', string="Por",default=lambda self: self.env.user, readonly=True)
    cause = fields.Char(string='Motivo',default="Imprevisto")
    date_postpone = fields.Date(string='Registro', default=fields.Date.today, readonly=True)
    start_date_new = fields.Datetime('Reprogramación para', required=True)
    end_date_new = fields.Datetime('Finaliza', required=True)

    #En esta funcion validamos que postergaciones no supera la unidad.
    @api.onchange('start_date_new')
    def _onchange_start_date(self):
        if self.start_date_new:
            start = fields.Datetime.from_string(self.start_date_new)
            duration_meeting = timedelta(minutes=20)
            self.end_date_new = start + duration_meeting

    def create_postpone(self):
        meetings = [meeting for meeting in self.meeting_id.postpone_ids]
        if len(meetings) >= 1:
            #Si supera la unidad se procede a impedir la creación de la programación
            raise ValidationError("El socio no puede postergar más la cita a menos que pague por la reprogramación")
        #Si no supera la unidad se procede a crear en el modelo postpone.meeting
        for item in self:
            self.env['postpone.meeting'].create({
                'meeting_id': item.meeting_id.id,
                'user_id': item.user_id.id,
                'cause': self.cause,
                'date_postpone': datetime.today(),
                'start_date': item.meeting_id.date_start ,
                'start_date_new': item.start_date_new,
            })
            #Terminamos la funcion con la actualización del start_date con el start_date_new del del wizard
            item.meeting_id.date_start = self.start_date_new
            item.meeting_id.date_end = self.end_date_new
        return True
    