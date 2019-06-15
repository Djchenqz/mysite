from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from .models import BlogType, Blog
from read_statistics.models import ReadNum
from read_statistics.utils import read_statistics_once_read
# Create your views here.

def get_blog_list_common_data(request, blogs):
	page_num = request.GET.get('page')
	paginator = Paginator(blogs, settings.EACH_PAGE_BLOGS_OF_NUMBER)
	page_of_blogs = paginator.get_page(page_num)
	current_page = page_of_blogs.number
	page_range = list(range(max(1, current_page-2), min(paginator.num_pages, current_page+2)+1))
	if page_range[0] > 2:
		page_range.insert(0, '...')
	if page_range[-1] < paginator.num_pages - 1:
		page_range.append('...')
	if page_range[0] != 1:
		page_range.insert(0, 1)
	if page_range[-1] != paginator.num_pages:
		page_range.append(paginator.num_pages)
	# 获取日期归档博客数量
	blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
	blog_dates_dict = {}
	for blog_date in blog_dates:
		blog_count = Blog.objects.filter(created_time__year=blog_date.year, created_time__month=blog_date.month).count()
		blog_dates_dict[blog_date] = blog_count
	context = {}
	context['blogs'] = page_of_blogs
	context['page_range'] = page_range
	context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
	context['blog_dates'] = blog_dates_dict
	return context

def blog_list(request):
	blogs_all_list = Blog.objects.all()
	context = get_blog_list_common_data(request, blogs_all_list)
	return render(request, 'blog/blog_list.html', context)

def blogs_with_type(request, blog_type_pk):
	blog_type= get_object_or_404(BlogType, pk=blog_type_pk)
	blogs_all_list = Blog.objects.filter(blog_type=blog_type)
	context = get_blog_list_common_data(request, blogs_all_list)
	context['blog_type'] = blog_type
	return render(request, 'blog/blogs_with_type.html', context)

def blogs_with_date(request, year, month):
	blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
	context = get_blog_list_common_data(request, blogs_all_list)
	context['blogs_with_date'] = '%s年%s月'%(year, month)
	return render(request, 'blog/blogs_with_date.html', context)

def blog_detail(request, blog_pk):
	blog = get_object_or_404(Blog, pk=blog_pk)
	key = read_statistics_once_read(request, blog)
	context = {}
	context['blog'] = blog
	context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
	context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
	response = render(request, 'blog/blog_detail.html', context)
	response.set_cookie(key, 'true')
	return response