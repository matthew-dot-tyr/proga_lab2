"""Лабораторная работа № 2, вариант 7: пассажирский транспорт (меню)."""

from exceptions import TransportError
from models import (Bus, Passenger, Route, Stop, Tram, TransportSystem)
from storage import JsonStorage, Storage, XmlStorage

MENU = """
===== Пассажирский транспорт =====
1. Добавить маршрут          8. Купить билет
2. Показать маршруты         9. Показать билеты
3. Найти маршруты по остановке  10. Переоформить билет
4. Изменить цену маршрута    11. Вернуть билет
5. Удалить маршрут           12. Сохранить в файл
6. Добавить остановку        13. Загрузить из файла
7. Удалить остановку          0. Выход"""


class ConsoleMenu:
    """Консольное меню. Ошибки выводятся, программа не завершается."""

    def __init__(self, system: TransportSystem) -> None:
        self.system = system

    @staticmethod
    def _storage(path: str) -> Storage:
        """Формат выбирается по расширению файла."""
        return XmlStorage() if path.endswith(".xml") else JsonStorage()

    def run(self) -> None:
        while True:
            print(MENU)
            try:
                choice = input("Выберите пункт: ").strip()
                if choice == "0":
                    print("До свидания!")
                    break
                self.handle(choice)
            except TransportError as exc:  # собственные исключения
                print(f"Ошибка: {exc}")
            except ValueError as exc:  # например, ввели не число
                print(f"Неверный ввод: {exc}")
            except (EOFError, KeyboardInterrupt):
                print("\nВвод прерван")
                break

    def handle(self, choice: str) -> None:
        if choice == "1":
            self.add_route()
        elif choice == "2":
            print("\n".join(r.get_info() for r in self.system.routes.values())
                  or "Маршрутов нет")
        elif choice == "3":
            found = self.system.find_routes_by_stop(input("Остановка: "))
            print("\n".join(r.get_info() for r in found) or "Не найдено")
        elif choice == "4":
            self.system.update_route_price(input("Номер маршрута: "),
                                           float(input("Новая цена: ")))
        elif choice == "5":
            self.system.delete_route(input("Номер маршрута: "))
        elif choice == "6":
            route = self.system.get_route(input("Номер маршрута: "))
            route.add_stop(Stop(input("Название остановки: ")))
        elif choice == "7":
            route = self.system.get_route(input("Номер маршрута: "))
            route.remove_stop(int(input("Номер остановки: ")) - 1)
        elif choice == "8":
            passenger = Passenger(input("Имя пассажира: "),
                                  input("Телефон: "))
            ticket = self.system.buy_ticket(passenger,
                                            input("Номер маршрута: "))
            print(ticket.get_info())
        elif choice == "9":
            print("\n".join(t.get_info()
                            for t in self.system.tickets.values())
                  or "Билетов нет")
        elif choice == "10":
            self.system.change_ticket_route(int(input("Номер билета: ")),
                                            input("Новый маршрут: "))
        elif choice == "11":
            self.system.refund_ticket(int(input("Номер билета: ")))
        elif choice == "12":
            path = input("Файл (.json или .xml): ")
            self._storage(path).save(self.system, path)
            print("Сохранено")
        elif choice == "13":
            path = input("Файл (.json или .xml): ")
            self.system = self._storage(path).load(path)
            print("Загружено")
        else:
            print("Нет такого пункта")

    def add_route(self) -> None:
        number = input("Номер маршрута: ")
        title = input("Название: ")
        price = float(input("Цена билета: "))
        kind = input("Транспорт (1 - автобус, 2 - трамвай): ")
        vehicle_number = input("Номер транспорта: ")
        capacity = int(input("Вместимость: "))
        if kind == "2":
            vehicle = Tram(vehicle_number, capacity,
                           int(input("Число вагонов: ")))
        else:
            low = input("Низкий пол (да/нет): ") == "да"
            vehicle = Bus(vehicle_number, capacity, low)
        self.system.add_route(Route(number, title, price, vehicle))
        print("Маршрут добавлен")


if __name__ == "__main__":
    ConsoleMenu(TransportSystem()).run()
