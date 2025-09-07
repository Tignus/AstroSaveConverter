"""Console loading bar utility."""

import time


class LoadingBar:
    """Simple text-based loading bar."""

    time = 0
    __bar_count = 20
    __update_period = 0

    def __init__(self, time: int) -> None:
        """Initialize a loading bar.

        Args:
            time: Seconds to fully complete the loading bar.
        """
        self.time = time
        self.__update_period = time / self.__bar_count

    def start_loading(self) -> None:
        """Animate the loading bar until completion."""

        print("[", end='')
        for _ in range(self.__bar_count):
            print(" ", end='')
        print("]", end='', flush=True)

        for i in range(self.__bar_count):
            time.sleep(self.__update_period)
            self.clean_bar()
            self.print_bar(i)

    def clean_bar(self) -> None:
        """Remove the bar from the console."""
        for _ in range(self.__bar_count + 2):
            print("\b", end='')
        print("", end='', flush=True)

    def print_bar(self, progress: int) -> None:
        """Print the bar with a given progress state."""
        print("[", end='')
        for i in range(self.__bar_count):
            if progress >= i:
                print("■", end='')
            else:
                print(" ", end='')
        print("]", end='', flush=True)
