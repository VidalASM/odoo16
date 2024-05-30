###############################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
###############################################################################

from odoo import fields, models


# Tables used for PLE Reports
class Table25(models.Model):
    _name = "l10n_pe_edi.table.25"
    _description = "Tabla 25: Convenios para evitar la doble tributación"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(string="Code", size=2, required=True)


class Table27(models.Model):
    _name = "l10n_pe_edi.table.27"
    _description = "Tabla 27: Tipo de Vinculacion economica"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(string="Code", size=2, required=True)
    description = fields.Text(string="Description")


class Table30(models.Model):
    _name = "l10n_pe_edi.table.30"
    _description = "Tabla 30: Clasificacion de lo Bienes " "y Servicios adquiridos"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(string="Code", size=1, required=True)


class Table31(models.Model):
    _name = "l10n_pe_edi.table.31"
    _description = "Tabla 31: Tipo de renta"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(string="Code", size=2, required=True)
    description = fields.Text(string="Description")


class Table32(models.Model):
    _name = "l10n_pe_edi.table.32"
    _description = (
        "Tabla 32: Modalidad del servicio prestado " "por el sujeto no domiciliado"
    )
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(string="Code", size=1, required=True)


class Table33(models.Model):
    _name = "l10n_pe_edi.table.33"
    _description = (
        "Tabla 33: Exoneraciones de operaciones de "
        "no domiciliados (ART. 19 DE LA LEY DEL IMPUESTO A LA RENTA)"
    )
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(string="Code", size=1, required=True)


class Table35(models.Model):
    _name = "l10n_pe_edi.table.35"
    _description = "Tabla 35: Paises"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(string="Code", size=4, required=True)
