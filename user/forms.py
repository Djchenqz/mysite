from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

class LoginForm(forms.Form):
	username_or_email = forms.CharField(label='用户名',
								widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入用户名或邮箱'}))
	password = forms.CharField(label='密码',
								widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入密码'}))

	def clean(self):
		username_or_email = self.cleaned_data['username_or_email']
		password = self.cleaned_data['password']
		user = auth.authenticate(username=username_or_email, password=password)
		if not user:
			if User.objects.filter(email=username_or_email).exists():
				username = User.objects.get(email=username_or_email).username
				user = auth.authenticate(username=username, password=password)
				if user:
					self.cleaned_data['user'] = user
					return self.cleaned_data
				raise forms.ValidationError('用户名或密码不正确')
			raise forms.ValidationError('用户名或密码不正确')
		else:
			self.cleaned_data['user'] = user
		return self.cleaned_data

class RegisterForm(forms.Form):
	username = forms.CharField(label='用户名',
								max_length=30, 
								min_length=3, 
								widget=forms.TextInput(
									attrs={'class':'form-control', 'placeholder':'请输入3-30位用户名'}))
	email = forms.CharField(label='邮箱',
							widget=forms.EmailInput(
								attrs={'class':'form-control', 'placeholder':'请输入邮箱'}))
	password = forms.CharField(label='密码',
							min_length=6, 
							widget=forms.PasswordInput(
								attrs={'class':'form-control', 'placeholder':'请输入密码'}))
	password2 = forms.CharField(label='再输入一次密码',
							min_length=6, 
							widget=forms.PasswordInput(
								attrs={'class':'form-control', 'placeholder':'请再输入密码'}))
	verification_code = forms.CharField(label='验证码',
										required=False,
										widget=forms.TextInput(
											attrs={'class':'form-control', 'placeholder':'点击“发送验证码”发送到邮箱'}))
	def __init__(self, *args, **kwargs):
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super(RegisterForm, self).__init__(*args, **kwargs)

	def clean(self):
		# 判断验证码
		code = self.request.session.get('register_code', '') # 服务器发送的验证码
		verification_code = self.cleaned_data.get('verification_code', '') # 用户提交的验证码
		if code == '' or code != verification_code:
			raise forms.ValidationError('验证码不正确')
		return self.cleaned_data

	def clean_username(self):
		username = self.cleaned_data['username']
		if User.objects.filter(username=username).exists():
			raise forms .ValidationError('用户名已存在')
		return username

	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱已被注册')
		return email

	def clean_password2(self):
		password = self.cleaned_data['password']
		password2 = self.cleaned_data['password2']
		if password != password2:
			raise forms.ValidationError('两次密码输入不一致')
		return password2

	def clean_verification_code(self):
		verification_code = self.cleaned_data.get('verification_code', '').strip()
		if verification_code == '':
			raise forms.ValidationError('验证码不能为空')
		return verification_code

class ChangeNickNameForm(forms.Form):
	nickname_new = forms.CharField(label='新的昵称',
								max_length=20,
								widget=forms.TextInput(
									attrs={'class':'form-control', 'placeholder':'请输入新的昵称'}))
	def __init__(self, *args, **kwargs):
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super(ChangeNickNameForm, self).__init__(*args, **kwargs)

	def clean(self):
		if self.user.is_authenticated:
			self.cleaned_data['user'] = self.user
		else:
			raise forms.ValidationError('您尚未登录')

	def clean_nickname(self):
		nickname_new = self.cleaned_data.get('nickname_new', '').strip()
		if nickname_new == '':
			raise forms.ValidationError('新的昵称不能为空')
		return nickname_new

class BindEmailForm(forms.Form):
	email = forms.EmailField(label='邮箱',
							widget=forms.EmailInput(
								attrs={'class':'form-control', 'placeholder':'请输入正确的邮箱'}))
	verification_code = forms.CharField(label='验证码',
										required=False,
										widget=forms.TextInput(
											attrs={'class':'form-control', 'placeholder':'点击“发送验证码”发送到邮箱'}))
	def __init__(self, *args, **kwargs):
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super(BindEmailForm, self).__init__(*args, **kwargs)

	def clean_email(self):
		# 判断用户是否登录
		if self.request.user.is_authenticated:
			self.cleaned_data['user'] = self.request.user
		else:
			raise forms.ValidationError('用户尚未登录')
		# 判断用户是否已绑定邮箱
		if self.request.user.email != '':
			raise forms.ValidationError('您已绑定邮箱')
		# 判断验证码
		code = self.request.session.get('bind_email_code','') # 服务器发送的验证码
		verification_code = self.cleaned_data.get('verification_code','') # 用户提交的验证码
		if code == '' or code != verification_code:
			raise forms.ValidationError('验证码不正确')
		return self.cleaned_data

	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱已被绑定')
		return email

	def clean_verification_code(self):
		verification_code = self.cleaned_data.get('verification_code', '').strip()
		if verification_code == '':
			raise forms.ValidationError('验证码不能为空')
		return verification_code

class ResetPasswordForm(forms.Form):
	old_password = forms.CharField(label='原密码',
								min_length=6,
								widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入原密码'}))
	new_password = forms.CharField(label='新密码',
								min_length=6,
								widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入新密码'}))
	new_password2 = forms.CharField(label='新密码',
								min_length=6,
								widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请再输入新密码'}))
	def __init__(self, *args, **kwargs):
		if 'user' in kwargs:
			self.user = kwargs.pop('user')
		super(ResetPasswordForm, self).__init__(*args, **kwargs)

	def clean(self):
		# 验证新密码输入是否正确
		new_password = self.cleaned_data.get('new_password', '')
		new_password2 = self.cleaned_data.get('new_password2', '')
		if new_password != new_password2 or new_password == '':
			raise forms.ValidationError('密码输入不正确')
		return self.cleaned_data

	def clean_old_password(self):
		# 验证原密码是否正确
		old_password = self.cleaned_data.get('old_password', '')
		if not self.user.check_password(old_password):
			raise forms.ValidationError('原密码输入不正确')
		return old_password


class ForgotPasswordForm(forms.Form):
	email = forms.CharField(label='邮箱',
							widget=forms.EmailInput(
								attrs={'class':'form-control', 'placeholder':'请输入绑定的邮箱'}))
	verification_code = forms.CharField(label='验证码',
								required=False,
								widget=forms.TextInput(
									attrs={'class':'form-control', 'placeholder':'点击“发送验证码”发送到邮箱'}))
	new_password = forms.CharField(label='新密码',
								min_length=6,
								widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入新密码'}))
	def __init__(self, *args, **kwargs):
		if 'request' in kwargs:
			self.request = kwargs.pop('request')
		super(ForgotPasswordForm, self).__init__(*args, **kwargs)


	def clean_email(self):
		email = self.cleaned_data.get('email', '').strip()
		if not User.objects.filter(email=email).exists():
			raise forms.ValidationError('邮箱不存在')
		return email

	def clean_verification_code(self):
		verification_code = self.cleaned_data.get('verification_code', '') # 用户提交的验证码
		if verification_code.strip() == '':
			raise forms.ValidationError('验证码不能为空')
		# 判断验证码
		code = self.request.session.get('forgot_password_code', '') # 服务器发送的验证码
		if code == '' or code != verification_code:
			raise forms.ValidationError('验证码不正确')
		return verification_code