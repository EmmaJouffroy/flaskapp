
from flask_wtf import Form
from wtforms import SelectField
from wtforms.validators import DataRequired


class SearchForm(Form):
    search = SelectField(choices=[('All', 'All'),
                                  ('Agriculture and agri-food',
                                   'Agriculture and agri-food'),
                                  ('Industry', 'Industry'),
                                  ('Energetics',
                                   'Energetics'),
                                  ('Trade and crafts', 'Trade and crafts'),
                                  ('Tourism', 'Tourism'),
                                  ('Telecom and Internet', 'Telecom and Internet'),
                                  ('Research', 'Research'),
                                  ('Finance and insurance', 'Finance and insurance'), ])
