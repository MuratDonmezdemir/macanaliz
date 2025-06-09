from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ..models import User

class ProfileForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[
        DataRequired(message='Kullanıcı adı zorunludur.'),
        Length(min=3, max=50, message='Kullanıcı adı 3-50 karakter arasında olmalıdır.')
    ])
    email = StringField('E-posta', validators=[
        DataRequired(message='E-posta adresi zorunludur.'),
        Email(message='Geçerli bir e-posta adresi giriniz.')
    ])
    notifications = BooleanField('Bildirimleri Etkinleştir')
    submit = SubmitField('Profili Güncelle')
    
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = self.username.data
        self.original_email = self.email.data
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Bu e-posta adresi zaten kullanılıyor. Lütfen farklı bir e-posta adresi seçin.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mevcut Şifre', validators=[
        DataRequired(message='Mevcut şifrenizi girmelisiniz.')
    ])
    new_password = PasswordField('Yeni Şifre', validators=[
        DataRequired(message='Yeni şifre zorunludur.'),
        Length(min=6, message='Şifre en az 6 karakter uzunluğunda olmalıdır.')
    ])
    confirm_password = PasswordField('Yeni Şifre (Tekrar)', validators=[
        DataRequired(message='Şifre tekrarı zorunludur.'),
        EqualTo('new_password', message='Şifreler eşleşmiyor.')
    ])
    submit = SubmitField('Şifreyi Değiştir')
