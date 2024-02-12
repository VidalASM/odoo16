# -*- coding: utf-8 -*-
# from odoo import http


# class SaleQweb(http.Controller):
#     @http.route('/sale_qweb/sale_qweb', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_qweb/sale_qweb/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_qweb.listing', {
#             'root': '/sale_qweb/sale_qweb',
#             'objects': http.request.env['sale_qweb.sale_qweb'].search([]),
#         })

#     @http.route('/sale_qweb/sale_qweb/objects/<model("sale_qweb.sale_qweb"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_qweb.object', {
#             'object': obj
#         })
