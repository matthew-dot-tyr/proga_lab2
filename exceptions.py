"""Собственные исключения для программы «Пассажирский транспорт»."""


class TransportError(Exception):
    """Базовое исключение программы."""


class InvalidCapacityError(TransportError):
    """Вместимость транспорта должна быть положительным числом."""


class StopIndexError(TransportError):
    """Остановки с таким номером нет в маршруте."""


class DuplicateRouteError(TransportError):
    """Маршрут с таким номером уже существует."""


class RouteNotFoundError(TransportError):
    """Маршрут не найден."""


class TicketNotFoundError(TransportError):
    """Билет не найден."""


class NoSeatsError(TransportError):
    """На маршруте нет свободных мест."""


class StorageError(TransportError):
    """Ошибка при чтении или записи файла."""
