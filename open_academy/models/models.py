# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Course(models.Model):
    _name = 'course.course'
    name = fields.Many2one('product.product', string='Course', required=True)
    id = fields.Char()
    description = fields.Char(string='Description')
    responsible = fields.Many2one('res.users', string='Responsible')
    session_id = fields.One2many('session.session', 'course_ids', string='Session')
    _sql_constraints = [
        ('title_different_to_description', 'check(name != description)',
         'The description should be different to the title'),
        ('title_is_unique', 'unique(name)', 'The title must be unique.')
    ]

    def copy(self, default=None):
        if default is None:
            default = {}
        new_name = f'Copy of {self.name}' if self.name else ''
        default.update({
            'name': new_name,
        })
        new = super(Course, self).copy(default=default)
        return new


class Session(models.Model):
    _name = 'session.session'
    name = fields.Char(string='Session Name')
    active = fields.Boolean(default=True, string='Active')
    number_of_seats = fields.Integer(string='Number of Seats', default=1)
    occupied_seats = fields.Integer(compute='_compute_occupied_seats')
    attendee_ids = fields.Many2many('res.partner', string='Attendees')
    course_ids = fields.Many2one('course.course', string='Courses')
    duration = fields.Integer(string='Duration', default=1)
    instructor = fields.Many2one('res.partner', string='Instructor')
    start_date = fields.Date(default=lambda self: fields.Date.today(), string='Start Date')
    teacher = fields.Many2one('res.partner', string='Teacher')

    def _compute_occupied_seats(self):
        for record in self:
            record.occupied_seats = 100 - (
                    record.number_of_seats - len(record.attendee_ids)) * 100 / record.number_of_seats

    @api.constrains('attendee_ids')
    def _check_not_instructor_in_attendees(self):
        for record in self:
            if record.instructor in record.attendee_ids:
                raise ValidationError('The instructor cannot be an attendee to the session.')

    @api.onchange('number_of_seats', 'attendee_ids')
    def _onchange_seats(self):
        for record in self:
            self.occupied_seats = 100 - (self.number_of_seats - len(self.attendee_ids)) * 100 / self.number_of_seats
            if self.occupied_seats > 100:
                return {
                    'warning': {
                        'title': 'Too Many Attendees',
                        'message': f'You can\'t have more than {self.number_of_seats} attendees in your session.'
                    }
                }
            elif self.occupied_seats < 0:
                return {
                    'warning': {
                        'title': 'Wrong Value',
                        'message': 'You can\' put a negative value for the number of seats.'
                    }
                }
