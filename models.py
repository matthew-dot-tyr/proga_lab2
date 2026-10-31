"""Классы предметной области «Пассажирский транспорт»."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from exceptions import (
    DuplicateRouteError,
    InvalidCapacityError,
    NoSeatsError,
    RouteNotFoundError,
    StopIndexError,
    TicketNotFoundError,
)


class Passenger:
    """Пассажир."""

    def __init__(self, name: str, phone: str) -> None:
        if not name.strip():
            # встроенное исключение ValueError
            raise ValueError("Имя пассажира не может быть пустым")
        self.name = name.strip()
        self.phone = phone

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "phone": self.phone}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Passenger":
        return cls(data["name"], data["phone"])


class Stop:
    """Остановка."""

    def __init__(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Название остановки не может быть пустым")
        self.name = name.strip()

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Stop":
        return cls(data["name"])


class Vehicle(ABC):
    """Абстрактное транспортное средство (базовый класс)."""

    def __init__(self, number: str, capacity: int) -> None:
        if not number.strip():
            raise ValueError("Номер транспорта не может быть пустым")
        self.number = number.strip()
        self._capacity = 1
        self.capacity = capacity  # проверка выполняется в setter

    @property
    def capacity(self) -> int:
        return self._capacity

    @capacity.setter
    def capacity(self, value: int) -> None:
        if value <= 0:
            raise InvalidCapacityError(
                f"Вместимость {value} должна быть больше нуля")
        self._capacity = value

    @abstractmethod
    def get_info(self) -> str:
        """Описание транспорта для показа на экране."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Преобразование в словарь."""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Vehicle":
        """Создаёт Bus или Tram в зависимости от поля type."""
        if data["type"] == "tram":
            return Tram(data["number"], int(data["capacity"]),
                        int(data["wagons"]))
        return Bus(data["number"], int(data["capacity"]),
                   bool(data["low_floor"]))


class Bus(Vehicle):
    """Автобус (может быть с низким полом)."""

    def __init__(self, number: str, capacity: int,
                 low_floor: bool = False) -> None:
        super().__init__(number, capacity)
        self.low_floor = low_floor

    def get_info(self) -> str:
        floor = ", низкий пол" if self.low_floor else ""
        return f"Автобус {self.number} (мест: {self.capacity}{floor})"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "bus", "number": self.number,
                "capacity": self.capacity, "low_floor": self.low_floor}


class Tram(Vehicle):
    """Трамвай (несколько вагонов)."""

    def __init__(self, number: str, capacity: int, wagons: int = 1) -> None:
        super().__init__(number, capacity)
        if wagons < 1:
            raise ValueError("Число вагонов должно быть не меньше 1")
        self.wagons = wagons

    def get_info(self) -> str:
        return (f"Трамвай {self.number} (мест: {self.capacity}, "
                f"вагонов: {self.wagons})")

    def to_dict(self) -> dict[str, Any]:
        return {"type": "tram", "number": self.number,
                "capacity": self.capacity, "wagons": self.wagons}


class Route:
    """Маршрут: номер, название, цена билета, транспорт и остановки."""

    def __init__(self, number: str, title: str, price: float,
                 vehicle: Vehicle, stops: Optional[list[Stop]] = None) -> None:
        if not number.strip() or not title.strip():
            raise ValueError("Номер и название маршрута не могут быть пустыми")
        if price <= 0:
            raise ValueError("Цена билета должна быть больше нуля")
        self.number = number.strip()
        self.title = title.strip()
        self.price = price
        self.vehicle = vehicle
        self.stops: list[Stop] = stops or []

    def add_stop(self, stop: Stop) -> None:
        """Добавляет остановку в конец маршрута."""
        self.stops.append(stop)

    def remove_stop(self, index: int) -> None:
        """Удаляет остановку по номеру (нумерация с 0)."""
        if not 0 <= index < len(self.stops):
            raise StopIndexError(
                f"Остановки {index + 1} нет (всего {len(self.stops)})")
        del self.stops[index]

    def has_stop(self, name: str) -> bool:
        return any(name.lower() == s.name.lower() for s in self.stops)

    def get_info(self) -> str:
        stops = " - ".join(s.name for s in self.stops) or "нет остановок"
        return (f"Маршрут {self.number} «{self.title}», {self.price} руб.\n"
                f"   {self.vehicle.get_info()}\n   Остановки: {stops}")

    def to_dict(self) -> dict[str, Any]:
        return {"number": self.number, "title": self.title,
                "price": self.price, "vehicle": self.vehicle.to_dict(),
                "stops": [s.to_dict() for s in self.stops]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Route":
        return cls(data["number"], data["title"], float(data["price"]),
                   Vehicle.from_dict(data["vehicle"]),
                   [Stop.from_dict(s) for s in data["stops"]])


class Ticket:
    """Билет: пассажир, номер маршрута и цена."""

    def __init__(self, ticket_id: int, passenger: Passenger,
                 route_number: str, price: float) -> None:
        self.ticket_id = ticket_id
        self.passenger = passenger
        self.route_number = route_number
        self.price = price

    def get_info(self) -> str:
        return (f"Билет №{self.ticket_id}: {self.passenger.name}, "
                f"маршрут {self.route_number}, {self.price} руб.")

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.ticket_id, "passenger": self.passenger.to_dict(),
                "route_number": self.route_number, "price": self.price}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ticket":
        return cls(int(data["id"]), Passenger.from_dict(data["passenger"]),
                   data["route_number"], float(data["price"]))


