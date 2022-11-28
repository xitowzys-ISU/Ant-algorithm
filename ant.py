import sys
from typing import Any
from loguru import logger


def logger_configuration(level: str = "DEBUG") -> None:

    logger.remove()

    logger.level("ERROR")

    logger.add(
        sys.stdout, level=level, colorize=True, format="(<level>{level}</level>) [<green>{time:HH:mm:ss}</green>] ➤ <level>{message}</level>")


class Ant():
    def __init__(self, path_file: str, epochs: int) -> None:
        self.__path_file: str = path_file
        self.__epochs: int = epochs

        self.__constant: float = 2
        self.__e: float = 0.6

        self.__start: int = 0
        self.__end: int = 0
        self.__nodes: dict[Any, Any] = {}
        self.__all_paths: list[list[list[str | int]]] = []

        self.__ants: dict[str, float] = {}
        self.__paths_lengths: dict[str, int] = {}

        self.__roads: dict[str, float] = {}

    def run(self) -> None:
        self.__read_file()
        self.__all_path()
        self.__paths_length()
        self.__search_roads()

    def __read_file(self) -> None:

        with open(self.__path_file) as file:
            for line in file:
                arr: list[int] = [int(i) for i in line.split()]
                if len(arr) < 3:
                    self.__start = int(arr[0])
                    self.__end = int(arr[1])
                else:
                    if arr[0] in self.__nodes:
                        self.__nodes[arr[0]].append([arr[1], arr[2]])
                    else:
                        self.__nodes[arr[0]] = [[arr[1], arr[2]]]

        self.__nodes = {key: self.__nodes[key]
                        for key in sorted(self.__nodes.keys())}

        logger.info(f"Начало пути: {self.__start}")
        logger.info(f"Конец пути: {self.__end}\n{'-' * 40}")

        logger.debug(f"{self.__start}, {self.__end}, {self.__nodes}")

    # Проверка существует ли уже путь в массиве
    def __check(self, arr: list[Any]) -> bool:
        is_final: bool = True
        for i in arr:
            if i[0][-1] == str(self.__end):
                continue
            else:
                is_final = False
                break
        return is_final

    # Поиск всех возможных путей
    def __all_path(self) -> None:
        for i in self.__nodes[self.__start]:
            length_0 = i[1]
            path_0: str = str(self.__start) + str(i[0])
            paths: list[list[str | int]] = [[path_0, length_0]]
            while not self.__check(paths):
                newpaths = []
                for j in paths:
                    path: str | int = j[0]
                    length: str | int = j[1]
                    last_node: int = int(j[0][-1])
                    if last_node == self.__end:
                        newpaths.append([path, length])
                    else:
                        for k in self.__nodes[last_node]:
                            path += str(k[0])
                            newpaths.append([path, length + k[1]])
                            path = path[:-1]
                    paths = newpaths
            self.__all_paths.append(paths)

    def __paths_length(self) -> None:
        for i in self.__all_paths:
            for j in i:

                # Создаем муравьи и количество феромонов который он откладывает
                self.__ants[j[0]] = self.__constant / j[1]
                self.__paths_lengths[j[0]] = j[1]

    def __search_roads(self) -> None:
        for i in self.__nodes:
            for j in self.__nodes[i]:
                self.__roads[str(i) + str(j[0])] = 1.0

        for _ in range(self.__epochs):

            # Испарение феромона
            for road in self.__roads:
                self.__roads[road] *= self.__e

            # Обновление феромона
            for ant_way in self.__ants:
                for i in range(len(ant_way)-1):
                    self.__roads[ant_way[i] + ant_way[i+1]
                                 ] += self.__ants[ant_way]

        self.__roads = {k: v for k, v in sorted(
            self.__roads.items(), key=lambda item: item[1], reverse=True)}

    def print_result(self) -> None:
        for _ in range(len(self.__nodes[self.__start])):
            way: str = ""

            for road in self.__roads:
                if road[0] == str(self.__start):
                    way += road
                    break

            self.__roads.pop(way)

            while way[-1] != str(self.__end):
                for road in self.__roads:
                    if road[0] == way[-1]:
                        way += road[1]
                        continue

            logger.success(
                f"\nЛучший путь {way}\nДлина пути: {self.__paths_lengths[way]}\n{'-' * 40}")


if __name__ == "__main__":
    logger_configuration(level="INFO")

    ant: Ant = Ant(path_file="./graph.txt", epochs=100)

    ant.run()
    ant.print_result()
