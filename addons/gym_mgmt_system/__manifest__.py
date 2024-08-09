# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Shahul Faiz (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'GYM Management System',
    'summary': 'GYM Management System',
    'version': '15.0.1.0.0',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'description': "GYM Management System",
    'depends': [
        'mail', 'contacts', 'hr', 'product', 'membership', 'sale', 'membership_variable_period', 'crm', 'account', 
        'partner_contact_birthdate', 'partner_contact_gender', 'sign', 'l10n_pe_edi_odoofact', 'calendar', 
        'ruc_validation_sunat', 'partner_contact_personal_information_page', 
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/assign_workout.xml',
        'wizard/automatic_payment.xml',
        'wizard/move_cancel_views.xml',
        'views/equipments.xml',
        'views/members.xml',
        'views/report.xml',
        'views/exercise.xml',
        'views/exercise_for.xml',
        'views/trainer_skill.xml',
        'views/membership_plan.xml',
        'views/membership.xml',
        'views/measurement_history.xml',
        'views/attendance_record.xml',
        'views/workout_plan.xml',
        'views/trainers.xml',
        'views/crm.xml',
        'views/calendar_views.xml',
        'wizard/upgrade_crm_lead.xml',
        'wizard/freeze_wizard_views.xml',
        'wizard/transfer_wizard_views.xml',
        'wizard/attendace_wizard_views.xml',
        'report/workout_plan_reports.xml',
        'report/workout_plan_template.xml',
        'report/my_workout_plan_reports.xml',
        'report/my_workout_plan_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'gym_mgmt_system/static/src/js/systray_icon.js',
            'gym_mgmt_system/static/src/xml/systray_icon.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
