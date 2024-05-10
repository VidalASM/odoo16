from odoo import api, fields, models


class EEFFPLE(models.Model):
    _name = 'eeff.ple'
    _description = 'Rubro EEFF PLE'
    _inherit = 'model.sunat.catalog'

    sequence = fields.Integer(
        required=True,
        default=1,
        string='Secuencia'
    )
    # The 'parent_id' field had to be changed from Many2one to Many2many
    # This field will be hidden and for the next version remove this field
    parent_id = fields.Many2one(
        string='Padre',
        comodel_name='eeff.ple'
    )
    parent_ids = fields.Many2many(
        'eeff.ple',
        'eeff_ple_eeff_ple_rel',
        'eeff_ple1_id',
        'eeff_ple2_id',
        string='Padre',
    )
    eeff_type = fields.Selection(
        selection=[
            ('3.1', '3.1 ESF'),
            ('3.18', '3.18 EFEMD'),
            ('3.19', '3.19 ECPN'),
            ('3.20', '3.20 EERR'),
            ('3.24', '3.24 ERI'),
            ('3.25', '3.25 EFEMI')
        ],
        string='Tipo'
    )

    @api.model
    def automated_links(self):
        data_level_1 = [
            {'id': 1, 'sequence': 32, 'code': '1D020T', 'description': 'TOTAL DE ACTIVOS', 'eeff_type': '3.1'},
            {'id': 2, 'sequence': 66, 'code': '1D070T', 'description': 'TOTAL PASIVO Y PATRIMONIO', 'eeff_type': '3.1'},
            {'id': 3, 'sequence': 87, 'code': '2D07ST', 'description': 'Ganancia (Pérdida) Neta del Ejercicio', 'eeff_type': '3.20'},
            {'id': 4, 'sequence': 151, 'code': '3D0402', 'description': 'Efectivo y Equivalente al Efectivo al Inicio del Ejercicio', 'eeff_type': '3.18'},
            {'id': 5, 'sequence': 152, 'code': '3D04ST', 'description': 'Efectivo y Equivalente al Efectivo al Final del Ejercicio', 'eeff_type': '3.18'},
            {'id': 6, 'sequence': 173, 'code': '5D04ST', 'description': 'Resultado Integral Total del Ejercicio, neto del Impuesto a las Ganancias', 'eeff_type': '3.24'},
            {'id': 7, 'sequence': 190, 'code': '4D01ST', 'description': 'Saldos al 31 de diciembre de', 'eeff_type': '3.19'},
            {'id': 8, 'sequence': 207, 'code': '4D02ST', 'description': 'Saldos al 31 de diciembre de', 'eeff_type': '3.19'},
            {'id': 9, 'sequence': 282, 'code': '3D0405', 'description': 'Aumento (Disminución) Neto de Efectivo y Equivalente al Efectivo', 'eeff_type': '3.25'},
            {'id': 10, 'sequence': 283, 'code': '3D0402', 'description': 'Efectivo y Equivalente al Efectivo al Inicio del Ejercicio', 'eeff_type': '3.25'},
            {'id': 11, 'sequence': 284, 'code': '3D04ST', 'description': 'Efectivo y Equivalente al Efectivo al Finalizar el Ejercicio', 'eeff_type': '3.25'}
        ]
        data_level_2 = [
            {'id': 1, 'id_parent': 1, 'sequence': 16, 'code': '1D01ST', 'description': 'Total Activos Corrientes', 'eeff_type': '3.1'},
            {'id': 2, 'id_parent': 1, 'sequence': 31, 'code': '1D02ST', 'description': 'Total Activos No Corrientes', 'eeff_type': '3.1'},
            {'id': 3, 'id_parent': 2, 'sequence': 57, 'code': '1D040T', 'description': 'Total Pasivos', 'eeff_type': '3.1'},
            {'id': 4, 'id_parent': 2, 'sequence': 65, 'code': '1D07ST', 'description': 'Total Patrimonio', 'eeff_type': '3.1'},
            {'id': 5, 'id_parent': 3, 'sequence': 83, 'code': '2D04ST', 'description': 'Resultado antes de Impuesto a las Ganancias', 'eeff_type': '3.20'},
            {'id': 6, 'id_parent': 3, 'sequence': 84, 'code': '2D0502', 'description': 'Gasto por Impuesto a las Ganancias', 'eeff_type': '3.20'},
            {'id': 7, 'id_parent': 3, 'sequence': 86, 'code': '2D0504', 'description': 'Ganancia (pérdida) procedente de operaciones discontinuadas, neta del impuesto a las ganancias', 'eeff_type': '3.20'},
            {'id': 8, 'id_parent': 3, 'sequence': 153, 'code': '5D0101', 'description': 'Ganancia (Pérdida) Neta del Ejercicio', 'eeff_type': '3.24'},
            {'id': 9, 'id_parent': 3, 'sequence': 208, 'code': '3D05ST', 'description': 'Ganancia (Pérdida) Neta del Ejercicio', 'eeff_type': '3.25'},
            {'id': 10, 'id_parent': 5, 'sequence': 150, 'code': '3D0405', 'description': 'Aumento (Disminución) Neto de Efectivo y Equivalente al Efectivo', 'eeff_type': '3.18'},
            {'id': 11, 'id_parent': 6, 'sequence': 172, 'code': '5D03ST', 'description': 'Otros Resultado Integral', 'eeff_type': '3.24'},
            {'id': 12, 'id_parent': 7, 'sequence': 189, 'code': '4D0136', 'description': 'Total incremento (disminución) en el patrimonio', 'eeff_type': '3.19'},
            {'id': 13, 'id_parent': 8, 'sequence': 206, 'code': '4D0236', 'description': 'Total incremento (disminución) en el patrimonio', 'eeff_type': '3.19'},
            {'id': 14, 'id_parent': 9, 'sequence': 279, 'code': '3D03ST', 'description': 'Flujos de Efectivo y Equivalente al Efectivo Procedente de (Utilizados en) Actividades de Financiación', 'eeff_type': '3.25'},
            {'id': 15, 'id_parent': 9, 'sequence': 280, 'code': '3D0401', 'description': 'Aumento (Disminución) Neto de Efectivo y Equivalente al Efectivo, antes de las Variaciones en las Tasas de Cambio', 'eeff_type': '3.25'},
            {'id': 16, 'id_parent': 9, 'sequence': 281, 'code': '3D0404', 'description': 'Efectos de las Variaciones en las Tasas de Cambio sobre el Efectivo y Equivalentes al Efectivo', 'eeff_type': '3.25'}
        ]
        data_level_3 = [
            {'id': 1, 'id_parent': 1, 'sequence': 1, 'code': '1D0109', 'description': 'Efectivo y Equivalentes al Efectivo', 'eeff_type': '3.1'},
            {'id': 2, 'id_parent': 1, 'sequence': 2, 'code': '1D0114', 'description': 'Otros Activos Financieros', 'eeff_type': '3.1'},
            {'id': 3, 'id_parent': 1, 'sequence': 3, 'code': '1D0121', 'description': 'Cuentas por cobrar comerciales y otras cuentas por cobrar', 'eeff_type': '3.1'},
            {'id': 4, 'id_parent': 1, 'sequence': 8, 'code': '1D0106', 'description': 'Inventarios', 'eeff_type': '3.1'},
            {'id': 5, 'id_parent': 1, 'sequence': 9, 'code': '1D0112', 'description': 'Activos Biológicos', 'eeff_type': '3.1'},
            {'id': 6, 'id_parent': 1, 'sequence': 10, 'code': '1D0117', 'description': 'Activos por Impuestos a las Ganancias', 'eeff_type': '3.1'},
            {'id': 7, 'id_parent': 1, 'sequence': 11, 'code': '1D0113', 'description': 'Otros Activos no financieros', 'eeff_type': '3.1'},
            {'id': 8, 'id_parent': 1, 'sequence': 12, 'code': '1D0118', 'description': 'Total Activos Corrientes Distintos de los Activos o Grupos de Activos para su Disposición Clasificados como Mantenidos para la Venta o para Distribuir a los Propietarios', 'eeff_type': '3.1'},
            {'id': 9, 'id_parent': 1, 'sequence': 15, 'code': '1D0115', 'description': 'Activos no Corrientes o Grupos de Activos para su Disposición Clasificados como Mantenidos para la Venta o como Mantenidos para Distribuir a los Propietarios', 'eeff_type': '3.1'},
            {'id': 10, 'id_parent': 2, 'sequence': 17, 'code': '1D0217', 'description': 'Otros Activos Financieros', 'eeff_type': '3.1'},
            {'id': 11, 'id_parent': 2, 'sequence': 18, 'code': '1D0221', 'description': 'Inversiones en subsidiarias, negocios conjuntos y asociadas', 'eeff_type': '3.1'},
            {'id': 12, 'id_parent': 2, 'sequence': 19, 'code': '1D0219', 'description': 'Cuentas por cobrar comerciales y otras cuentas por cobrar', 'eeff_type': '3.1'},
            {'id': 13, 'id_parent': 2, 'sequence': 24, 'code': '1D0216', 'description': 'Activos Biológicos', 'eeff_type': '3.1'},
            {'id': 14, 'id_parent': 2, 'sequence': 25, 'code': '1D0211', 'description': 'Propiedades de Inversión', 'eeff_type': '3.1'},
            {'id': 15, 'id_parent': 2, 'sequence': 26, 'code': '1D0205', 'description': 'Propiedades, Planta y Equipo (neto)', 'eeff_type': '3.1'},
            {'id': 16, 'id_parent': 2, 'sequence': 27, 'code': '1D0206', 'description': 'Activos intangibles distintos de la plusvalía', 'eeff_type': '3.1'},
            {'id': 17, 'id_parent': 2, 'sequence': 28, 'code': '1D0207', 'description': 'Activos por impuestos diferidos', 'eeff_type': '3.1'},
            {'id': 18, 'id_parent': 2, 'sequence': 29, 'code': '1D0212', 'description': 'Plusvalía', 'eeff_type': '3.1'},
            {'id': 19, 'id_parent': 2, 'sequence': 30, 'code': '1D0208', 'description': 'Otros Activos no financieros', 'eeff_type': '3.1'},
            {'id': 20, 'id_parent': 3, 'sequence': 45, 'code': '1D03ST', 'description': 'Total Pasivos Corrientes', 'eeff_type': '3.1'},
            {'id': 21, 'id_parent': 3, 'sequence': 56, 'code': '1D04ST', 'description': 'Total Pasivos No Corrientes', 'eeff_type': '3.1'},
            {'id': 22, 'id_parent': 4, 'sequence': 58, 'code': '1D0701', 'description': 'Capital Emitido', 'eeff_type': '3.1'},
            {'id': 23, 'id_parent': 4, 'sequence': 59, 'code': '1D0702', 'description': 'Primas de Emisión', 'eeff_type': '3.1'},
            {'id': 24, 'id_parent': 4, 'sequence': 60, 'code': '1D0703', 'description': 'Acciones de Inversión', 'eeff_type': '3.1'},
            {'id': 25, 'id_parent': 4, 'sequence': 61, 'code': '1D0711', 'description': 'Acciones Propias en Cartera', 'eeff_type': '3.1'},
            {'id': 26, 'id_parent': 4, 'sequence': 62, 'code': '1D0712', 'description': 'Otras Reservas de Capital', 'eeff_type': '3.1'},
            {'id': 27, 'id_parent': 4, 'sequence': 63, 'code': '1D0707', 'description': 'Resultados Acumulados', 'eeff_type': '3.1'},
            {'id': 28, 'id_parent': 4, 'sequence': 64, 'code': '1D0708', 'description': 'Otras Reservas de Patrimonio', 'eeff_type': '3.1'},
            {'id': 29, 'id_parent': 5, 'sequence': 76, 'code': '2D03ST', 'description': 'Ganancia (Pérdida) por actividades de operación', 'eeff_type': '3.20'},
            {'id': 30, 'id_parent': 5, 'sequence': 77, 'code': '2D0401', 'description': 'Ingresos Financieros', 'eeff_type': '3.20'},
            {'id': 31, 'id_parent': 5, 'sequence': 78, 'code': '2D0402', 'description': 'Gastos Financieros', 'eeff_type': '3.20'},
            {'id': 32, 'id_parent': 5, 'sequence': 79, 'code': '2D0410', 'description': 'Diferencias de Cambio neto', 'eeff_type': '3.20'},
            {'id': 33, 'id_parent': 5, 'sequence': 80, 'code': '2D0414', 'description': 'Otros ingresos (gastos) de las subsidiarias,negocios conjuntos y asociadas', 'eeff_type': '3.20'},
            {'id': 34, 'id_parent': 5, 'sequence': 81, 'code': '2D0411', 'description': 'Ganancias (Pérdidas) que surgen de la Diferencia entre el Valor Libro Anterior y el Valor Justo de Activos Financieros Reclasificados Medidos a Valor Razonable', 'eeff_type': '3.20'},
            {'id': 35, 'id_parent': 5, 'sequence': 82, 'code': '2D0413', 'description': 'Diferencia entre el importe en libros de los activos distribuidos y el importe en libros del dividendo a pagar', 'eeff_type': '3.20'},
            {'id': 36, 'id_parent': 7, 'sequence': 85, 'code': '2D0503', 'description': 'Ganancia (Pérdida) Neta de Operaciones  Continuadas', 'eeff_type': '3.20'},
            {'id': 37, 'id_parent': 10, 'sequence': 149, 'code': '3D0404', 'description': 'Efectos de las Variaciones en las Tasas de Cambio sobre el Efectivo y Equivalentes al Efectivo', 'eeff_type': '3.18'},
            {'id': 38, 'id_parent': 11, 'sequence': 171, 'code': '5D02ST', 'description': 'Suma de Impuestos a las Ganancias Relacionados con Componentes de Otro Resultado Integral', 'eeff_type': '3.24'},
            {'id': 39, 'id_parent': 12, 'sequence': 180, 'code': '4D0131', 'description': 'Resultado Integral Total del Ejercicio', 'eeff_type': '3.19'},
            {'id': 40, 'id_parent': 12, 'sequence': 181, 'code': '4D0104', 'description': 'Dividendos en Efectivo Declarados', 'eeff_type': '3.19'},
            {'id': 41, 'id_parent': 12, 'sequence': 182, 'code': '4D0105', 'description': 'Emisión (reducción) de patrimonio', 'eeff_type': '3.19'},
            {'id': 42, 'id_parent': 12, 'sequence': 183, 'code': '4D0132', 'description': 'Reducción o Amortización de Acciones de Inversión', 'eeff_type': '3.19'},
            {'id': 43, 'id_parent': 12, 'sequence': 184, 'code': '4D0133', 'description': 'Incremento (Disminución) por otras Aportaciones de los Propietarios', 'eeff_type': '3.19'},
            {'id': 44, 'id_parent': 12, 'sequence': 185, 'code': '4D0134', 'description': 'Disminución (Incremento) por otras Distribuciones a los Propietarios', 'eeff_type': '3.19'},
            {'id': 45, 'id_parent': 12, 'sequence': 186, 'code': '4D0135', 'description': 'Incremento (Disminución) por Cambios en la Participación de Subsidiarias que no impliquen Pérdidas de Control', 'eeff_type': '3.19'},
            {'id': 46, 'id_parent': 12, 'sequence': 187, 'code': '4D0114', 'description': 'Incremento (disminución) por transacciones con acciones propias en cartera', 'eeff_type': '3.19'},
            {'id': 47, 'id_parent': 12, 'sequence': 188, 'code': '4D0112', 'description': 'Incremento (Disminución) por Transferencia y Otros Cambios de patrimonio', 'eeff_type': '3.19'},
            {'id': 48, 'id_parent': 13, 'sequence': 197, 'code': '4D0231', 'description': 'Resultado Integral Total del Ejercicio', 'eeff_type': '3.19'},
            {'id': 49, 'id_parent': 13, 'sequence': 198, 'code': '4D0204', 'description': 'Dividendos en Efectivo Declarados', 'eeff_type': '3.19'},
            {'id': 50, 'id_parent': 13, 'sequence': 199, 'code': '4D0205', 'description': 'Emisión (reducción) de patrimonio', 'eeff_type': '3.19'},
            {'id': 51, 'id_parent': 13, 'sequence': 200, 'code': '4D0232', 'description': 'Reducción o Amortización de Acciones de Inversión', 'eeff_type': '3.19'},
            {'id': 52, 'id_parent': 13, 'sequence': 201, 'code': '4D0233', 'description': 'Incremento (Disminución) por otras Aportaciones de los Propietarios', 'eeff_type': '3.19'},
            {'id': 53, 'id_parent': 13, 'sequence': 202, 'code': '4D0234', 'description': 'Disminución (Incremento) por otras Distribuciones a los Propietarios', 'eeff_type': '3.19'},
            {'id': 54, 'id_parent': 13, 'sequence': 203, 'code': '4D0235', 'description': 'Incremento (Disminución) por Cambios en la Participación de Subsidiarias que no impliquen Pérdidas de Control', 'eeff_type': '3.19'},
            {'id': 55, 'id_parent': 13, 'sequence': 204, 'code': '4D0214', 'description': 'Incremento (disminución) por transacciones con acciones propias en cartera', 'eeff_type': '3.19'},
            {'id': 56, 'id_parent': 13, 'sequence': 205, 'code': '4D0212', 'description': 'Incremento (Disminución) por Transferencia y Otros Cambios de patrimonio', 'eeff_type': '3.19'},
            {'id': 57, 'id_parent': 14, 'sequence': 262, 'code': '3D02ST', 'description': 'Flujos de Efectivo y Equivalente al Efectivo Procedente de (Utilizados en) Actividades de Inversión', 'eeff_type': '3.25'},
            {'id': 58, 'id_parent': 14, 'sequence': 263, 'code': '3D0325', 'description': 'Obtención de Préstamos', 'eeff_type': '3.25'},
            {'id': 59, 'id_parent': 14, 'sequence': 264, 'code': '3D0319', 'description': 'Préstamos de entidades relacionadas', 'eeff_type': '3.25'},
            {'id': 60, 'id_parent': 14, 'sequence': 265, 'code': '3D0326', 'description': 'Cambios en las participaciones en la propiedad de subsidiarias que no resultan en pérdida de control', 'eeff_type': '3.25'},
            {'id': 61, 'id_parent': 14, 'sequence': 266, 'code': '3D0327', 'description': 'Emisión de Acciones', 'eeff_type': '3.25'},
            {'id': 62, 'id_parent': 14, 'sequence': 267, 'code': '3D0328', 'description': 'Emisión de Otros Instrumentos de Patrimonio', 'eeff_type': '3.25'},
            {'id': 63, 'id_parent': 14, 'sequence': 268, 'code': '3D0329', 'description': 'Subvenciones del gobierno', 'eeff_type': '3.25'},
            {'id': 64, 'id_parent': 14, 'sequence': 269, 'code': '3D0330', 'description': 'Amortización o pago de Préstamos', 'eeff_type': '3.25'},
            {'id': 65, 'id_parent': 14, 'sequence': 270, 'code': '3D0322', 'description': 'Pasivos por Arrendamiento Financiero', 'eeff_type': '3.25'},
            {'id': 66, 'id_parent': 14, 'sequence': 271, 'code': '3D0321', 'description': 'Préstamos de entidades relacionadas', 'eeff_type': '3.25'},
            {'id': 67, 'id_parent': 14, 'sequence': 272, 'code': '3D0331', 'description': 'Cambios en las participaciones en la propiedad de subsidiarias que no resultan en pérdida de control', 'eeff_type': '3.25'},
            {'id': 68, 'id_parent': 14, 'sequence': 273, 'code': '3D0310', 'description': 'Recompra o Rescate de Acciones de la Entidad (Acciones en Cartera)', 'eeff_type': '3.25'},
            {'id': 69, 'id_parent': 14, 'sequence': 274, 'code': '3D0323', 'description': 'Adquisición de Otras Participaciones en el Patrimonio', 'eeff_type': '3.25'},
            {'id': 70, 'id_parent': 14, 'sequence': 275, 'code': '3D0311', 'description': 'Intereses pagados', 'eeff_type': '3.25'},
            {'id': 71, 'id_parent': 14, 'sequence': 276, 'code': '3D0305', 'description': 'Dividendos pagados', 'eeff_type': '3.25'},
            {'id': 72, 'id_parent': 14, 'sequence': 277, 'code': '3D0332', 'description': 'Impuestos a las ganancias (pagados) reembolsados', 'eeff_type': '3.25'},
            {'id': 73, 'id_parent': 14, 'sequence': 278, 'code': '3D0333', 'description': 'Otros cobros (pagos) de efectivo relativos a la actividad de financiación', 'eeff_type': '3.25'}
        ]
        data_level_4 = [
            {'id': 1, 'id_parent': 3, 'sequence': 4, 'code': '1D0103', 'description': 'Cuentas por Cobrar Comerciales (neto)', 'eeff_type': '3.1'},
            {'id': 2, 'id_parent': 3, 'sequence': 5, 'code': '1D0105', 'description': 'Otras Cuentas por Cobrar (neto)', 'eeff_type': '3.1'},
            {'id': 3, 'id_parent': 3, 'sequence': 6, 'code': '1D0104', 'description': 'Cuentas por Cobrar a Entidades Relacionadas', 'eeff_type': '3.1'},
            {'id': 4, 'id_parent': 3, 'sequence': 7, 'code': '1D0107', 'description': 'Anticipos', 'eeff_type': '3.1'},
            {'id': 5, 'id_parent': 8, 'sequence': 13, 'code': '1D0119', 'description': 'Activos no Corrientes o Grupos de Activos para su Disposición Clasificados como Mantenidos para la Venta', 'eeff_type': '3.1'},
            {'id': 6, 'id_parent': 8, 'sequence': 14, 'code': '1D0120', 'description': 'Activos no Corrientes o Grupos de Activos para su Disposición Clasificados como Mantenidos para Distribuir a los Propietarios', 'eeff_type': '3.1'},
            {'id': 7, 'id_parent': 12, 'sequence': 20, 'code': '1D0201', 'description': 'Cuentas por Cobrar Comerciales', 'eeff_type': '3.1'},
            {'id': 8, 'id_parent': 12, 'sequence': 21, 'code': '1D0203', 'description': 'Otras Cuentas por Cobrar', 'eeff_type': '3.1'},
            {'id': 9, 'id_parent': 12, 'sequence': 22, 'code': '1D0202', 'description': 'Cuentas por Cobrar a Entidades Relacionadas', 'eeff_type': '3.1'},
            {'id': 10, 'id_parent': 12, 'sequence': 23, 'code': '1D0220', 'description': 'Anticipos', 'eeff_type': '3.1'},
            {'id': 11, 'id_parent': 20, 'sequence': 33, 'code': '1D0309', 'description': 'Otros Pasivos Financieros', 'eeff_type': '3.1'},
            {'id': 12, 'id_parent': 20, 'sequence': 34, 'code': '1D0316', 'description': 'Cuentas por pagar comerciales y otras cuentas por pagar', 'eeff_type': '3.1'},
            {'id': 13, 'id_parent': 20, 'sequence': 39, 'code': '1D0313', 'description': 'Provisión por Beneficios a los Empleados', 'eeff_type': '3.1'},
            {'id': 14, 'id_parent': 20, 'sequence': 40, 'code': '1D0310', 'description': 'Otras provisiones', 'eeff_type': '3.1'},
            {'id': 15, 'id_parent': 20, 'sequence': 41, 'code': '1D0311', 'description': 'Pasivos por Impuestos a las Ganancias', 'eeff_type': '3.1'},
            {'id': 16, 'id_parent': 20, 'sequence': 42, 'code': '1D0314', 'description': 'Otros Pasivos no financieros', 'eeff_type': '3.1'},
            {'id': 17, 'id_parent': 20, 'sequence': 43, 'code': '1D0315', 'description': 'Total de Pasivos Corrientes distintos de Pasivos incluidos en Grupos de Activos para su Disposición Clasificados como Mantenidos para la Venta', 'eeff_type': '3.1'},
            {'id': 18, 'id_parent': 21, 'sequence': 46, 'code': '1D0401', 'description': 'Otros Pasivos Financieros', 'eeff_type': '3.1'},
            {'id': 19, 'id_parent': 21, 'sequence': 47, 'code': '1D0411', 'description': 'Cuentas por pagar comerciales y otras cuentas por pagar', 'eeff_type': '3.1'},
            {'id': 20, 'id_parent': 21, 'sequence': 52, 'code': '1D0409', 'description': 'Provisión por Beneficios a los Empleados', 'eeff_type': '3.1'},
            {'id': 21, 'id_parent': 21, 'sequence': 53, 'code': '1D0406', 'description': 'Otras provisiones', 'eeff_type': '3.1'},
            {'id': 22, 'id_parent': 21, 'sequence': 54, 'code': '1D0404', 'description': 'Pasivos por impuestos diferidos', 'eeff_type': '3.1'},
            {'id': 23, 'id_parent': 21, 'sequence': 55, 'code': '1D0410', 'description': 'Otros pasivos no financieros', 'eeff_type': '3.1'},
            {'id': 24, 'id_parent': 29, 'sequence': 69, 'code': '2D02ST', 'description': 'Ganancia (Pérdida) Bruta', 'eeff_type': '3.20'},
            {'id': 25, 'id_parent': 29, 'sequence': 70, 'code': '2D0302', 'description': 'Gastos de Ventas y Distribución', 'eeff_type': '3.20'},
            {'id': 26, 'id_parent': 29, 'sequence': 71, 'code': '2D0301', 'description': 'Gastos de Administración', 'eeff_type': '3.20'},
            {'id': 27, 'id_parent': 29, 'sequence': 72, 'code': '2D0407', 'description': 'Ganancia (Pérdida) de la baja en Activos Financieros medidos al Costo Amortizado', 'eeff_type': '3.20'},
            {'id': 28, 'id_parent': 29, 'sequence': 73, 'code': '2D0403', 'description': 'Otros Ingresos Operativos', 'eeff_type': '3.20'},
            {'id': 29, 'id_parent': 29, 'sequence': 74, 'code': '2D0404', 'description': 'Otros Gastos Operativos', 'eeff_type': '3.20'},
            {'id': 30, 'id_parent': 29, 'sequence': 75, 'code': '2D0412', 'description': 'Otras ganancias (pérdidas)', 'eeff_type': '3.20'},
            {'id': 31, 'id_parent': 38, 'sequence': 162, 'code': '5D01ST', 'description': 'Otro Resultado Integral antes de Impuestos', 'eeff_type': '3.24'},
            {'id': 32, 'id_parent': 38, 'sequence': 163, 'code': '5D0202', 'description': 'Variación Neta por Coberturas del Flujo de Efectivo', 'eeff_type': '3.24'},
            {'id': 33, 'id_parent': 38, 'sequence': 164, 'code': '5D0208', 'description': 'Coberturas de inversión neta de negocios en el extranjero', 'eeff_type': '3.24'},
            {'id': 34, 'id_parent': 38, 'sequence': 165, 'code': '5D0203', 'description': 'Ganancias (Pérdidas) de Inversiones en Instrumentos de Patrimonio al valor razonable', 'eeff_type': '3.24'},
            {'id': 35, 'id_parent': 38, 'sequence': 166, 'code': '5D0204', 'description': 'Diferencia de Cambio por Conversión de Operaciones en el Extranjero', 'eeff_type': '3.24'},
            {'id': 36, 'id_parent': 38, 'sequence': 167, 'code': '5D0209', 'description': 'Variación neta de activos no corrientes o grupos de activos mantenidos para la venta', 'eeff_type': '3.24'},
            {'id': 37, 'id_parent': 38, 'sequence': 168, 'code': '5D0206', 'description': 'Superávit de Revaluación', 'eeff_type': '3.24'},
            {'id': 38, 'id_parent': 38, 'sequence': 169, 'code': '5D0210', 'description': 'Ganancia (pérdida) actuariales en plan de beneficios definidos', 'eeff_type': '3.24'},
            {'id': 39, 'id_parent': 38, 'sequence': 170, 'code': '5D0211', 'description': 'Cambios en el valor razonable de pasivos financieros atribuibles a cambios en el riesgo de crédito del pasivo', 'eeff_type': '3.24'},
            {'id': 40, 'id_parent': 39, 'sequence': 177, 'code': '4D0128', 'description': 'Saldo Inicial Reexpresado', 'eeff_type': '3.19'},
            {'id': 41, 'id_parent': 39, 'sequence': 178, 'code': '4D0129', 'description': 'Ganancia (Pérdida) Neta del Ejercicio', 'eeff_type': '3.19'},
            {'id': 42, 'id_parent': 39, 'sequence': 179, 'code': '4D0130', 'description': 'Otro Resultado Integral', 'eeff_type': '3.19'},
            {'id': 43, 'id_parent': 48, 'sequence': 194, 'code': '4D0228', 'description': 'Saldo Inicial Reexpresado', 'eeff_type': '3.19'},
            {'id': 44, 'id_parent': 48, 'sequence': 195, 'code': '4D0229', 'description': 'Ganancia (Pérdida) Neta del Ejercicio', 'eeff_type': '3.19'},
            {'id': 45, 'id_parent': 48, 'sequence': 196, 'code': '4D0230', 'description': 'Otro Resultado Integral', 'eeff_type': '3.19'},
            {'id': 46, 'id_parent': 57, 'sequence': 237, 'code': '3D01ST', 'description': 'Flujos de Efectivo y Equivalente al Efectivo Procedente de (Utilizados en) Actividades de Operación', 'eeff_type': '3.25'},
            {'id': 47, 'id_parent': 57, 'sequence': 238, 'code': '3D0220', 'description': 'Reembolso de Adelantos de Prestamos y Préstamos Concedidos a Terceros', 'eeff_type': '3.25'},
            {'id': 48, 'id_parent': 57, 'sequence': 239, 'code': '3D0218', 'description': 'Pérdida de control de subsidiarias u otros negocios', 'eeff_type': '3.25'},
            {'id': 49, 'id_parent': 57, 'sequence': 240, 'code': '3D0209', 'description': 'Reembolsos recibidos de préstamos a entidades relacionadas', 'eeff_type': '3.25'},
            {'id': 50, 'id_parent': 57, 'sequence': 241, 'code': '3D0201', 'description': 'Venta de Instrumentos Financieros de Patrimonio o Deuda de Otras Entidades', 'eeff_type': '3.25'},
            {'id': 51, 'id_parent': 57, 'sequence': 242, 'code': '3D0221', 'description': 'Contratos Derivados (futuro, a término, opciones)', 'eeff_type': '3.25'},
            {'id': 52, 'id_parent': 57, 'sequence': 243, 'code': '3D0222', 'description': 'Venta de Participaciones en Negocios Conjuntos, Neto del Efectivo Desapropiado', 'eeff_type': '3.25'},
            {'id': 53, 'id_parent': 57, 'sequence': 244, 'code': '3D0202', 'description': 'Venta de Propiedades, Planta y Equipo', 'eeff_type': '3.25'},
            {'id': 54, 'id_parent': 57, 'sequence': 245, 'code': '3D0203', 'description': 'Venta de Activos Intangibles', 'eeff_type': '3.25'},
            {'id': 55, 'id_parent': 57, 'sequence': 246, 'code': '3D0223', 'description': 'Venta de Otros Activos de largo plazo', 'eeff_type': '3.25'},
            {'id': 56, 'id_parent': 57, 'sequence': 247, 'code': '3D0231', 'description': 'Subvenciones del gobierno', 'eeff_type': '3.25'},
            {'id': 57, 'id_parent': 57, 'sequence': 248, 'code': '3D0210', 'description': 'Intereses Recibidos', 'eeff_type': '3.25'},
            {'id': 58, 'id_parent': 57, 'sequence': 249, 'code': '3D0211', 'description': 'Dividendos Recibidos', 'eeff_type': '3.25'},
            {'id': 59, 'id_parent': 57, 'sequence': 250, 'code': '3D0225', 'description': 'Anticipos y Prestamos Concedidos a Terceros', 'eeff_type': '3.25'},
            {'id': 60, 'id_parent': 57, 'sequence': 251, 'code': '3D0232', 'description': 'Obtener el control de subsidiarias u otros negocios', 'eeff_type': '3.25'},
            {'id': 61, 'id_parent': 57, 'sequence': 252, 'code': '3D0212', 'description': 'Prestamos concedidos a entidades relacionadas', 'eeff_type': '3.25'},
            {'id': 62, 'id_parent': 57, 'sequence': 253, 'code': '3D0205', 'description': 'Compra de Instrumentos Financieros de Patrimonio o Deuda de Otras Entidades', 'eeff_type': '3.25'},
            {'id': 63, 'id_parent': 57, 'sequence': 254, 'code': '3D0226', 'description': 'Contratos Derivados (futuro, a término, opciones)', 'eeff_type': '3.25'},
            {'id': 64, 'id_parent': 57, 'sequence': 255, 'code': '3D0219', 'description': 'Compra de Subsidiarias, Neto del Efectivo Adquirido', 'eeff_type': '3.25'},
            {'id': 65, 'id_parent': 57, 'sequence': 256, 'code': '3D0227', 'description': 'Compra de Participaciones en Negocios Conjuntos, Neto del Efectivo Adquirido', 'eeff_type': '3.25'},
            {'id': 66, 'id_parent': 57, 'sequence': 257, 'code': '3D0206', 'description': 'Compra de Propiedades, Planta y Equipo', 'eeff_type': '3.25'},
            {'id': 67, 'id_parent': 57, 'sequence': 258, 'code': '3D0207', 'description': 'Compra de Activos Intangibles', 'eeff_type': '3.25'},
            {'id': 68, 'id_parent': 57, 'sequence': 259, 'code': '3D0229', 'description': 'Compra de Otros Activos de largo plazo', 'eeff_type': '3.25'},
            {'id': 69, 'id_parent': 57, 'sequence': 260, 'code': '3D0233', 'description': 'Impuestos a las ganancias (pagados) reembolsados', 'eeff_type': '3.25'},
            {'id': 70, 'id_parent': 57, 'sequence': 261, 'code': '3D0234', 'description': 'Otros cobros (pagos) de efectivo relativos a la actividad de inversión', 'eeff_type': '3.25'}
        ]
        data_level_5 = [
            {'id': 1, 'id_parent': 12, 'sequence': 35, 'code': '1D0302', 'description': 'Cuentas por Pagar Comerciales', 'eeff_type': '3.1'},
            {'id': 2, 'id_parent': 12, 'sequence': 36, 'code': '1D0304', 'description': 'Otras Cuentas por Pagar', 'eeff_type': '3.1'},
            {'id': 3, 'id_parent': 12, 'sequence': 37, 'code': '1D0303', 'description': 'Cuentas por Pagar a Entidades Relacionadas', 'eeff_type': '3.1'},
            {'id': 4, 'id_parent': 12, 'sequence': 38, 'code': '1D0317', 'description': 'Ingresos diferidos', 'eeff_type': '3.1'},
            {'id': 5, 'id_parent': 12, 'sequence': 44, 'code': '1D0312', 'description': 'Pasivos incluidos en Grupos de Activos para su Disposición Clasificados como Mantenidos para la Venta', 'eeff_type': '3.1'},
            {'id': 6, 'id_parent': 19, 'sequence': 48, 'code': '1D0407', 'description': 'Cuentas por Pagar Comerciales', 'eeff_type': '3.1'},
            {'id': 7, 'id_parent': 19, 'sequence': 49, 'code': '1D0408', 'description': 'Otras Cuentas por Pagar', 'eeff_type': '3.1'},
            {'id': 8, 'id_parent': 19, 'sequence': 50, 'code': '1D0402', 'description': 'Cuentas por Pagar a Entidades Relacionadas', 'eeff_type': '3.1'},
            {'id': 9, 'id_parent': 19, 'sequence': 51, 'code': '1D0403', 'description': 'Ingresos Diferidos', 'eeff_type': '3.1'},
            {'id': 10, 'id_parent': 24, 'sequence': 67, 'code': '2D01ST', 'description': 'Ingresos de actividades ordinarias', 'eeff_type': '3.20'},
            {'id': 11, 'id_parent': 24, 'sequence': 68, 'code': '2D0201', 'description': 'Costo de Ventas', 'eeff_type': '3.20'},
            {'id': 12, 'id_parent': 31, 'sequence': 154, 'code': '5D0103', 'description': 'Variación Neta por Coberturas del Flujo de Efectivo', 'eeff_type': '3.24'},
            {'id': 13, 'id_parent': 31, 'sequence': 155, 'code': '5D0109', 'description': 'Coberturas de inversión neta de negocios en el extranjero', 'eeff_type': '3.24'},
            {'id': 14, 'id_parent': 31, 'sequence': 156, 'code': '5D0104', 'description': 'Ganancias (Pérdidas) de Inversiones en Instrumentos de Patrimonio al valor razonable', 'eeff_type': '3.24'},
            {'id': 15, 'id_parent': 31, 'sequence': 157, 'code': '5D0105', 'description': 'Diferencia de Cambio por Conversión de Operaciones en el Extranjero', 'eeff_type': '3.24'},
            {'id': 16, 'id_parent': 31, 'sequence': 158, 'code': '5D0110', 'description': 'Variación neta de activos no corrientes o grupos de activos mantenidos para la venta', 'eeff_type': '3.24'},
            {'id': 17, 'id_parent': 31, 'sequence': 159, 'code': '5D0107', 'description': 'Superávit de Revaluación', 'eeff_type': '3.24'},
            {'id': 18, 'id_parent': 31, 'sequence': 160, 'code': '5D0111', 'description': 'Ganancia (pérdida) actuariales en plan de beneficios definidos', 'eeff_type': '3.24'},
            {'id': 19, 'id_parent': 31, 'sequence': 161, 'code': '5D0112', 'description': 'Cambios en el valor razonable de pasivos financieros atribuibles a cambios en el riesgo de crédito del pasivo', 'eeff_type': '3.24'},
            {'id': 20, 'id_parent': 40, 'sequence': 174, 'code': '4D0101', 'description': 'Saldos al 1ero. de enero de', 'eeff_type': '3.19'},
            {'id': 21, 'id_parent': 40, 'sequence': 175, 'code': '4D0126', 'description': 'Cambios en Políticas Contables', 'eeff_type': '3.19'},
            {'id': 22, 'id_parent': 40, 'sequence': 176, 'code': '4D0127', 'description': 'Corrección de Errores', 'eeff_type': '3.19'},
            {'id': 23, 'id_parent': 43, 'sequence': 191, 'code': '4D0201', 'description': 'Saldos al 1ero. de enero de', 'eeff_type': '3.19'},
            {'id': 24, 'id_parent': 43, 'sequence': 192, 'code': '4D0226', 'description': 'Cambios en Políticas Contables', 'eeff_type': '3.19'},
            {'id': 25, 'id_parent': 43, 'sequence': 193, 'code': '4D0227', 'description': 'Corrección de Errores', 'eeff_type': '3.19'},
            {'id': 26, 'id_parent': 46, 'sequence': 222, 'code': '3D0608', 'description': 'Otros ajustes para conciliar la ganancia (pérdida) del ejercicio', 'eeff_type': '3.25'},
            {'id': 27, 'id_parent': 46, 'sequence': 223, 'code': '3D0835', 'description': '(Aumento) disminución de cuentas por cobrar comerciales y otras cuentas por cobrar', 'eeff_type': '3.25'},
            {'id': 28, 'id_parent': 46, 'sequence': 224, 'code': '3D0804', 'description': '(Aumento) Disminución en Inventarios', 'eeff_type': '3.25'},
            {'id': 29, 'id_parent': 46, 'sequence': 225, 'code': '3D0813', 'description': '(Aumento) Disminución en Activos Biológicos', 'eeff_type': '3.25'},
            {'id': 30, 'id_parent': 46, 'sequence': 226, 'code': '3D0818', 'description': '(Aumento) Disminución de otros activos no financieros', 'eeff_type': '3.25'},
            {'id': 31, 'id_parent': 46, 'sequence': 227, 'code': '3D0833', 'description': 'Aumento (disminución) de cuentas por pagar comerciales y otras cuentas por pagar', 'eeff_type': '3.25'},
            {'id': 32, 'id_parent': 46, 'sequence': 228, 'code': '3D0829', 'description': 'Aumento (Disminución) de Provisión por Beneficios a los Empleados', 'eeff_type': '3.25'},
            {'id': 33, 'id_parent': 46, 'sequence': 229, 'code': '3D0815', 'description': 'Aumento (Disminución) de Otras Provisiones', 'eeff_type': '3.25'},
            {'id': 34, 'id_parent': 46, 'sequence': 230, 'code': '3D0830', 'description': 'Total de ajustes por conciliación de ganancias (pérdidas)', 'eeff_type': '3.25'},
            {'id': 35, 'id_parent': 46, 'sequence': 231, 'code': '3D0121', 'description': 'Flujos de efectivo y equivalente al efectivo procedente de (utilizados en) operaciones', 'eeff_type': '3.25'},
            {'id': 36, 'id_parent': 46, 'sequence': 232, 'code': '3D0103', 'description': 'Intereses recibidos (no incluidos en la Actividad de Inversión)', 'eeff_type': '3.25'},
            {'id': 37, 'id_parent': 46, 'sequence': 233, 'code': '3D0107', 'description': 'Intereses pagados (no incluidos en la Actividad de Financiación)', 'eeff_type': '3.25'},
            {'id': 38, 'id_parent': 46, 'sequence': 234, 'code': '3D0111', 'description': 'Dividendos Recibidos (no incluidos en la Actividad de Inversión)', 'eeff_type': '3.25'},
            {'id': 39, 'id_parent': 46, 'sequence': 235, 'code': '3D0116', 'description': 'Dividendos pagados (no incluidos en la Actividad de Financiación)', 'eeff_type': '3.25'},
            {'id': 40, 'id_parent': 46, 'sequence': 236, 'code': '3D0120', 'description': 'Impuestos a las ganancias (pagados) reembolsados', 'eeff_type': '3.25'}
        ]
        data_level_6 = [
            {'id': 1, 'id_parent': 25, 'sequence': 209, 'code': '3D0611', 'description': 'Gasto por Intereses', 'eeff_type': '3.25'},
            {'id': 2, 'id_parent': 25, 'sequence': 210, 'code': '3D0627', 'description': 'Ingreso por Intereses', 'eeff_type': '3.25'},
            {'id': 3, 'id_parent': 25, 'sequence': 211, 'code': '3D0628', 'description': 'Ingreso por Dividendos', 'eeff_type': '3.25'},
            {'id': 4, 'id_parent': 25, 'sequence': 212, 'code': '3D0629', 'description': 'Pérdida (Ganancia) por Diferencias de Cambio no realizadas', 'eeff_type': '3.25'},
            {'id': 5, 'id_parent': 25, 'sequence': 213, 'code': '3D0620', 'description': 'Gasto por Impuestos a las Ganancias', 'eeff_type': '3.25'},
            {'id': 6, 'id_parent': 25, 'sequence': 214, 'code': '3D0610', 'description': 'Pérdidas por Deterioro de Valor (Reversiones de Pérdidas por Deterioro de Valor) reconocidas en el Resultado del Ejercicio', 'eeff_type': '3.25'},
            {'id': 7, 'id_parent': 25, 'sequence': 215, 'code': '3D0602', 'description': 'Depreciación, Amortización y Agotamiento', 'eeff_type': '3.25'},
            {'id': 8, 'id_parent': 25, 'sequence': 216, 'code': '3D0631', 'description': 'Pérdidas (Ganancias) por Valor Razonable', 'eeff_type': '3.25'},
            {'id': 9, 'id_parent': 25, 'sequence': 217, 'code': '3D0632', 'description': 'Pérdida (Ganancias) por la Disposición de Activos no Corrientes Mantenidas para la Venta', 'eeff_type': '3.25'},
            {'id': 10, 'id_parent': 25, 'sequence': 218, 'code': '3D0634', 'description': 'Diferencia entre el importe en libros de los activos distribuidos y el importe en libros del dividendo a pagar', 'eeff_type': '3.25'},
            {'id': 11, 'id_parent': 25, 'sequence': 219, 'code': '3D0635', 'description': 'Pérdida (ganancia) en venta de propiedades de inversión', 'eeff_type': '3.25'},
            {'id': 12, 'id_parent': 25, 'sequence': 220, 'code': '3D0605', 'description': 'Pérdida (Ganancia) en Venta de Propiedades, Planta y Equipo', 'eeff_type': '3.25'},
            {'id': 13, 'id_parent': 25, 'sequence': 221, 'code': '3D0618', 'description': 'Pérdida (Ganancia) en Venta de Activos Intangibles', 'eeff_type': '3.25'}
        ]
        
        for dict_level_1 in data_level_1:
            record_level_1 = self._create_record_if_not_exists(dict_level_1, False)

            for dict_level_2 in self._filter_data_by_parent_id(dict_level_1, data_level_2):
                record_level_2 = self._create_record_if_not_exists(dict_level_2, record_level_1)

                for dict_level_3 in self._filter_data_by_parent_id(dict_level_2, data_level_3):
                    record_level_3 = self._create_record_if_not_exists(dict_level_3, record_level_2)

                    for dict_level_4 in self._filter_data_by_parent_id(dict_level_3, data_level_4):
                        record_level_4 = self._create_record_if_not_exists(dict_level_4, record_level_3)

                        for dict_level_5 in self._filter_data_by_parent_id(dict_level_4, data_level_5):
                            record_level_5 = self._create_record_if_not_exists(dict_level_5, record_level_4)

                            for dict_level_6 in self._filter_data_by_parent_id(dict_level_5, data_level_6):
                                record_level_6 = self._create_record_if_not_exists(dict_level_6, record_level_5)
        
        dict_seq_98 = {'sequence': 98, 'code': '3D0121', 'description': 'Flujos de efectivo y equivalente al efectivo procedente de (utilizados en) operaciones', 'eeff_type': '3.18'}        
        record_seq_98 = self._create_record_if_not_exists(dict_seq_98, False)
        
        dict_seq_88 = {'sequence': 88, 'code': '3D0101', 'description': 'Venta de Bienes y Prestación de Servicios', 'eeff_type': '3.18'}
        dict_seq_89 = {'sequence': 89, 'code': '3D0112', 'description': 'Regalías, cuotas, comisiones, otros ingresos de actividades ordinarias', 'eeff_type': '3.18'}
        dict_seq_90 = {'sequence': 90, 'code': '3D0110', 'description': 'Contratos mantenidos con propósito de intermediación o para negociar', 'eeff_type': '3.18'}
        dict_seq_91 = {'sequence': 91, 'code': '3D0117', 'description': 'Arrendamiento y posterior venta de esos activos', 'eeff_type': '3.18'}
        dict_seq_92 = {'sequence': 92, 'code': '3D0104', 'description': 'Otros cobros de efectivo relativos a la actividad de operación', 'eeff_type': '3.18'}
        dict_seq_93 = {'sequence': 93, 'code': '3D0109', 'description': 'Proveedores de Bienes y Servicios', 'eeff_type': '3.18'}
        dict_seq_94 = {'sequence': 94, 'code': '3D0118', 'description': 'Contratos mantenidos con propósito de intermediación o para negociar', 'eeff_type': '3.18'}
        dict_seq_95 = {'sequence': 95, 'code': '3D0105', 'description': 'Pagos a y por cuenta de los empleados', 'eeff_type': '3.18'}
        dict_seq_96 = {'sequence': 96, 'code': '3D0119', 'description': 'Elaboración o adquisición de activos para arrendar y otros mantenidos para la venta', 'eeff_type': '3.18'}
        dict_seq_97 = {'sequence': 97, 'code': '3D0108', 'description': 'Otros Pagos de Efectivo Relativos a la Actividad de Operación', 'eeff_type': '3.18'}
        record_seq_88 = self._create_record_if_not_exists(dict_seq_88, record_seq_98)
        record_seq_89 = self._create_record_if_not_exists(dict_seq_89, record_seq_98)
        record_seq_90 = self._create_record_if_not_exists(dict_seq_90, record_seq_98)
        record_seq_91 = self._create_record_if_not_exists(dict_seq_91, record_seq_98)
        record_seq_92 = self._create_record_if_not_exists(dict_seq_92, record_seq_98)
        record_seq_93 = self._create_record_if_not_exists(dict_seq_93, record_seq_98)
        record_seq_94 = self._create_record_if_not_exists(dict_seq_94, record_seq_98)
        record_seq_95 = self._create_record_if_not_exists(dict_seq_95, record_seq_98)
        record_seq_96 = self._create_record_if_not_exists(dict_seq_96, record_seq_98)
        record_seq_97 = self._create_record_if_not_exists(dict_seq_97, record_seq_98)
        
        dict_seq_130 = {'sequence': 130, 'code': '3D02ST', 'description': 'Flujos de Efectivo y Equivalente al Efectivo Procedente de (Utilizados en) Actividades de Inversión', 'eeff_type': '3.18'}
        record_seq_130 = self._create_record_if_not_exists(dict_seq_130, False)
        
        dict_seq_106 = {'sequence': 106, 'code': '3D0220', 'description': 'Reembolso de Adelantos de Prestamos y Préstamos Concedidos a Terceros', 'eeff_type': '3.18'}
        dict_seq_107 = {'sequence': 107, 'code': '3D0218', 'description': 'Pérdida de control de subsidiarias u otros negocios', 'eeff_type': '3.18'}
        dict_seq_108 = {'sequence': 108, 'code': '3D0209', 'description': 'Reembolsos recibidos de préstamos a entidades relacionadas', 'eeff_type': '3.18'}
        dict_seq_109 = {'sequence': 109, 'code': '3D0201', 'description': 'Venta de Instrumentos Financieros de Patrimonio o Deuda de Otras Entidades', 'eeff_type': '3.18'}
        dict_seq_110 = {'sequence': 110, 'code': '3D0221', 'description': 'Contratos Derivados (futuro, a término, opciones)', 'eeff_type': '3.18'}
        dict_seq_111 = {'sequence': 111, 'code': '3D0222', 'description': 'Venta de Participaciones en Negocios Conjuntos, Neto del Efectivo Desapropiado', 'eeff_type': '3.18'}
        dict_seq_112 = {'sequence': 112, 'code': '3D0202', 'description': 'Venta de Propiedades, Planta y Equipo', 'eeff_type': '3.18'}
        dict_seq_113 = {'sequence': 113, 'code': '3D0203', 'description': 'Venta de Activos Intangibles', 'eeff_type': '3.18'}
        dict_seq_114 = {'sequence': 114, 'code': '3D0223', 'description': 'Venta de Otros Activos de largo plazo', 'eeff_type': '3.18'}
        dict_seq_115 = {'sequence': 115, 'code': '3D0231', 'description': 'Subvenciones del gobierno', 'eeff_type': '3.18'}
        dict_seq_116 = {'sequence': 116, 'code': '3D0210', 'description': 'Intereses Recibidos', 'eeff_type': '3.18'}
        dict_seq_117 = {'sequence': 117, 'code': '3D0211', 'description': 'Dividendos Recibidos', 'eeff_type': '3.18'}
        dict_seq_118 = {'sequence': 118, 'code': '3D0225', 'description': 'Anticipos y Prestamos Concedidos a Terceros', 'eeff_type': '3.18'}
        dict_seq_119 = {'sequence': 119, 'code': '3D0232', 'description': 'Obtener el control de subsidiarias u otros negocios', 'eeff_type': '3.18'}
        dict_seq_120 = {'sequence': 120, 'code': '3D0212', 'description': 'Prestamos concedidos a entidades relacionadas', 'eeff_type': '3.18'}
        dict_seq_121 = {'sequence': 121, 'code': '3D0205', 'description': 'Compra de Instrumentos Financieros de Patrimonio o Deuda de Otras Entidades', 'eeff_type': '3.18'}
        dict_seq_122 = {'sequence': 122, 'code': '3D0226', 'description': 'Contratos Derivados (futuro, a término, opciones)', 'eeff_type': '3.18'}
        dict_seq_123 = {'sequence': 123, 'code': '3D0219', 'description': 'Compra de Subsidiarias, Neto del Efectivo Adquirido', 'eeff_type': '3.18'}
        dict_seq_124 = {'sequence': 124, 'code': '3D0227', 'description': 'Compra de Participaciones en Negocios Conjuntos, Neto del Efectivo Adquirido', 'eeff_type': '3.18'}
        dict_seq_125 = {'sequence': 125, 'code': '3D0206', 'description': 'Compra de Propiedades, Planta y Equipo', 'eeff_type': '3.18'}
        dict_seq_126 = {'sequence': 126, 'code': '3D0207', 'description': 'Compra de Activos Intangibles', 'eeff_type': '3.18'}
        dict_seq_127 = {'sequence': 127, 'code': '3D0229', 'description': 'Compra de Otros Activos de largo plazo', 'eeff_type': '3.18'}
        dict_seq_128 = {'sequence': 128, 'code': '3D0233', 'description': 'Impuestos a las ganancias (pagados) reembolsados', 'eeff_type': '3.18'}
        dict_seq_129 = {'sequence': 129, 'code': '3D0234', 'description': 'Otros cobros (pagos) de efectivo relativos a la actividad de inversión', 'eeff_type': '3.18'}
        record_seq_106 = self._create_record_if_not_exists(dict_seq_106, record_seq_130)
        record_seq_107 = self._create_record_if_not_exists(dict_seq_107, record_seq_130)
        record_seq_108 = self._create_record_if_not_exists(dict_seq_108, record_seq_130)
        record_seq_109 = self._create_record_if_not_exists(dict_seq_109, record_seq_130)
        record_seq_110 = self._create_record_if_not_exists(dict_seq_110, record_seq_130)
        record_seq_111 = self._create_record_if_not_exists(dict_seq_111, record_seq_130)
        record_seq_112 = self._create_record_if_not_exists(dict_seq_112, record_seq_130)
        record_seq_113 = self._create_record_if_not_exists(dict_seq_113, record_seq_130)
        record_seq_114 = self._create_record_if_not_exists(dict_seq_114, record_seq_130)
        record_seq_115 = self._create_record_if_not_exists(dict_seq_115, record_seq_130)
        record_seq_116 = self._create_record_if_not_exists(dict_seq_116, record_seq_130)
        record_seq_117 = self._create_record_if_not_exists(dict_seq_117, record_seq_130)
        record_seq_118 = self._create_record_if_not_exists(dict_seq_118, record_seq_130)
        record_seq_119 = self._create_record_if_not_exists(dict_seq_119, record_seq_130)
        record_seq_120 = self._create_record_if_not_exists(dict_seq_120, record_seq_130)
        record_seq_121 = self._create_record_if_not_exists(dict_seq_121, record_seq_130)
        record_seq_122 = self._create_record_if_not_exists(dict_seq_122, record_seq_130)
        record_seq_123 = self._create_record_if_not_exists(dict_seq_123, record_seq_130)
        record_seq_124 = self._create_record_if_not_exists(dict_seq_124, record_seq_130)
        record_seq_125 = self._create_record_if_not_exists(dict_seq_125, record_seq_130)
        record_seq_126 = self._create_record_if_not_exists(dict_seq_126, record_seq_130)
        record_seq_127 = self._create_record_if_not_exists(dict_seq_127, record_seq_130)
        record_seq_128 = self._create_record_if_not_exists(dict_seq_128, record_seq_130)
        record_seq_129 = self._create_record_if_not_exists(dict_seq_129, record_seq_130)

        dict_seq_147 = {'sequence': 147, 'code': '3D03ST', 'description': 'Flujos de Efectivo y Equivalente al Efectivo Procedente de (Utilizados en) Actividades de Financiación', 'eeff_type': '3.18'}
        record_seq_147 = self._create_record_if_not_exists(dict_seq_147, False)
        
        dict_seq_131 = {'sequence': 131, 'code': '3D0325', 'description': 'Obtención de Préstamos', 'eeff_type': '3.18'}
        dict_seq_132 = {'sequence': 132, 'code': '3D0319', 'description': 'Préstamos de entidades relacionadas', 'eeff_type': '3.18'}
        dict_seq_133 = {'sequence': 133, 'code': '3D0326', 'description': 'Cambios en las participaciones en la propiedad de subsidiarias que no resultan en pérdida de control', 'eeff_type': '3.18'}
        dict_seq_134 = {'sequence': 134, 'code': '3D0327', 'description': 'Emisión de Acciones', 'eeff_type': '3.18'}
        dict_seq_135 = {'sequence': 135, 'code': '3D0328', 'description': 'Emisión de Otros Instrumentos de Patrimonio', 'eeff_type': '3.18'}
        dict_seq_136 = {'sequence': 136, 'code': '3D0329', 'description': 'Subvenciones del gobierno', 'eeff_type': '3.18'}
        dict_seq_137 = {'sequence': 137, 'code': '3D0330', 'description': 'Amortización o pago de Préstamos', 'eeff_type': '3.18'}
        dict_seq_138 = {'sequence': 138, 'code': '3D0322', 'description': 'Pasivos por Arrendamiento Financiero', 'eeff_type': '3.18'}
        dict_seq_139 = {'sequence': 139, 'code': '3D0321', 'description': 'Préstamos de entidades relacionadas', 'eeff_type': '3.18'}
        dict_seq_140 = {'sequence': 140, 'code': '3D0331', 'description': 'Cambios en las participaciones en la propiedad de subsidiarias que no resultan en pérdida de control', 'eeff_type': '3.18'}
        dict_seq_141 = {'sequence': 141, 'code': '3D0310', 'description': 'Recompra o Rescate de Acciones de la Entidad (Acciones en Cartera)', 'eeff_type': '3.18'}
        dict_seq_142 = {'sequence': 142, 'code': '3D0323', 'description': 'Adquisición de Otras Participaciones en el Patrimonio', 'eeff_type': '3.18'}
        dict_seq_143 = {'sequence': 143, 'code': '3D0311', 'description': 'Intereses pagados', 'eeff_type': '3.18'}
        dict_seq_144 = {'sequence': 144, 'code': '3D0305', 'description': 'Dividendos pagados', 'eeff_type': '3.18'}
        dict_seq_145 = {'sequence': 145, 'code': '3D0332', 'description': 'Impuestos a las ganancias (pagados) reembolsados', 'eeff_type': '3.18'}
        dict_seq_146 = {'sequence': 146, 'code': '3D0333', 'description': 'Otros cobros (pagos) de efectivo relativos a la actividad de financiación', 'eeff_type': '3.18'}
        dict_seq_148 = {'sequence': 148, 'code': '3D0401', 'description': 'Aumento (Disminución) Neto de Efectivo y Equivalente al Efectivo, antes de las Variaciones en las Tasas de Cambio', 'eeff_type': '3.18'}
        record_seq_131 = self._create_record_if_not_exists(dict_seq_131, record_seq_147)
        record_seq_132 = self._create_record_if_not_exists(dict_seq_132, record_seq_147)
        record_seq_133 = self._create_record_if_not_exists(dict_seq_133, record_seq_147)
        record_seq_134 = self._create_record_if_not_exists(dict_seq_134, record_seq_147)
        record_seq_135 = self._create_record_if_not_exists(dict_seq_135, record_seq_147)
        record_seq_136 = self._create_record_if_not_exists(dict_seq_136, record_seq_147)
        record_seq_137 = self._create_record_if_not_exists(dict_seq_137, record_seq_147)
        record_seq_138 = self._create_record_if_not_exists(dict_seq_138, record_seq_147)
        record_seq_139 = self._create_record_if_not_exists(dict_seq_139, record_seq_147)
        record_seq_140 = self._create_record_if_not_exists(dict_seq_140, record_seq_147)
        record_seq_141 = self._create_record_if_not_exists(dict_seq_141, record_seq_147)
        record_seq_142 = self._create_record_if_not_exists(dict_seq_142, record_seq_147)
        record_seq_143 = self._create_record_if_not_exists(dict_seq_143, record_seq_147)
        record_seq_144 = self._create_record_if_not_exists(dict_seq_144, record_seq_147)
        record_seq_145 = self._create_record_if_not_exists(dict_seq_145, record_seq_147)
        record_seq_146 = self._create_record_if_not_exists(dict_seq_146, record_seq_147)
        record_seq_148 = self._create_record_if_not_exists(dict_seq_148, record_seq_147)
        
        dict_seq_105 = {'sequence': 105, 'code': '3D01ST', 'description': 'Flujos de Efectivo y Equivalente al Efectivo Procedente de (Utilizados en) Actividades de Operación', 'eeff_type': '3.18'}
        record_seq_105 = self._create_record_if_not_exists(dict_seq_105, False)
        
        dict_seq_99 = {'sequence': 99, 'code': '3D0103', 'description': 'Intereses recibidos (no incluidos en la Actividad de Inversión)', 'eeff_type': '3.18'}
        dict_seq_100 = {'sequence': 100, 'code': '3D0107', 'description': 'Intereses pagados (no incluidos en la Actividad de Financiación)', 'eeff_type': '3.18'}
        dict_seq_101 = {'sequence': 101, 'code': '3D0111', 'description': 'Dividendos Recibidos (no incluidos en la Actividad de Inversión)', 'eeff_type': '3.18'}
        dict_seq_102 = {'sequence': 102, 'code': '3D0116', 'description': 'Dividendos pagados(no incluidos en la Actividad de Financiación)', 'eeff_type': '3.18'}
        dict_seq_103 = {'sequence': 103, 'code': '3D0120', 'description': 'Impuestos a las ganancias (pagados) reembolsados', 'eeff_type': '3.18'}
        dict_seq_104 = {'sequence': 104, 'code': '3D0122', 'description': 'Otros cobros (pagos) de efectivo', 'eeff_type': '3.18'}
        record_seq_99 = self._create_record_if_not_exists(dict_seq_99, record_seq_105)
        record_seq_100 = self._create_record_if_not_exists(dict_seq_100, record_seq_105)
        record_seq_101 = self._create_record_if_not_exists(dict_seq_101, record_seq_105)
        record_seq_102 = self._create_record_if_not_exists(dict_seq_102, record_seq_105)
        record_seq_103 = self._create_record_if_not_exists(dict_seq_103, record_seq_105)
        record_seq_104 = self._create_record_if_not_exists(dict_seq_104, record_seq_105)
        
        if not record_seq_98.parent_ids:
            record_seq_98.write({
                'parent_ids': [(4, record_seq_105.id)]
            })
        
        if not record_seq_130.parent_ids:
            record_seq_130.write({
                'parent_ids': [(4, record_seq_148.id)]
            })
        
        if not record_seq_147.parent_ids:
            record_seq_147.write({
                'parent_ids': [(4, record_seq_148.id)]
            })
            
        if not record_seq_105.parent_ids:
            record_seq_105.write({
                'parent_ids': [(4, record_seq_148.id)]
            })

    def _create_record_if_not_exists(self, data, rec):
        domain = [
            ('code', '=', data['code']),
            ('description', '=', data['description']),
            ('eeff_type', '=', data['eeff_type'])
        ]
        record = self.search(domain, limit=1)

        if record:
            if not record.parent_ids and rec:
                record.write({'parent_ids': [(4, rec.id)]})
        else:
            vals = {
                'sequence': data['sequence'],
                'code': data['code'],
                'description': data['description'],
                'eeff_type': data['eeff_type']
            }
            if rec:
                vals['parent_ids'] = [(4, rec.id)]
            record = self.create(vals)

        return record

    def _filter_data_by_parent_id(self, dictionary, data):
        return list(filter(lambda dict: dict['id_parent'] == dictionary['id'], data))


class AccountAccount(models.Model):
    _inherit = 'account.account'

    eeff_ple_id = fields.Many2one(
        string='3.1 Rubro ESF',
        comodel_name='eeff.ple'
    )
    eeff_type = fields.Selection(
        string='Tipo EEFF PLE',
        related='eeff_ple_id.eeff_type'
    )
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    eeff_ple_id = fields.Many2one(
        string='3.1 Rubro ESF',
        comodel_name='eeff.ple',
        related='account_id.eeff_ple_id',
        store=True
    )
