# -*- coding: utf-8 -*-

from datetime import timedelta, date

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DocumentLevel(models.Model):
    _name = 'documents.level'

    name = fields.Char(required=True)
    user_ids = fields.Many2many('res.users')
    parent = fields.Many2one('documents.level', string='Nivel Padre')

class DocumentFile(models.Model):
    _name = 'documents.file'

    name = fields.Char('Nombre', required=True)
    type = fields.Char('Tipo')
    number = fields.Char('Numeración')
    description = fields.Char('Descripción')
    sgd_number = fields.Char('Número Expediente SGD')
    date_begin = fields.Date('Fecha de inicio', tracking=True, default=fields.Date.today())
    date_end = fields.Date('Fecha final', tracking=True, default=fields.Date.today())

class Document(models.Model):
    _inherit = 'documents.document'
    document_date = fields.Date('Fecha del documento', tracking=True, default=fields.Date.today())
    level_1 = fields.Many2one('documents.level', string='Fondo')
    level_2 = fields.Many2one('documents.level', string='Sección')
    level_3 = fields.Many2one('documents.level', string='Serie Documental')
    level_4 = fields.Many2one('documents.level', string='Sub Serie Documental')
    level_5 = fields.Many2one('documents.level', string='Año')
    origin = fields.Char('Origen')
    number = fields.Char('Número')
    issue = fields.Char('Asunto')
    sender = fields.Char('Remitente')
    file_id = fields.Many2one('documents.file', string='Expediente')
    social_reason = fields.Char('Razón Social')
    medium = fields.Char('Medio Portador')
    file_amount = fields.Integer('Cantidad Folios')
    image_amount = fields.Integer('Cantidad Imágenes')
    # Expedientes
    file_type = fields.Char('Tipo de Expediente')
    file_number = fields.Char('Numeración de Expediente')
    file_description = fields.Char('Descripción de Expediente')
    sgd_number = fields.Char('Número Expediente SGD')
    file_date_begin = fields.Date('Fecha de inicio Expediente', tracking=True, default=fields.Date.today())
    file_date_end = fields.Date('Fecha final Expediente', tracking=True, default=fields.Date.today())
