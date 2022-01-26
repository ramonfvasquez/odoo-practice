from datetime import datetime
from odoo import models, fields, api, _


class SessionWizard(models.TransientModel):
    _name = 'session.wizard'
    _description = 'Session Wizard'
    product = fields.Many2one('product.product', string='Product')
    unitary_price = fields.Float(string='Unitary Price')

    @api.onchange('product')
    def _onchange_product_price(self):
        self.unitary_price = self.product[0].list_price if self.product else 1

    def generate_attendee_invoice(self):
        session = self.env['session.session'].browse(self.env.context.get('active_id'))
        attendees = session.attendee_ids
        for record in attendees:
            account_move = self.env['account.move'].sudo().create({
                'partner_id': record.id,
                'type': 'out_invoice',
                'invoice_date': datetime.today(),
                'journal_id': 8,
            })

            invoice = self.env['account.move.line']
            invoice.sudo().with_context(check_move_validity=False).create({
                'account_id': session.id,
                'date': datetime.today(),
                'journal_id': 1,
                'move_id': account_move.id,
                'name': session.name,
                'partner_id': record.id,
                'price_unit': self.unitary_price,
                'product_id': self.product[0].id,
                'quantity': 1,
            })




