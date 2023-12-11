# -*- coding: utf-8 -*-
# from odoo import http


# class Paquetalia(http.Controller):
#     @http.route('/paquetalia/paquetalia', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/paquetalia/paquetalia/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('paquetalia.listing', {
#             'root': '/paquetalia/paquetalia',
#             'objects': http.request.env['paquetalia.paquetalia'].search([]),
#         })

#     @http.route('/paquetalia/paquetalia/objects/<model("paquetalia.paquetalia"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('paquetalia.object', {
#             'object': obj
#         })
