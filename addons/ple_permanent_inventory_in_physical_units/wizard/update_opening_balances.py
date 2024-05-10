from odoo import models, fields


class UpdateOpeningWizard(models.TransientModel):
    _name = 'update.opening.wizard'
    _description = 'update opening wizard'
    borrower_id = fields.Many2one('ple.permanent.inventory.physical.units', string='Inventario Valorizado')

    def update_opening_balances(self):
        to_id = (self.env.context.get('default_permanent_id')).get('default_permanent_id')
        ple_permanent_inventory = self.env['ple.permanent.inventory.physical.units'].search([('id', '=', to_id)])
        from_balances = dict()
        list_from_balances = list()
        for datos in self.borrower_id.list_val_unit_final:
            list_from_balances.append(datos.product_id)
            from_balances[datos.product_id] = {}
            from_balances[datos.product_id]['product_valuation'] = datos.product_valuation
            from_balances[datos.product_id]['quantity_product_hand'] = datos.quantity_product_hand
            from_balances[datos.product_id]['udm_product'] = datos.udm_product
            from_balances[datos.product_id]['standard_price'] = datos.standard_price
            from_balances[datos.product_id]['code_exist'] = datos.code_exist
            from_balances[datos.product_id]['correct_name'] = datos.product_valuation
        ple_permanent_inventory.write({
            'list_val_units': [(5, 0, 0)],
        })
        for rec in from_balances.keys():
            res = from_balances.get(rec)
            ple_permanent_inventory.write({
                'list_val_units': [
                    (0, 0, {'product_id': rec,
                            'product_valuation': res['product_valuation'],
                            'quantity_product_hand': res['quantity_product_hand'],
                            'udm_product': res['udm_product'],
                            'standard_price': res['standard_price'],
                            'code_exist': res['code_exist'],
                            }),
                ]
            })


    def update_opening_balances_2(self):
        to_id = (self.env.context.get('default_permanent_id')).get('default_permanent_id')
        ple_permanent_inventory = self.env['ple.permanent.inventory.physical.units'].search([('id', '=', to_id)])

        for a in self.borrower_id.list_val_unit_final:
            for b in ple_permanent_inventory.list_val_units:
                if a.product_id == b.product_id:
                    if a.standard_price != b.standard_price:
                        b.standard_price = a.standard_price
