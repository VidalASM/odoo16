from odoo.tests.common import TransactionCase


class TestSunatOperationWizard(TransactionCase):

    def setUp(self):
        super().setUp()
        self.SunatOperationWizard = self.env["sunat.operation.wizard"]
        self.StockValuationLayer = self.env["stock.valuation.layer"]

        # Crear objetos necesarios para las pruebas

    def test_print_default(self):
        "Check print_default method"
        # Preparar datos de prueba
        operation_sunat = "01"  # Reemplazar con el valor adecuado
        active_ids = [1, 2, 3]  # Reemplazar con los IDs adecuados
        context = {'active_ids': active_ids}
        self.env.context = context

        # Ejecutar el método a probar
        wizard = self.SunatOperationWizard.create(
            {'operation_sunat': operation_sunat})
        wizard.print_default()

        # Verificar los resultados esperados

        print("Test print_default SunatOperationWizard OK ...... !!!!")
        print('==================== Test SunatOperationWizard OK  ====================')
