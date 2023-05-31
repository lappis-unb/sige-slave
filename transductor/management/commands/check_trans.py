import logging
import threading
import time

from django.core.management.base import BaseCommand
from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

from transductor.models import Transductor

logger = logging.getLogger("tasks")


class Command(BaseCommand):
    help = "Test all transducers."

    def handle(self, *args, **options) -> None:
        start_time = time.perf_counter()
        logger.info("-" * 65)
        logger.info("# Command - Test all transducers.")
        broken_transductors = Transductor.objects.filter(broken=True)

        if not broken_transductors:
            logger.info("No broken transducers to test.")
            return

        threads = []
        for transductor in broken_transductors:
            thread = threading.Thread(target=self.test_transductor, args=(transductor,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        elapsed_time = time.perf_counter() - start_time
        logger.info(f"Execution time: {elapsed_time:.2f} seconds")

    def test_transductor(self, transductor: Transductor) -> None:
        """Tests the connection to a transducer."""

        ip, port = transductor.ip_address, transductor.port

        try:
            with ModbusTcpClient(ip, port):
                logger.info(f"Successfully connected to transducer at: {ip}:{port}.")

                if transductor.broken:
                    self.activate_transductor(transductor)

        except ConnectionException:
            logger.error(f"Connection FAILED to transducer at: {ip}:{port}")

            if transductor.active:
                self.deactivate_transductor(transductor)

        finally:
            transductor.save()

    def activate_transductor(self, transductor: Transductor) -> None:
        logger.info(f"Activated transducer: {transductor.ip_address}:{transductor.port}.")
        transductor.active = True
        transductor.broken = False

    def deactivate_transductor(self, transductor: Transductor) -> None:
        logger.error(f"Disabled transducer: {transductor.ip_address}:{transductor.port}")
        transductor.broken = True
        transductor.active = False
