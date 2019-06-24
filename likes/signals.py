from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify
from django.utils.html import strip_tags
from .models import LikeRecord


@receiver(post_save, sender=LikeRecord)
def send_notification(sender, instance, **kwargs):
	# 发送站内消息
	if instance.content_type.model == 'blog':
		# 点赞博客
		blog = instance.content_object
		verb = '{0} 点赞了你的博客《{1}》'.format(instance.user.get_username_or_nickname(), blog.title)
	elif instance.content_type.model == 'comment':
		# 点赞评论
		comment = instance.content_object
		verb = '{0} 点赞了你的评论"{1}"'.format(instance.user.get_username_or_nickname(), strip_tags(comment.text))
	url = instance.content_object.get_url()
	recipient = instance.content_object.get_user()
	notify.send(instance.user, recipient=recipient, verb=verb, action_object=instance, url=url)