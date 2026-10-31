"""Демонстрация исключений и записи/чтения файлов JSON и XML."""

from exceptions import TransportError
from models import (Bus, Passenger, Route, Stop, Tram, TransportSystem)
from storage import JsonStorage, XmlStorage


def build_system() -> TransportSystem:
    """Создаёт тестовые данные: два маршрута и два билета."""
    system = TransportSystem()
    bus = Route("25", "Центр - Вокзал", 50.0, Bus("А123ВС", 2, True))
    for name in ("Центр", "Площадь", "Вокзал"):
        bus.add_stop(Stop(name))
    tram = Route("7", "Парк - Завод", 40.0, Tram("Т-501", 100, 2))
    for name in ("Парк", "Площадь", "Завод"):
        tram.add_stop(Stop(name))
    system.add_route(bus)
    system.add_route(tram)
    system.buy_ticket(Passenger("Иван Петров", "+7 900 111-22-33"), "25")
    system.buy_ticket(Passenger("Анна Смирнова", "+7 900 444-55-66"), "7")
    return system


def demo_exceptions() -> None:
    system = build_system()
    print("--- Обработка исключений ---")
    try:
        system.get_route("999")                      # маршрута нет
    except TransportError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        Bus("А1", -5)                                # плохая вместимость
    except TransportError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        system.get_ticket(99)                        # билета нет
    except TransportError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        system.get_route("25").remove_stop(10)       # остановки нет
    except TransportError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        # на маршруте 25 всего 2 места, один билет уже продан
        system.buy_ticket(Passenger("Пётр", "1"), "25")
        system.buy_ticket(Passenger("Ольга", "2"), "25")
    except TransportError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        system.add_route(Route("7", "Дубль", 10.0, Bus("Б1", 10)))
    except TransportError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        JsonStorage().load("no_file.json")           # файла нет
    except TransportError as exc:
        print(f"[{type(exc).__name__}] {exc}")
    try:
        Passenger("", "123")                         # встроенное ValueError
    except ValueError as exc:
        print(f"[ValueError] {exc}")
    try:
        print(10 / 0)                                # встроенное исключение
    except ZeroDivisionError as exc:
        print(f"[ZeroDivisionError] {exc}")
    finally:
        print("[finally] выполняется всегда")


def demo_files() -> None:
    system = build_system()
    JsonStorage().save(system, "data/transport.json")
    XmlStorage().save(system, "data/transport.xml")
    print("\n--- Чтение из файлов ---")
    for storage, path in ((JsonStorage(), "data/transport.json"),
                          (XmlStorage(), "data/transport.xml")):
        loaded = storage.load(path)
        print(f"{path}:")
        for route in loaded.routes.values():
            print(route.get_info())
        for ticket in loaded.tickets.values():
            print(ticket.get_info())


if __name__ == "__main__":
    demo_exceptions()
    demo_files()
