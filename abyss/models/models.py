# -*- coding: utf-8 -*-
from odoo import models, fields, api
import random, datetime
from odoo.exceptions import ValidationError


class Player(models.Model):
    _name = 'abyss.player'
    _description = 'abyss.player'

    name = fields.Char()
    description = fields.Text()
    image = fields.Image(max_width=200)
    age = fields.Integer(readonly=True, compute='_get_age')
    birth_date = fields.Date()
    player_created = fields.Datetime(default=lambda t: fields.Datetime.now())
    success = fields.Boolean(readonly=True)

    abyss_character = fields.Many2many('abyss.character', string="Characters")

    @api.depends('birth_date')
    def _get_age(self):
        for record in self:
            if record.birth_date:
                birth_date = fields.Datetime.from_string(record.birth_date)
                today = fields.Date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                record.age = age
            else:
                record.age = 0


class Character(models.Model):
    _name = 'abyss.character'
    _description = 'abyss.character'

    name = fields.Char()
    description = fields.Text()
    type = fields.Selection(
        [('1', 'Hydro'), ('2', 'Pyro'), ('3', 'Electro'), ('4', 'Geo'), ('5', 'Anemo'), ('6', 'Cryo'), ('7', 'Dendro')])
    stars = fields.Selection([('1', '4*'), ('2', '5*')])
    image = fields.Image(max_width=200)

    abyss_players = fields.Many2many('abyss.player', string="Players")
