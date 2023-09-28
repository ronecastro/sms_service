from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from app.models import User, Rule, Notification
from phonenumbers import parse, is_valid_number
from flask import g

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Register')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})

    def __init__(self, user=User, custom_validation=False, *args, **kwargs):  # accept the object
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.user = user  # set the object as class attr
        self.custom_validation = custom_validation

    def validate_username(self, field):
        #print("username validation")
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            #print("username error")
            raise ValidationError('Please use a different username.')

    def validate_email(self, field):
        #print("email validation")
        #print("field", field.data)
        #print("user", self.user.email)
        if not self.custom_validation: #no custom validation
            #print("no custom_validation")
            email = User.query.filter_by(email=field.data).first()
            if email is not None:
                raise ValidationError('Please use a different email address.')
        else: #with custom validation
            #print("with custom validation")
            if (self.user.email != field.data):
                #print("field and user are different")
                email = User.query.filter_by(email=field.data).first()
                if email is None:
                    #print("user query not None")
                    pass
                else:
                    raise ValidationError('Please use a different email address.')
            else:
                #print("field and user are equal")
                pass

    def validate_phone(self, field):
        if not self.custom_validation:
            # print("phone validation")
            try:
                if is_valid_number(parse(str(field))):
                    # print("phone valid")
                    # print(field.data)
                    pass
                else:
                    raise ValidationError('Phone number not valid.')
            except:
                raise ValidationError('Phone number not valid.')

class RuleForm(FlaskForm):
    select = BooleanField()
    rule = StringField('Rule', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})

    def validate_rule(self, rule):
        id = g.id
        if id == None:
            rule = Rule.query.filter_by(rule=rule.data).first()
            if rule is not None:
                raise ValidationError('Rule already in use!')
        else:
            rule_existent = Rule.query.filter_by(id=id).first()
            #print("rule_existent", rule_existent)
            rule_modified = Rule.query.filter_by(rule=rule.data).first()
            #print("rule_modified", rule_modified)
            if rule_modified is not None:
                if rule_existent.id != rule_modified.id:
                    raise ValidationError('Rule already in use!')

class NotificationForm(FlaskForm):
    expiration = StringField('Expiration', validators=[DataRequired()])
    pv = StringField('PV', validators=[DataRequired()])
    rule = StringField('Rule', validators=[DataRequired()])
    limit = StringField('Limit(s)', validators=[DataRequired()])
    subrule = SelectField('Subrule(s)', choices=[(0, ''),(1, 'AND'), (2, 'OR'), (3, 'NOT')])
    persistent = BooleanField()
    interval = StringField('Interval', validators=[Optional()])
    submit = SubmitField('Add')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
