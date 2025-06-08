from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', 
                         validators=[DataRequired(message='Bu alan zorunludur!'), 
                                     Length(min=4, max=20, message='Kullanıcı adı 4-20 karakter arasında olmalıdır.')])
    
    email = StringField('E-posta',
                       validators=[DataRequired(message='Bu alan zorunludur!'), 
                                   Email(message='Geçerli bir e-posta adresi giriniz.')])
    
    password = PasswordField('Şifre', 
                           validators=[DataRequired(message='Bu alan zorunludur!'),
                                       Length(min=6, message='Şifre en az 6 karakter olmalıdır.')])
    
    confirm_password = PasswordField('Şifre Tekrar',
                                   validators=[DataRequired(message='Bu alan zorunludur!'),
                                               EqualTo('password', message='Şifreler eşleşmiyor!')])
    
    submit = SubmitField('Kayıt Ol')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen farklı bir kullanıcı adı seçin.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu e-posta adresi zaten kayıtlı. Lütfen farklı bir e-posta adresi kullanın.')

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')
