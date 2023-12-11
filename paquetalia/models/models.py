# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class Furgoneta(models.Model):
    _name = 'paquetalia.furgoneta'

    matricula = fields.Char()
    capacitat = fields.Float()
    foto = fields.Image(max_width=200)
    enviaments = fields.One2many('paquetalia.viatge', 'furgoneta', string='Enviaments')

    paquets_enviats = fields.Many2many(
        'paquetalia.paquet',
        'furgoneta_paquet_rel',
        'furgoneta_id',
        'paquet_id',
        string='Paquets Enviats',
        compute='_compute_paquets_enviats'
    )

    @api.depends('enviaments.paquets')
    def _compute_paquets_enviats(self):
        for furgoneta in self:
            paquets_enviats = furgoneta.enviaments.mapped('paquets')
            furgoneta.paquets_enviats = [(6, 0, paquets_enviats.ids)]

    @api.constrains('capacitat')
    def check_capacitat(self):
        for furgoneta in self:
            if furgoneta.capacitat < 0:
                raise exceptions.ValidationError("La capacitat de la furgoneta no pot ser negativa.")


class Paquet(models.Model):
    _name = 'paquetalia.paquet'

    identificador = fields.Char()
    volum = fields.Float(default=0.0)


class Viatge(models.Model):
    _name = 'paquetalia.viatge'

    conductor = fields.Many2one('res.partner', string='Conductor')
    identificador = fields.Char()
    furgoneta = fields.Many2one('paquetalia.furgoneta', string='Furgoneta')
    paquets = fields.Many2many('paquetalia.paquet', string='Paquets')
    m3_aprofitats = fields.Float(compute='_compute_m3_aprofitats', store=True)

    @api.depends('paquets')
    def _compute_m3_aprofitats(self):
        for viatge in self:
            viatge.m3_aprofitats = sum(p.volum for p in viatge.paquets)

    @api.constrains('paquets')
    def check_paquets(self):
        for viatge in self:
            if len(viatge.paquets) > 0 and viatge.m3_aprofitats > viatge.furgoneta.capacitat:
                raise exceptions.ValidationError("La cantitat de paquets excedeix la capacitat de la furgoneta.")

            viatge.furgoneta.write({'paquets_enviats': [(4, paquet.id) for paquet in viatge.paquets]})

    def assign_furgoneta(self, furgoneta):
        for viatge in self:
            viatge.furgoneta = furgoneta




