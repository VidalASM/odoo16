#######################################################################################
#
#    Copyright (C) 2019-TODAY OPeru.
#    Author      :  Grupo Odoo S.A.C. (<http://www.operu.pe>)
#
#    This program is copyright property of the author mentioned above.
#    You can`t redistribute it and/or modify it.
#
#######################################################################################

from odoo import api, fields, models


class CatalogTmpl(models.AbstractModel):
    _name = "l10n_pe_edi.catalog.tmpl"
    _description = "Catalog Template"
    _rec_name = "complete_name"
    _rec_names_search = ["name", "code"]

    active = fields.Boolean(default=True)
    code = fields.Char(index=True, required=True)
    name = fields.Char(string="Description", index=True, required=True)
    complete_name = fields.Char(compute="_compute_complete_name", store=True)

    @api.depends("name", "code")
    def _compute_complete_name(self):
        for rec in self:
            if rec.name and rec.code:
                rec.complete_name = "%s %s" % (rec.code, rec.name)
            else:
                rec.complete_name = rec.name


# CATALOGOS NO CREADOS
# Catalog No. 01: Codigos de Tipo de documento
# Catalog No. 02: Codigos de Tipo de moneda
# Catalog No. 04: Codigos de Pais
# Catalog No. 05: Codigos de Tipo de tributos
# Catalog No. 06: Codigos de Tipo de documento de identidad
# Catalog No. 13: Codigos de Ubicaion geografica (UBIGEO)


# Catalog No. 03: Codigos de Tipo de unidades de medida comercial
class Catalog03(models.Model):
    _name = "l10n_pe_edi.catalog.03"
    _description = "Catalog No. 03: Codigos de Tipo de unidades de medida comercial"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=3)


# Catalog No. 07: Codigos de Tipo de afectacion del IGV
class Catalog07(models.Model):
    _name = "l10n_pe_edi.catalog.07"
    _description = "Catalog No. 07: Codigos de Tipo de afectacion del IGV"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)
    tribute_code = fields.Char()
    code_of = fields.Char(size=2)


# Catalog No. 08: Codigos de Sistema de calculo del ISC
class Catalog08(models.Model):
    _name = "l10n_pe_edi.catalog.08"
    _description = "Catalog No. 08: Codigos de Sistemas de calculo del ISC"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)
    rate = fields.Float()
    code_of = fields.Char(size=1)


# Catalog No. 09: Codigos de Tipo de Nota de credito electronica
class Catalog09(models.Model):
    _name = "l10n_pe_edi.catalog.09"
    _description = "Catalog No. 09: Codigos de Tipo de Notas de credito electronica"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)
    code_of = fields.Char(size=2)


# Catalog No. 10: Codigos de Tipo de Nota de debito electronica
class Catalog10(models.Model):
    _name = "l10n_pe_edi.catalog.10"
    _description = "Catalog No. 10: Codigos de Tipo de Notas de debito electronica"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)
    code_of = fields.Char(size=1)


# Catalog No. 11: Codigos de Tipo de Valor de venta
class Catalog11(models.Model):
    _name = "l10n_pe_edi.catalog.11"
    _description = "Catalog No. 11: Codigos de Tipo de Valores de venta"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)


# Catalog No. 12: Codigos de Tipo de Documento relacionado tributario
class Catalog12(models.Model):
    _name = "l10n_pe_edi.catalog.12"
    _description = (
        "Catalog No. 12: Codigos de Tipo de Documentos relacionados tributarios"
    )
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)


# Catalog No. 14: Codigos de Otro concepto tributarios
class Catalog14(models.Model):
    _name = "l10n_pe_edi.catalog.14"
    _description = "Catalog No. 14: Codigos de Otros conceptos tributarios"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=4)


# Catalog No. 15: Codigos de Elemento adicionale en la factura y/o
# boleta de venta
class Catalog15(models.Model):
    _name = "l10n_pe_edi.catalog.15"
    _description = (
        "Catalog No. 15: Codigos de Elementos adicionales en la "
        "factura y/o boleta de venta"
    )
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=4)


# Catalog No. 16: Codigos de Tipo de Precio de venta unitario
class Catalog16(models.Model):
    _name = "l10n_pe_edi.catalog.16"
    _description = "Catalog No. 16: Codigos de Tipo de Precios de venta unitario"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)


# Catalog No. 17: Codigos de Tipo de Operacion
class Catalog17(models.Model):
    _name = "l10n_pe_edi.catalog.17"
    _description = "Catalog No. 17: Codigos de Tipo de Operacion"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)


# Catalog No. 18: Codigos de Modalidad de traslado
class Catalog18(models.Model):
    _name = "l10n_pe_edi.catalog.18"
    _description = "Catalog No. 18: Codigos de Modalidades de traslado"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)


# Catalog No. 19: Codigos de Estado de item
class Catalog19(models.Model):
    _name = "l10n_pe_edi.catalog.19"
    _description = "Catalog No. 19: Codigos de Estados de item"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=1)


