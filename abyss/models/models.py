# -*- coding: utf-8 -*-

from odoo import models, fields, api
import random, datetime
from odoo.exceptions import ValidationError


class Player(models.Model):
    _name = 'abyss.player'
    _description = 'abyss.player'

    name = fields.Char()
    level = fields.Integer(default=1)
    experience = fields.Integer(default=0)
    money = fields.Float("Money", default=0.0)
    description = fields.Text()
    image = fields.Image(max_width=200)
    small_image = fields.Image(max_width=50, max_height=50, related='image', store=True)
    age = fields.Integer(readonly=True, compute='_get_age')
    birth_date = fields.Date()
    player_created = fields.Datetime(default=lambda t: fields.Datetime.now())
    success = fields.Boolean(readonly=True)

    weapons = fields.Many2many(
        'abyss.weapon',
        string="Weapons",
        widget="many2many_tags",
        domain="[('required_level', '<=', level)]"
    )
    enemies = fields.Many2many('abyss.enemy', string="Enemies")
    characters = fields.Many2many('abyss.character', string="Characters")

    @api.constrains('experience')
    def _check_level_up(self):
        for player in self:
            if player.experience >= 100 * player.level:
                player.level += 1

    def gain_experience(self, amount):
        self.experience += amount

    @api.onchange('weapons')
    def _onchange_weapons(self):
        if self.weapons:
            new_weapon_cost = self.weapons[-1].cost
            remaining_money = self.money - new_weapon_cost

            if remaining_money < 0:
                raise ValidationError("No tienes suficiente dinero para comprar esta arma")

            self.write({'money': remaining_money})

        elif not self.weapons:
            pass

    @api.onchange('characters')
    def _onchange_characters(self):
        for character in self.characters:
            if character.weapon_type and not any(weapon.type == character.weapon_type for weapon in self.weapons):
                raise ValidationError("No tienes un arma del tipo necesario para este personaje.")


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
    element_type = fields.Selection([
        ('Hydro', 'Hydro'),
        ('Pyro', 'Pyro'),
        ('Electro', 'Electro'),
        ('Geo', 'Geo'),
        ('Anemo', 'Anemo'),
        ('Cryo', 'Cryo'),
        ('Dendro', 'Dendro')
    ])
    weapon_type = fields.Selection([
        ('Sword', 'Sword'),
        ('Claymore', 'Claymore'),
        ('Bow', 'Bow'),
        ('Catalyst', 'Catalyst'),
        ('Polearm', 'Polearm')
    ])
    stars = fields.Selection([('4', '4*'), ('5', '5*')])
    health = fields.Integer()
    is_dead = fields.Boolean(default=False, readonly=True)
    small_image = fields.Image(max_width=50, max_height=50, related='image', store=True)
    image = fields.Image(max_width=200)
    level = fields.Integer(default=1)

    abyss_players = fields.Many2many('abyss.player', string="Players")
    enemies = fields.Many2many('abyss.enemy', string="Enemies")


    @api.onchange('vida_actual')
    def _onchange_goal(self):
            if self.muerto <= 0:
                self.muerto = 1

    is_immune = fields.Boolean(default=False, compute='_compute_immunity', store=True)

    @api.depends('element_type', 'abyss_players.enemies')
    def _compute_immunity(self):
        for character in self:
            character.is_immune = any(
                enemy.element_type == character.element_type for player in character.abyss_players for enemy in
                player.enemies
            )


class Weapon(models.Model):
    _name = 'abyss.weapon'
    _description = 'abyss.weapon'

    name = fields.Char()
    cost = fields.Float(default=0.0)
    weapon_type = fields.Selection([('Sword', 'Sword'), ('Claymore', 'Claymore'), ('Bow', 'Bow'), ('Catalyst', 'Catalyst'), ('Polearm', 'Polearm')])
    damage = fields.Integer()
    small_image = fields.Image(max_width=50, max_height=50, related='image', store=True)
    required_level = fields.Integer(default=1)
    image = fields.Image(max_width=200)


class Enemy(models.Model):
    _name = 'abyss.enemy'
    _description = 'abyss.enemy'

    name = fields.Char()
    element_type = fields.Selection([
        ('Hydro', 'Hydro'),
        ('Pyro', 'Pyro'),
        ('Electro', 'Electro'),
        ('Geo', 'Geo'),
        ('Anemo', 'Anemo'),
        ('Cryo', 'Cryo'),
        ('Dendro', 'Dendro')
    ])
    health = fields.Integer()
    damage = fields.Integer()
    small_image = fields.Image(max_width=50, max_height=50, related='image', store=True)
    energy = fields.Integer()
    image = fields.Image(max_width=200)

    @api.constrains('element_type')
    def _check_valid_element(self):
        valid_elements = ['Hydro', 'Pyro', 'Electro', 'Geo', 'Anemo', 'Cryo', 'Dendro']
        if self.element_type not in valid_elements:
            raise ValidationError("El enemigo es inmune al elemento del personaje")

    @api.constrains('energy')
    def _check_energy(self):
        if self.energy <= 0:
            raise ValidationError("El enemigo no tiene energia")