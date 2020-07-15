import re
import functools
from werkzeug import MultiDict
from werkzeug.wrappers import Request

class BaseValidator:
    '''Base validator for single form fields'''

    def check(self, fieldname, fieldvalue):
        pass

class BaseCompositeValidator:
    '''Base validator for multiple form fields'''

    def check(self, form):
        pass

class Required(BaseValidator):
    '''Validates form fields that are required'''

    def check(self, fieldname, fieldvalue):
        if len(fieldvalue) == 0:
            return f'Required'

class MinLength(BaseValidator):
    '''Validates form fields that have a minimum length'''

    def __init__(self, minlength):
        self.minlength = minlength

    def check(self, fieldname, fieldvalue):
        if len(fieldvalue) < self.minlength:
            return f'Needs to be {self.minlength} characters long or longer'

class MaxLength(BaseValidator):
    '''Validates form fields that have a minimum length'''

    def __init__(self, maxlength):
        self.maxlength = maxlength

    def check(self, fieldname, fieldvalue):
        if len(fieldvalue) > self.maxlength:
            return f'Too long. Needs to be {self.maxlength} characters long or shorter'

class Email(BaseValidator):
    '''Validates form email fields'''

    def check(self, fieldname, fieldvalue):
        if not re.match(r'\w+@\w+\.\w+', fieldvalue):
            return f'Has to be an email address'

class Equal(BaseCompositeValidator):
    '''Composite validator that check for equality of to form fields'''

    def __init__(self, field_a, field_b):
        self.field_a = field_a
        self.field_b = field_b

    def check(self, form):
        if self.field_a in form and self.field_b in form:
            if form[self.field_a] != form[self.field_b]:
                return {'': f'{self.field_a} has to equal {self.field_b}'}

class ValidationManager:
    '''Used as validation orchestrator'''

    def __init__(self, form_description, composite_validators=[]):
        self.form_blueprint = form_description
        self.composite_validators = composite_validators

    def check(self, form):
        summary = {}
        for field, validators in self.form_blueprint.items():
            if field in form.keys():
                fieldvalue = form[field]
                for validator in validators:
                    error = validator.check(field, fieldvalue)
                    if error:
                        summary[field] = error
            else:
                raise Exception()

        for validator in self.composite_validators:
                errors = validator.check(form)
                if errors:
                    summary.update(errors)
                    
        return summary