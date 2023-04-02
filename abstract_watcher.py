import abc
from typing import Coroutine, Any
import asyncio

"""
Описание задачи:
    Необходимо реализовать планировщик, позволяющий запускать и отслеживать фоновые корутины.
    Планировщик должен обеспечивать:
        - возможность планирования новой задачи
        - отслеживание состояния завершенных задач (сохранение результатов их выполнения)
        - отмену незавершенных задач перед остановкой работы планировщика
        
    Ниже представлен интерфейс, которому должна соответствовать ваша реализация.

    Обратите внимание, что перед завершением работы планировщика, все запущенные им корутины должны быть
    корректным образом завершены.

    В папке tests вы найдете тесты, с помощью которых мы будем проверять работоспособность вашей реализации
"""


class AbstractRegistrator(abc.ABC):
    """
    Сохраняет результаты работы завершенных задач.
    В тестах мы передадим в ваш Watcher нашу реализацию Registrator и проверим корректность сохранения результатов.
    """

    def __init__(self):
        self.values = []
        self.errors = []

    @abc.abstractmethod
    def register_value(self, value: Any) -> None:
        # Store values returned from done task
        self.values.append(value)

    @abc.abstractmethod
    def register_error(self, error: BaseException) -> None:
        # Store exceptions returned from done task
        self.errors.append(error)


class AbstractWatcher(abc.ABC):
    """
    Абстрактный интерфейс, которому должна соответсвовать ваша реализация Watcher.
    При тестировании мы расчитываем на то, что этот интерфейс будет соблюден.
    """

    def __init__(self, registrator: AbstractRegistrator):
        self.registrator = registrator  # we expect to find registrator here

    @abc.abstractmethod
    async def start(self) -> None:
        # Good idea is to implement here all necessary for start watcher :)
        ...

    @abc.abstractmethod
    async def stop(self) -> None:
        # Method will be called on the end of the Watcher's work
        ...

    @abc.abstractmethod
    def start_and_watch(self, coro: Coroutine) -> None:
        # Start new task and put to watching
        ...


class StudentWatcher(AbstractWatcher):
    def __init__(self, registrator: AbstractRegistrator):
        super().__init__(registrator)
        # Your code goes here
        self.tasks = set()

    async def start(self) -> None:
        # Your code goes here

        # чуть спим, чтобы отдать акцент
        await asyncio.sleep(1)
        if len(self.tasks) > 0:
            # отбираем выполненные задачи
            done, pending = await asyncio.wait(self.tasks, timeout=0.1)

            # по выполненым задачам записываем результат или ошибку и удаляем из сета задач
            for task in done:
                try:
                    res = task.result()
                    self.registrator.register_value(res)
                except ValueError as ve:
                    self.registrator.register_error(ve)
                finally:
                    self.tasks.remove(task)

    async def stop(self) -> None:
        # Your code goes here
        # опять спим (может и лишнее это)
        await asyncio.sleep(1)
        for task in self.tasks:
            # пробуем узнать результат
            try:
                res = task.result()
                self.registrator.register_value(res)
            except ValueError as ve:
                self.registrator.register_error(ve)
            # в итоге завершаем задачу
            task.cancel()

    def start_and_watch(self, coro: Coroutine) -> None:
        # Your code goes here
        # Создаю корутину и запускаю в фоне выполнение
        task = asyncio.create_task(coro)

        # Добавляю в сет задач
        self.tasks.add(task)