class TransportSystem:
    """Система пассажирского транспорта: маршруты и билеты (CRUD)."""

    def __init__(self) -> None:
        self.routes: dict[str, Route] = {}
        self.tickets: dict[int, Ticket] = {}
        self.next_ticket_id = 1

    # --- CRUD для маршрутов ---
    def add_route(self, route: Route) -> None:
        """Create: добавляет маршрут."""
        if route.number in self.routes:
            raise DuplicateRouteError(
                f"Маршрут {route.number} уже существует")
        self.routes[route.number] = route

    def get_route(self, number: str) -> Route:
        """Read: возвращает маршрут по номеру."""
        if number not in self.routes:
            raise RouteNotFoundError(f"Маршрут {number} не найден")
        return self.routes[number]

    def update_route_price(self, number: str, price: float) -> None:
        """Update: меняет цену билета на маршруте."""
        if price <= 0:
            raise ValueError("Цена билета должна быть больше нуля")
        self.get_route(number).price = price

    def delete_route(self, number: str) -> None:
        """Delete: удаляет маршрут вместе с его билетами."""
        self.get_route(number)
        del self.routes[number]
        for ticket_id in [t.ticket_id for t in self.tickets.values()
                          if t.route_number == number]:
            del self.tickets[ticket_id]

    def find_routes_by_stop(self, stop_name: str) -> list[Route]:
        """Возвращает маршруты, которые проходят через остановку."""
        return [r for r in self.routes.values() if r.has_stop(stop_name)]

    # --- CRUD для билетов ---
    def _sold(self, route_number: str) -> int:
        """Сколько билетов продано на маршрут."""
        return sum(1 for t in self.tickets.values()
                   if t.route_number == route_number)

    def buy_ticket(self, passenger: Passenger, route_number: str) -> Ticket:
        """Create: покупка билета (если есть свободные места)."""
        route = self.get_route(route_number)
        if self._sold(route_number) >= route.vehicle.capacity:
            raise NoSeatsError(f"На маршруте {route_number} нет мест")
        ticket = Ticket(self.next_ticket_id, passenger, route_number,
                        route.price)
        self.tickets[ticket.ticket_id] = ticket
        self.next_ticket_id += 1
        return ticket

    def get_ticket(self, ticket_id: int) -> Ticket:
        """Read: возвращает билет по номеру."""
        if ticket_id not in self.tickets:
            raise TicketNotFoundError(f"Билет №{ticket_id} не найден")
        return self.tickets[ticket_id]

    def change_ticket_route(self, ticket_id: int, route_number: str) -> None:
        """Update: переоформляет билет на другой маршрут."""
        ticket = self.get_ticket(ticket_id)
        route = self.get_route(route_number)
        if self._sold(route_number) >= route.vehicle.capacity:
            raise NoSeatsError(f"На маршруте {route_number} нет мест")
        ticket.route_number = route_number
        ticket.price = route.price

    def refund_ticket(self, ticket_id: int) -> Ticket:
        """Delete: возврат билета."""
        ticket = self.get_ticket(ticket_id)
        del self.tickets[ticket_id]
        return ticket

    # --- сериализация ---
    def to_dict(self) -> dict[str, Any]:
        return {"next_ticket_id": self.next_ticket_id,
                "routes": [r.to_dict() for r in self.routes.values()],
                "tickets": [t.to_dict() for t in self.tickets.values()]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TransportSystem":
        system = cls()
        for item in data["routes"]:
            system.add_route(Route.from_dict(item))
        for item in data["tickets"]:
            ticket = Ticket.from_dict(item)
            system.tickets[ticket.ticket_id] = ticket
        system.next_ticket_id = int(data["next_ticket_id"])
        return system
