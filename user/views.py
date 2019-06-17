import random, string, time
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import LoginForm, RegisterForm, ChangeNickNameForm, BindEmailForm, ResetPasswordForm, ForgotPasswordForm
from .models import Profile
# Create your views here.
def login(request):
	'''
	username = request.GET.get('username', '')
	password = request.GET.get('password', '')
	user = auth.authenticate(request, username=username, password=password)
	if user:
		auth.login(request, user)
		return redirect('/')
	else:
		return render(request, 'error.html', {'message':'用户名或密码不正确'})
	'''
	if request.method == 'POST':
		login_form = LoginForm(request.POST)
		if login_form.is_valid():
			user = login_form.cleaned_data['user']
			auth.login(request, user)
			if request.GET.get('from'):
				return redirect(request.GET.get('from'))
			else:
				return redirect(reverse('home'))
	else:
		login_form = LoginForm()
	context = {}
	context['login_form'] = login_form
	return render(request, 'user/login.html', context)

def login_for_modal(request):
	login_form = LoginForm(request.POST)
	data = {}
	if login_form.is_valid():
		user = login_form.cleaned_data['user']
		auth.login(request, user)
		data['status'] = 'SUCCESS'
	else:
		data['status'] = 'ERROR'
	print(data['status'])
	return JsonResponse(data)

def register(request):
	if request.method == 'POST':
		register_form = RegisterForm(request.POST, request=request)
		if register_form.is_valid():
			username = register_form.cleaned_data['username']
			email = register_form.cleaned_data['email']
			password = register_form.cleaned_data['password']
			# 创建用户
			user = User.objects.create_user(username, email, password)
			user.save()

			# 清除session
			del request.session['register_code']
			# 登录用户
			user = auth.authenticate(username=username, password=password)
			auth.login(request, user)
			if request.GET.get('from'):
				return redirect(request.GET.get('from'))
			else:
				return redirect(reverse('home'))
	else:
		register_form = RegisterForm()
	context = {}
	context['register_form'] = register_form
	return render(request, 'user/register.html', context)

def logout(request):
	auth.logout(request)
	return redirect(request.GET.get('from'), reverse('home'))

def get_user_info(request):
	return render(request, 'user/user_info.html', {})

def change_nickname(request):
	redirect_to = request.GET.get('from', reverse('home'))
	if request.method == 'POST':
		form = ChangeNickNameForm(request.POST, user=request.user)
		if form.is_valid():
			nickname_new = form.cleaned_data['nickname_new']
			profile, created = Profile.objects.get_or_create(user=request.user)
			profile.nickname = nickname_new
			profile.save() 
			return redirect(redirect_to)
	else:
		form = ChangeNickNameForm()
	context = {}
	context['form'] = form
	context['page_title'] = '修改昵称'
	context['form_title'] = '修改昵称'
	context['submit_text'] = '确认'
	context['return_back'] = redirect_to
	return render(request, 'form.html', context)

def bind_email(request):
	redirect_to = request.GET.get('from', reverse('home'))
	if request.method == 'POST':
		form = BindEmailForm(request.POST, request=request)
		if form.is_valid():
			email = form.cleaned_data['email']
			request.user.email = email
			request.user.save()

			# 清除session
			del request.session['bind_email_code']
			return redirect(redirect_to)
	else:
		form = BindEmailForm()
	context = {}
	context['form'] = form
	context['page_title'] = '绑定邮箱'
	context['form_title'] = '绑定邮箱'
	context['submit_text'] = '确认'
	context['return_back'] = redirect_to
	return render(request, 'user/bind_email.html', context)



def send_verification_code(request):
	email = request.GET.get('email', '')
	send_for = request.GET.get('send_for', '')
	data = {}
	if email != '':
		# 生成验证码,字母+数字
		code_string = string.ascii_letters + string.digits
		code = ''.join(random.sample(code_string, 4))
		now = int(time.time())
		send_code_time = request.session.get('send_code_time', 0)
		if now - send_code_time < 30:
			data['status'] = 'ERROR'
		else:
			# session保存验证码
			request.session[send_for] = code	
			request.session['send_code_time'] = now
			# 发送邮件
			send_mail(
				'绑定邮箱',
				'验证码: %s' % code,
				'925431746@qq.com',
				[email], # 接收邮件的邮箱
				fail_silently=False,
				)	
			data['status'] = 'SUCCESS'
	else:
		data['status'] = 'ERROR'
	return JsonResponse(data)

def reset_password(request):
	redirect_to = request.GET.get('from', reverse('home'))
	if request.method == 'POST':
		form = ResetPasswordForm(request.POST, user=request.user)
		if form.is_valid():
			user = request.user
			new_password = form.cleaned_data['new_password']
			user.set_password(new_password)
			user.save()
			auth.logout(request)
			return redirect(reverse('home'))
	else:
		form = ResetPasswordForm()
	context = {}
	context['form'] = form
	context['page_title'] = '修改密码'
	context['form_title'] = '修改密码'
	context['submit_text'] = '确认'
	context['return_back'] = redirect_to
	return render(request, 'form.html', context)


def forgot_password(request):
	redirect_to = request.GET.get('from', reverse('home'))
	if request.method == 'POST':
		form = ForgotPasswordForm(request.POST, request=request)
		if form.is_valid():
			email = form.cleaned_data['email']
			new_password = form.cleaned_data['new_password']
			user = User.objects.get(email=email)
			user.set_password(new_password)
			user.save()
			return redirect(reverse('home'))
	else:
		form = ForgotPasswordForm()
	context = {}
	context['form'] = form
	context['page_title'] = '重置密码'
	context['form_title'] = '重置密码'
	context['submit_text'] = '确认'
	context['return_back'] = redirect_to
	return render(request, 'user/forgot_password.html', context)