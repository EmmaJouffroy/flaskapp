
from flask_wtf import Form
from wtforms import SelectField
from wtforms.validators import DataRequired


class SearchForm(Form):
    search = SelectField(choices=[('Tous', 'Tous'),
                                  ('Agriculture et agroalimentaire',
                                   'Agriculture et agroalimentaire'),
                                  ('Énergie', 'Énergie'),
                                  ('Commerce et artisanat',
                                   'Commerce et artisanat'),
                                  ('Tourisme', 'Tourisme'),
                                  ('Finance et assurance', 'Finance et assurance'),
                                  ('Télécoms et Internet', 'Télécoms et Internet'),
                                  ('Recherche', 'Recherche')])
