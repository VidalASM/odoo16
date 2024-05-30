from odoo.exceptions import AccessError
from odoo.tests import common


class TestIgvAfectationType(common.TransactionCase):

    def setUp(self):
        super(TestIgvAfectationType, self).setUp()
        self.model_igv_afectation_type = self.env['igv.afectation.type']
        self.model_users = self.env['res.users']

    def create_igv_afectation_type(self, code, descrition):
        igv_type = self.model_igv_afectation_type.create({
            'code': code,
            'description': descrition
        })
        return igv_type

    def create_users_by_group(self, groups, nro_user):
        user = self.model_users.create({
            'login': 'test_user%d' % nro_user,
            'name': 'Usuario%d - T' % nro_user,
            'email': 'usert%d@example.com' % nro_user,
            'notification_type': 'email',
            'groups_id': [(6, 0, groups)]
        })
        return user

    def test_01_create_igv_afectation_type(self):
        igv_type_1 = self.create_igv_afectation_type(100, 'Gravado - Test')
        self.assertTrue(igv_type_1)
        print('------------TEST OK - CREATE------------')

    def test_02_igv_afectation_type_permissions(self):
        document = self.create_igv_afectation_type(100, 'Gravado - Test')
        group_account_invoice = self.env.ref('account.group_account_invoice')
        group_account_user = self.env.ref('account.group_account_user')
        group_account_manager = self.env.ref('account.group_account_manager')

        # set a different user(account role) to prove permissions
        invoice_account = self.create_users_by_group([group_account_invoice.id], 1)
        user_account = self.create_users_by_group([group_account_user.id], 2)
        manager_account = self.create_users_by_group([group_account_manager.id], 3)
        normal_account = self.create_users_by_group([], 4)

        # invoice_account user
        # should do
        document.with_user(invoice_account).read()
        # shouldn't do
        self.assertRaises(AccessError, document.with_user(invoice_account).write,
                          {'description': 'prueba - invoice account'})
        self.assertRaises(AccessError, document.with_user(invoice_account).unlink)

        print('------------TEST OK - INVOICE ACCOUNT------------')

        document = self.create_igv_afectation_type(100, 'Gravado - Test')

        # user_account user
        # should do
        document.with_user(user_account).read()
        document.with_user(user_account).write({'description': 'prueba - user account'})
        document.with_user(user_account).unlink()

        print('------------TEST OK - USER ACCOUNT------------')

        document = self.create_igv_afectation_type(100, 'Gravado - Test')

        # user_account user
        # should do
        document.with_user(manager_account).read()
        document.with_user(manager_account).write({'description': 'prueba - manager account'})
        document.with_user(manager_account).unlink()

        print('------------TEST OK - USER ACCOUNT------------')

        # role different from account
        # should do
        document.with_user(normal_account).read()
        # shouldn't do
        self.assertRaises(AccessError, document.with_user(normal_account).write,
                          {'description': 'prueba - normal', 'code': 'ccc'})
        self.assertRaises(AccessError, document.with_user(normal_account).unlink)

        print('------------TEST OK - NORMAL USER------------')
