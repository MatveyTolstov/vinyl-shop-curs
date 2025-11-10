"""Middleware для логирования действий пользователей"""
from django.utils.deprecation import MiddlewareMixin
from .logger_utils import create_log_entry


class LoggingMiddleware(MiddlewareMixin):
    """Middleware для логирования входов и выходов пользователей"""
    
    def process_request(self, request):
        request._logging_user = getattr(request, 'user', None)
        request._logging_path = request.path
        return None
    
    def process_response(self, request, response):
        if response.status_code < 400:
            user = getattr(request, 'user', None)
            path = getattr(request, '_logging_path', request.path)

            ip_address = self.get_client_ip(request)

            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            
            if path == '/login/' and user and user.is_authenticated:
                create_log_entry(
                    action='login',
                    user=user,
                    description=f'Пользователь {user.username} вошел в систему',
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            
            elif path == '/logout/':
                create_log_entry(
                    action='logout',
                    user=getattr(request, '_logging_user', None),
                    description='Пользователь вышел из системы',
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            
            elif path == '/signup/' and response.status_code == 302:
                if hasattr(request, 'user') and request.user.is_authenticated:
                    create_log_entry(
                        action='signup',
                        user=request.user,
                        description=f'Новый пользователь {request.user.username} зарегистрировался',
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
        
        return response
    
    def get_client_ip(self, request):
        """Получает IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

