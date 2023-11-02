# -*- coding: utf-8 -*-
# from odoo import http


# class Abyss(http.Controller):
#     @http.route('/abyss/abyss', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/abyss/abyss/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('abyss.listing', {
#             'root': '/abyss/abyss',
#             'objects': http.request.env['abyss.abyss'].search([]),
#         })

#     @http.route('/abyss/abyss/objects/<model("abyss.abyss"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('abyss.object', {
#             'object': obj
#         })
