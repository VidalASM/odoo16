from odoo.exceptions import AccessError
from odoo.tests import common
from odoo.tests.common import Form


class TestDocumentType(common.TransactionCase):

    def setUp(self):
        super(TestDocumentType, self).setUp()
        self.document_type_model = self.env['l10n_latam.identification.type']
        self.res_users = self.env['res.users']

    def create_document_type(self, name, active):
        document = self.document_type_model.create({
            'name': name,
            'active': active
        })
        return document

    def create_res_users_by_group(self, groups, nro):
        user = self.res_users.create({
            'login': 'test_user%d' % nro,
            'name': 'Usuario%d - T' % nro,
            'email': 'usert%d@example.com' % nro,
            'notification_type': 'email',
            'groups_id': [(6, 0, groups)]
        })
        return user

    def test_01_create_document_type(self):
        document = self.create_document_type('DNI-prueba', True)
        self.assertTrue(document)
        print('------------TEST OK - CREATE------------')

    def test_02_sale_document_type_permissions(self):
        document = self.create_document_type('1-02', 'RUC-prueba', True)
        group_account_manager = self.env.ref('account.group_account_manager')
        group_contacts_conf = self.env.ref('base.group_system')

        # set a different user(account role) to prove permissions
        user_account = self.create_res_users_by_group([group_account_manager.id], 1)
        # should do
        document.with_user(user_account).read()
        # shouldn't do
        self.assertRaises(AccessError, document.with_user(user_account).write, {'name': 'prueba - account'})
        self.assertRaises(AccessError, document.with_user(user_account).unlink)
        print('------------TEST OK - USER ACCOUNT------------')

        # set a different user to prove permissions
        user = self.create_res_users_by_group([group_contacts_conf.id], 2)

        # should do
        document.with_user(user).read()
        document.with_user(user).write({'name': 'prueba - normal'})
        document.with_user(user).unlink()

        print('------------TEST OK - NORMAL USER------------')

    def test_03_create_partner_with_relation_document_type(self):
        document = self.create_document_type('1-02', 'RUC-prueba', True)
        document.update({
            'doc_length': 8,
            'doc_type': 'numeric',
            'exact_length': 'exact',
            'nationality': 'national'
        })
        partner_view = Form(
            self.env['res.partner'],
            view='base.view_partner_form'
        )
        partner_view.l10n_latam_identification_type_id = document
        partner_view.vat = '1234567sdsd9'
        self.assertTrue(partner_view.error_dialog)
        print('------------TEST OK - DOCUMENT TYPE VALIDATION | res.partner  ------------')
