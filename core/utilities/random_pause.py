# Python imports
import time as t
import random as r

# Terminal color import
from colorama import Fore, Style


def random_pause(min_seconds=2, max_seconds=5):
    """Pause for a random duration to mimic human behavior."""
    pause_duration = r.uniform(min_seconds, max_seconds)
    print(f"{Fore.YELLOW}Pausing for {pause_duration:.2f} seconds...{Style.RESET_ALL}")
    t.sleep(pause_duration)
