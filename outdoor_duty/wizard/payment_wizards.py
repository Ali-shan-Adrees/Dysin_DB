from  odoo import api,models, fields
from datetime import date

class payAmountWizards(models.TransientModel):
    _name = 'pay.amount.wizards'
    _description = 'Payment Wizard'

    amount = fields.Float(string='Paid amount', copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner')
    debit_account_id = fields.Many2one('account.account', string='Debit Account')
    credit_account_id = fields.Many2one('account.account', string='Credit Account')
    journal_id = fields.Many2one('account.journal', string='Journal')
    reference = fields.Char(string='Description')

    @api.model
    def default_get(self, fields):
        res = super(payAmountWizards, self).default_get(fields)
        # Set default debit and credit account IDs
        default_debit_account = self.env['account.account'].search([('code', '=', '300500200020001')], limit=1)
        default_credit_account = self.env['account.account'].search([('code', '=', '300800100010001')], limit=1)
        default_journal = self.env['account.journal'].search([('name', '=', 'Cash In Hand (PKR)')], limit=1)
        res.update({
            'debit_account_id': default_debit_account.id,
            'credit_account_id': default_credit_account.id,
            'journal_id': default_journal.id,
        })
        return res


    def submitted_payment(self):
        print("Yeah Clicked")
        line_ids = []
        credit_amount = 0.0
        for line in self:
            line_id ={
                'account_id': line.debit_account_id.id,
                'partner_id': line.partner_id.id,
                'name': line.reference,
                'debit': line.amount > 0.0 and line.amount or 0.0,
                'credit': line.amount < 0.0 and -line.amount or 0.0,
            }
            line_ids.append((0,0,line_id))
            credit_amount += line.amount
            line_credit_id = {
                'account_id': line.credit_account_id.id,
                'partner_id': line.partner_id.id,
                'name': line.reference,
                'debit': credit_amount > 0.0 and -credit_amount or 0.0,
                'credit': credit_amount < 0.0 and credit_amount or 0.0,

            }
            line_ids.append((0, 0, line_credit_id))
            move = {
                'name': '/',
                'journal_id': line.journal_id.id,
                'date': date.today(),
                'ref': line.reference,
                'line_ids': line_ids

            }
            if line_ids:
                move_id = self.env['account.move'].create(move)
                move_id.action_post()
                self.env['travel.authority'].browse(self._context.get('active_ids')).update({'payment_id': move_id})




        # if line_ids:
        #     move_id = self.env['account.move'].create(move)
        #     move_id.action_post()
        # self.write({'state': 'draft', 'move_id': move_id.id})

        self.env['travel.authority'].browse(self._context.get('active_ids')).update({'paid_amount':self.amount})
        return True
