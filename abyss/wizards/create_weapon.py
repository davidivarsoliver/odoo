from odoo import models, fields, api
class createweapon(models.TransientModel):
    _name = 'abyss.createweapon'

    name = fields.Char()
    cost = fields.Float(default=0.0)
    weapon_type = fields.Selection(
        [('Sword', 'Sword'), ('Claymore', 'Claymore'), ('Bow', 'Bow'), ('Catalyst', 'Catalyst'),
         ('Polearm', 'Polearm')])
    damage = fields.Integer()
    small_image = fields.Image(max_width=50, max_height=50, related='image', store=True)
    required_level = fields.Integer(default=1)
    image = fields.Image(max_width=200)

    def crear_weapon(self):
        self.env['abyss.weapon'].create({
            'name': self.name,
            'cost': self.cost,
            'weapon_type': self.weapon_type,
            'damage': self.damage,
            'small_image': self.small_image,
            'required_level': self.required_level,
            'image': self.image
    })