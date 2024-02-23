# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, api
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
    characters = fields.Many2many('abyss.character', string="Characters", relation='player_character_rel')

    @api.model
    def update_player_experience(self):
        players = self.search([])
        for player in players:
            experience_gain = 10
            new_experience = player.experience + experience_gain

            while new_experience >= 100:
                new_experience -= 100
                player.write({'level': player.level + 1})

            player.write({'experience': new_experience})

        return True

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

    @api.onchange('characters', 'weapons')
    def _onchange_characters(self):
        for character in self.characters:
            if character.weapon_type and not any(
                    weapon.weapon_type == character.weapon_type for weapon in self.weapons):
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
    enemies = fields.Many2many('abyss.enemy', string="Enemies", relation='character_enemy_rel')

    @api.onchange('vida_actual')
    def _onchange_goal(self):
        if self.muerto <= 0:
            self.vida_actual = 1

    is_immune = fields.Boolean(default=False, compute='_compute_immunity', store=True)

    @api.depends('element_type', 'enemies')
    def _compute_immunity(self):
        for character in self:
            character.is_immune = any(
                enemy.element_type == character.element_type for enemy in character.enemies
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


class Battle(models.Model):
    _name = 'abyss.battle'
    _description = 'abyss.battle'

    name = fields.Char(string="Nombre de la Batalla", required=True, help="Nombre de la Batalla")
    description = fields.Text(string="Descripción de la Batalla", help="Descripción de la Batalla")
    fecha_batalla = fields.Date(string="Fecha de la Batalla")
    attack = fields.Many2many('abyss.player', string="Atacantes", relation='battle_attack_rel', column1='battle_id', column2='player_id')
    defend = fields.Many2many('abyss.enemy', string="Defensores", relation='battle_defend_rel', column1='battle_id', column2='enemy_id')

    state = fields.Selection([('1', 'Creation'), ('2', 'Character Selection'), ('3', 'Waiting'),
                              ('4', 'Finished')], required=True, compute='_get_state')
    time_left = fields.Char(compute='_get_state')

    winner = fields.Many2one('abyss.player', string="Ganador de la última batalla", ondelete='set null')

    date = fields.Datetime(default=lambda self: fields.Datetime.now() + timedelta(hours=3))
    finished = fields.Boolean()

    battle_start_time = fields.Datetime()

    def _get_state(self):
        for battle in self:
            if not battle.finished:
                if not battle.attack or not battle.defend:
                    battle.state = '1'
                    battle.time_left = ''
                elif battle.state == '1':
                    battle.state = '2'
                    battle.time_left = ''
                elif battle.state == '2':
                    battle.state = '3'
                    battle.time_left = ''
                elif battle.state == '3':
                    elapsed_time = fields.Datetime.now() - fields.Datetime.from_string(battle.battle_start_time)
                    max_battle_duration = 10

                    if elapsed_time.total_seconds() / 60 < max_battle_duration:
                        battle.state = '3'
                        battle.time_left = f"{int(max_battle_duration - elapsed_time.total_seconds() / 60)} minutos"
                    else:
                        battle.state = '4'
                        battle.time_left = 'Tiempo agotado'
                elif battle.state == '4':
                    battle.time_left = ''
            else:
                battle.state = '4'
                battle.time_left = ''

    def run_battle(self):
        while not self.finished:
            if self.state == '1':
                self.start_battle()
            elif self.state == '2':
                self.choose_characters()
            elif self.state == '3':
                self.start_fight()
            elif self.state == '4':
                break

    def start_battle(self):
        if not self.attack or not self.defend:
            raise ValidationError("Debe haber al menos un atacante (jugador) y un defensor (enemigo).")

        for player in self.attack:
            selected_character = self.env['abyss.character'].search([('characters', 'in', player.character.ids)], limit=1)
            if not selected_character:
                raise ValidationError(f"El jugador {player.name} debe elegir un personaje antes de continuar.")

            # Verificar si el personaje tiene un arma asignada
            if not selected_character.weapons:
                raise ValidationError(
                    f"El jugador {player.name} debe tener al menos un arma asignada a su personaje antes de continuar.")

        for player in self.defend:
            selected_enemy = self.env['abyss.enemy'].search([('enemies', 'in', player.enemy.ids)], limit=1)
            if not selected_enemy:
                raise ValidationError(f"El jugador {player.name} debe asignar un enemigo antes de continuar.")

        self.battle_start_time = fields.Datetime.now()
        self.state = '2'

    def choose_characters(self):
        if not self.attack or not self.defend:
            raise ValidationError("Debe haber al menos un atacante (jugador) y un defensor (enemigo).")

        for player in self.attack:
            # Verificar si el jugador tiene al menos un personaje
            if not player.character or not player.character[0].weapons:
                raise ValidationError(
                    f"El jugador {player.name} debe tener al menos un personaje con un arma antes de continuar.")

        for player in self.defend:
            selected_enemy = self.env['abyss.enemy'].search([('enemies', 'in', player.enemy.ids)], limit=1)
            if not selected_enemy:
                raise ValidationError(f"El jugador {player.name} debe asignar un enemigo antes de continuar.")

        self.state = '3'

    def start_fight(self):
        attacker = self.attack[0]
        defender = self.defend[0]

        # Verificar si el atacante tiene al menos un arma
        if not attacker.character[0].weapons:
            raise ValidationError(f"El jugador {attacker.name} debe tener al menos un arma antes de atacar.")

        if attacker.character[0].weapons[0].weapon_type == defender.element_type:
            raise ValidationError("No puedes atacar a un enemigo inmune. Elige otro personaje.")

        player_damage = attacker.character[0].weapons[0].damage
        enemy_damage = defender.damage

        self.inflict_damage(defender, player_damage)

        if defender.health <= 0:
            self.reward_winner()
            self.finished = True
        else:
            self.inflict_damage(attacker.character[0], enemy_damage)

            if attacker.character[0].health <= 0:
                self.finished = True
                self.winner = defender.name
                self.reward_winner()

    def inflict_damage(self, target, damage):
        if isinstance(target, self.env['abyss.character']):
            target.health -= damage
            if target.health <= 0:
                target.is_dead = True
        elif isinstance(target, self.env['abyss.enemy']):
            target.health -= damage
            if target.health <= 0:
                self.end_battle()

    def end_battle(self):
        if self.attack[0].character[0].health <= 0:
            self.winner = self.defend[0].name
            self.reward_winner()
        elif self.defend[0].health <= 0:
            self.winner = self.attack[0].character[0].name
            self.reward_winner()

        self.finished = True

    def reward_winner(self):
        winner = self.env['abyss.player'].search([('name', '=', self.winner)], limit=1)

        # Lógica para dar dinero y experiencia al ganador
        winner.write({
            'money': winner.money + 1000,
            'experience': winner.experience + 50
        })
