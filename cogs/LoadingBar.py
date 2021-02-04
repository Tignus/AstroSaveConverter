import time

class LoadingBar:
    """The Loading Bar Class.

        This object represents a Loading Bar

        Attributes:
            time -- The number of seconds to fully complete the loading bar
            bar_count -- The number of rectangles to display when the bar is fully completed
            update_period -- The amount of time to wait between each rectangle

        Methods:
            start_loading() -- Start the loading bar process
            clean_bar() -- Remove the bar from the console
            print_bar(progress) -- Print the bar with the progress specified
    """
    time = 0
    __bar_count = 20
    __update_period = 0

    def __init__(self, time):
        """Initiates a loading bar object

        Arguments:
            time -- Time in seconds to fully complete the loading bar

        Returns:
            The Loading Bar

        Exception:
            None
        """
        self.time = time
        self.__update_period = time/self.__bar_count

    def start_loading(self):
        
        # Print initial bar
        print("[", end='')
        for i in range(self.__bar_count):
            print(" ", end='')
        print("]", end='', flush=True)

        # For each bar, wait the amount of time needed, wipe the bar and print the new one
        for i in range(self.__bar_count):
            time.sleep(self.__update_period)
            self.clean_bar()
            self.print_bar(i)

    def clean_bar(self):
        for i in range(self.__bar_count+2):
            print("\b", end='')
        print("", end='', flush=True)

    def print_bar(self, progress):
        print("[", end='')
        for i in range(self.__bar_count):
            if progress >= i:
                print("■", end='')
            else:
                print(" ", end='')
        print("]", end='', flush=True)
