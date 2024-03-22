from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frinx.client.v2.frinx_conductor_wrapper import FrinxConductorWrapper

from frinx.common.worker.worker import WorkerImpl


class ServiceWorkersImpl:
    """A class representing a collection of service workers.

    This class provides methods to manage and work with a list of `WorkerImpl` instances
    representing various service workers.

    Attributes:
        service_workers (list[WorkerImpl]): A list of `WorkerImpl` instances representing
            service workers.
    """

    def __init__(self) -> None:
        """Initialize a new ServiceWorkersImpl instance."""
        self.service_workers = self._inner_class_list()

    def tasks(self) -> list[WorkerImpl]:
        """Get the list of service workers.

        Returns:
            list[WorkerImpl]: A list of `WorkerImpl` instances representing service workers.
        """
        return self.service_workers

    def register(self, conductor_client: FrinxConductorWrapper) -> None:
        """Register service workers with the conductor client.

        This method iterates through the list of service workers and registers them
        with the provided `conductor_client`.

        Args:
            conductor_client (FrinxConductorWrapper): An instance of the FrinxConductorWrapper
                used for registration.

        Returns:
            None
        """
        for task in self.service_workers:
            task.register(conductor_client)

    @classmethod
    def _inner_class_list(cls) -> list[WorkerImpl]:
        """Get a list of instantiated WorkerImpl subclasses.

        This method scans the class attributes for subclasses of `WorkerImpl` and returns
        a list of instances of those subclasses.

        Returns:
            list[WorkerImpl]: A list of instantiated `WorkerImpl` subclasses found in the class.
        """
        results = []

        for attr_name in dir(cls):
            obj = getattr(cls, attr_name)
            if isinstance(obj, type) and issubclass(obj, WorkerImpl):
                task = obj()
                results.append(task)
        return results
