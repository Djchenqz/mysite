from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Count
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
		print('计算数据')
	else:
		print('使用缓存')
	context = {}
	context['read_nums'] = read_nums
	context['dates'] = dates
	context['hot_blogs'] = hot_blogs
	context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
	context['newest_blogs'] = Blog.objects.all().order_by('created_time')[:10]
	return render(request, 'home.html', context)

