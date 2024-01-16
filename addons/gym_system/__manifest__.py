# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Gym Management",
    'license': 'AGPL-3',
    'summary': """This module allow you to manage Gym.""",
    'description': """
        Gym management
        odoo gym
        gym odoo
        gym manage'
        This module allow you to manage Gym.
        Gym Management

This module Will help to manage gym activities.

Following features

Add the exercises
Set Schedule for particular Customer
Set nutrition plane
BMI Calculation
Calory Calculator
Menu:

Exercise:
Body Parts
Exercises
Muscles
Exercise Overview
Equipment
Ingredients
Workouts
Create Workouts Schedule
Workouts Schedules
Print Workouts Schedules
Nutrition Plans
BMI Calculation
Daily Calories Calculator
Weight Entry Overview

        
    """,
    'version': "12.0",
    'author': "David Montero Crespo",
    'support': 'softwareescarlata@gmail.com',
    'images': ['static/description/img1.jpg'],
    'category' : 'tools',
    'depends': ['base','product','calendar'],
    'data':[
        'security/gym_seurity.xml',
        'security/ir.model.access.csv',
        'data/gym_days.xml',
        'data/sequence.xml',
        'views/menu.xml',
        'wizard/weight_entry.xml',
        'wizard/wrokout_schedule_report_wizard.xml',
        'views/gym_workouts_view.xml',
        'views/workout_overview.xml',
        'views/body_parts.xml',
        'views/nutrition_plans.xml',
        'views/weight_entry.xml',
        'views/gym_equipment.xml',
        'views/muscle.xml',
        'views/ingredient.xml',
        'views/calculate_bmi.xml',
        'views/calorie_calculator.xml',
        'views/exercise_overview.xml',
        'views/exercise_body_parts.xml',
        'views/gym_customer.xml',
        'views/days.xml',
        'report/workout_report.xml',
        'wizard/workout_schedule.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,

}
