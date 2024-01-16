# -*- coding: utf-8 -*-
# from odoo import http


# class AccountDetails(http.Controller):
#     @http.route('/account_details/account_details', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_details/account_details/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_details.listing', {
#             'root': '/account_details/account_details',
#             'objects': http.request.env['account_details.account_details'].search([]),
#         })

#     @http.route('/account_details/account_details/objects/<model("account_details.account_details"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_details.object', {
#             'object': obj
#         })
