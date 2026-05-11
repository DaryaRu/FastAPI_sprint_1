class ServiceException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)
        
class ObjectNotFoundException(ServiceException):
    detail = "Объект не найден"
