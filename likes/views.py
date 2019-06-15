from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from .models import LikeCount, LikeRecord
# Create your views here.

def SuccessResponse(liked_num):
	data = {}
	data['status'] = 'SUCCESS'
	data['liked_num'] = liked_num
	return JsonResponse(data)

def ErrorResponse(message):
	data = {}
	data['status'] = 'ERROR'
	data['message'] = message
	return JsonResponse(data)

def like_change(request):
	# 获取数据
	user = request.user
	content_type = request.GET.get('content_type')
	object_id = int(request.GET.get('object_id'))
	try:
		content_type = ContentType.objects.get(model=content_type)
		model_class = content_type.model_class()
		model_obj = model_class.objects.get(pk=object_id)
	except ObjectDoesNotExist:
		return ErrorResponse('点赞对象不存在') 
	
	is_like = request.GET.get('is_like')
	print(is_like)
	if not user.is_authenticated:
		return ErrorResponse('您尚未登录')
	# 处理数据
	# 这里的is_like是字符串true或false
	if is_like == 'true':
		# 没有点赞数据，要点赞
		# 创建点赞记录
		like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
		like_record.save()
		# 点赞数据+1
		like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
		like_count.liked_num += 1
		like_count.save()
	else:
		# 有点赞数据，取消点赞
		like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
		# 删除记录
		like_record.delete()
		like_count = LikeCount.objects.get(content_type=content_type, object_id=object_id)
		# 总点赞数-1
		like_count.liked_num -= 1
		like_count.save()
	return SuccessResponse(like_count.liked_num)