# Catalog No. 20: Codigos de Motivo de traslado
class Catalog20(models.Model):
    _name = "l10n_pe_edi.catalog.20"
    _description = "Catalog No. 20: Codigos de Motivos de traslado"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)


# Catalog No. 21: Codigos de Documento relacionado para la guia
class Catalog21(models.Model):
    _name = "l10n_pe_edi.catalog.21"
    _description = "Catalog No. 21: Codigos de Documentos relacionados para la guia"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)


# Catalog No. 22: Codigos de Tipo de regimene de percepcion
class Catalog22(models.Model):
    _name = "l10n_pe_edi.catalog.22"
    _description = "Catalog No. 22: Codigos de Tipos de regimenes de percepcion"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)
    rate = fields.Float()


# Catalog No. 23: Codigos de Tipo de regimene de retencion
class Catalog23(models.Model):
    _name = "l10n_pe_edi.catalog.23"
    _description = "Catalog No. 23: Codigos de Tipos de regimenes de retencion"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)
    rate = fields.Float()


# Catalog No. 24: Codigos de Tarifa de servicio publico
class Catalog24(models.Model):
    _name = "l10n_pe_edi.catalog.24"
    _description = "Catalog No. 24: Codigos de Tarifas de servicio publico"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=4)
    type = fields.Char()


# Catalog No. 25: Codigos de Producto SUNAT
class Catalog25(models.Model):
    _name = "l10n_pe_edi.catalog.25"
    _description = "Catalog No. 25: Codigos de Productos SUNAT"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=8)


# Catalog No. 26: Codigos de Tipo de prestamo (credito hipotecario)
class Catalog26(models.Model):
    _name = "l10n_pe_edi.catalog.26"
    _description = (
        "Catalog No. 26: Codigos de Tipos de prestamo (credito hipo" "tecario)"
    )
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=1)


# Catalog No. 27: Codigos de Indicador de primera vivienda
class Catalog27(models.Model):
    _name = "l10n_pe_edi.catalog.27"
    _description = "Catalog No. 27: Codigos de Indicador de primera vivienda"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=1)


# Catalog No. 51: Codigos de Tipo de operacion
class Catalog51(models.Model):
    _name = "l10n_pe_edi.catalog.51"
    _description = "Catalog No. 51: Codigos de Tipo de operacion"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=4)
    type = fields.Char()


# Catalog No. 52: Codigos de Leyenda
class Catalog52(models.Model):
    _name = "l10n_pe_edi.catalog.52"
    _description = "Catalog No. 52: Codigos de Leyendas"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=4)


# Catalog No. 53: Codigos de Cargo o descuento
class Catalog53(models.Model):
    _name = "l10n_pe_edi.catalog.53"
    _description = "Catalog No. 53: Codigos de Cargo o descuento"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=2)
    level = fields.Char()


# Catalog No. 54: Codigos de Bien o servicio sujeto a detraccion
class Catalog54(models.Model):
    _name = "l10n_pe_edi.catalog.54"
    _description = "Catalog No. 54: Codigos de Bien o servicio sujeto a detraccion"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=3)
    code_of = fields.Char(size=2)
    rate = fields.Float()

    @api.depends("name", "code", "rate")
    def _compute_complete_name(self):
        for rec in self:
            if rec.name and rec.code:
                rec.complete_name = "%s %s (%s%%)" % (
                    rec.code,
                    rec.name,
                    str(rec.rate),
                )
            else:
                rec.complete_name = rec.name


# Catalog No. 55: Codigos de Identificacion del item
class Catalog55(models.Model):
    _name = "l10n_pe_edi.catalog.55"
    _description = "Catalog No. 55: Codigos de Identificacion del item"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=4)


# Catalog No. 56: Codigos de Tipo de servicio publico
class Catalog56(models.Model):
    _name = "l10n_pe_edi.catalog.56"
    _description = "Catalog No. 56: Codigos de Tipo de servicio publico"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=1)


# Catalog No. 57: Codigos de Tipo de servicio publico - telecomunicaciones
class Catalog57(models.Model):
    _name = "l10n_pe_edi.catalog.57"
    _description = (
        "Catalog No. 57: Codigos de Tipo de servicio publico - telecomunicaciones"
    )
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=1)


# Catalog No. 58: Codigos de Tipo de medidor - recibo de luz
class Catalog58(models.Model):
    _name = "l10n_pe_edi.catalog.58"
    _description = "Catalog No. 58: Codigos de Tipo de medidor - recibo de luz"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=1)


# Catalog No. 59: Codigos de Medio de pago
class Catalog59(models.Model):
    _name = "l10n_pe_edi.catalog.59"
    _description = "Catalog No. 59: Codigos de Medio de pago"
    _inherit = "l10n_pe_edi.catalog.tmpl"

    code = fields.Char(size=3)
    code_of = fields.Char(size=2)
