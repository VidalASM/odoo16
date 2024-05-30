# -*- coding: utf-8 -*-
# from odoo import http


# class Server\addons(http.Controller):
#     @http.route('/server\addons/server\addons', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/server\addons/server\addons/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('server\addons.listing', {
#             'root': '/server\addons/server\addons',
#             'objects': http.request.env['server\addons.server\addons'].search([]),
#         })

#     @http.route('/server\addons/server\addons/objects/<model("server\addons.server\addons"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('server\addons.object', {
#             'object': obj
#         })
