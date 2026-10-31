"""Сохранение и чтение данных: JSON и XML."""

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Any

from exceptions import StorageError, TransportError
from models import TransportSystem


class Storage(ABC):
    """Базовый класс файлового хранилища."""

    @abstractmethod
    def save(self, system: TransportSystem, path: str) -> None:
        """Записывает данные в файл."""

    @abstractmethod
    def load(self, path: str) -> TransportSystem:
        """Читает данные из файла."""


class JsonStorage(Storage):
    """Хранение в формате JSON."""

    def save(self, system: TransportSystem, path: str) -> None:
        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(system.to_dict(), file, ensure_ascii=False,
                          indent=4)
        except OSError as exc:
            raise StorageError(f"Не удалось записать файл: {exc}") from exc

    def load(self, path: str) -> TransportSystem:
        try:
            with open(path, encoding="utf-8") as file:
                data = json.load(file)
            return TransportSystem.from_dict(data)
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Не удалось прочитать файл: {exc}") from exc
        except (KeyError, TypeError, ValueError, TransportError) as exc:
            raise StorageError(f"Неверные данные в файле: {exc}") from exc


class XmlStorage(Storage):
    """Хранение в формате XML (ElementTree)."""

    def save(self, system: TransportSystem, path: str) -> None:
        data = system.to_dict()
        root = ET.Element("transport",
                          next_ticket_id=str(data["next_ticket_id"]))
        routes = ET.SubElement(root, "routes")
        for item in data["routes"]:
            route = ET.SubElement(routes, "route", number=item["number"],
                                  title=item["title"],
                                  price=str(item["price"]))
            vehicle = {k: str(v) for k, v in item["vehicle"].items()}
            ET.SubElement(route, "vehicle", **vehicle)
            stops = ET.SubElement(route, "stops")
            for stop in item["stops"]:
                ET.SubElement(stops, "stop", name=stop["name"])
        tickets = ET.SubElement(root, "tickets")
        for item in data["tickets"]:
            ticket = ET.SubElement(tickets, "ticket", id=str(item["id"]),
                                   route_number=item["route_number"],
                                   price=str(item["price"]))
            ET.SubElement(ticket, "passenger", **item["passenger"])
        tree = ET.ElementTree(root)
        ET.indent(tree)  # отступы для читаемости
        try:
            tree.write(path, encoding="utf-8", xml_declaration=True)
        except OSError as exc:
            raise StorageError(f"Не удалось записать файл: {exc}") from exc

    def load(self, path: str) -> TransportSystem:
        try:
            root = ET.parse(path).getroot()
        except (OSError, ET.ParseError) as exc:
            raise StorageError(f"Не удалось прочитать файл: {exc}") from exc
        try:
            return TransportSystem.from_dict(self._to_dict(root))
        except (KeyError, AttributeError, TypeError, ValueError,
                TransportError) as exc:
            raise StorageError(f"Неверные данные в файле: {exc}") from exc

    @staticmethod
    def _to_dict(root: ET.Element) -> dict[str, Any]:
        """Собирает из XML такой же словарь, как делает to_dict()."""
        routes = []
        for node in root.findall("routes/route"):
            vehicle = dict(node.find("vehicle").attrib)
            if "low_floor" in vehicle:
                vehicle["low_floor"] = vehicle["low_floor"] == "True"
            routes.append({
                "number": node.attrib["number"],
                "title": node.attrib["title"],
                "price": node.attrib["price"],
                "vehicle": vehicle,
                "stops": [dict(s.attrib) for s in node.findall("stops/stop")],
            })
        tickets = [{
            "id": node.attrib["id"],
            "route_number": node.attrib["route_number"],
            "price": node.attrib["price"],
            "passenger": dict(node.find("passenger").attrib),
        } for node in root.findall("tickets/ticket")]
        return {"next_ticket_id": root.attrib["next_ticket_id"],
                "routes": routes, "tickets": tickets}
