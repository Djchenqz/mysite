from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Q
from read_statistics.utils import get_seven_days_read_data,get_hot_blog
from blog.models import Blog, BlogType

def error(request):
	return render(request, '404.html', {})

def home(request):
	blog_content_type = ContentType.objects.get_for_model(Blog)
	read_nums, dates = get_seven_days_read_data(blog_content_type)
	# 获取博客排行缓存
	hot_blogs = cache.get('hot_blogs')
	if not hot_blogs:
		hot_blogs = get_hot_blog(blog_content_type)
		cache.set('hot_blogs', hot_blogs, 3600)
	context = {}
	context['read_nums'] = read_nums
	context['dates'] = dates
	context['hot_blogs'] = hot_blogs
	context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
	context['newest_blogs'] = Blog.objects.all().order_by('created_time')[:10]
	return render(request, 'home.html', context)

def search(request):
	search_words = request.GET.get('wd', '').strip()
	# 分词：按空格 & | ~
	condition = None
	for word in search_words.split(' '):
	    if condition is None:
	        condition = Q(title__icontains=word)
	    else:
	        condition = condition | Q(title__icontains=word)
	
	search_blogs = []
	if condition is not None:
	    # 筛选：搜索
	    search_blogs = Blog.objects.filter(condition)

	# 分页
	paginator = Paginator(search_blogs, 20)
	page_num = request.GET.get('page', 1) # 获取url的页面参数（GET请求）
	page_of_blogs = paginator.get_page(page_num)

	context = {}
	context['search_words'] = search_words
	context['search_blogs_count'] = search_blogs.count()
	context['page_of_blogs'] = page_of_blogs
	return render(request, 'search.html', context)