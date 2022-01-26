from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    is_instructor = fields.Boolean(string='Instructor')
    session_ids = fields.Many2many('session.session', string='Sessions')
    is_teacher = fields.Boolean(string='Teacher')
    teacher_lvl = fields.Selection(selection=[('lvl1', 'Level 1'), ('lvl2', 'Level 2')])
