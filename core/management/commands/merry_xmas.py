from django.core.management.base import BaseCommand
from colorama import Fore, Back, Style, init
import time
import random  # Import random for color selection


class Command(BaseCommand):
    help = "Display a festive Christmas tree with a Merry Christmas message"

    def draw_christmas_tree(self):
        tree = [
            "                    *                   ",
            "                   ***                  ",
            "                  *****                 ",
            "                 *******                ",
            "                ***o*****               ",
            "               ***********              ",
            "              *****o***o***             ",
            "             ***************            ",
            "            ****o************           ",
            "           **************o****          ",
            "          *********************         ",
            "         ***********************        ",
            "        ***********o*********o***       ",
            "       ********o******************      ",
            "      ************************o****     ",
            "     ******o******o*****************    ",
            "    ********************o************   ",
            "   ***********************************  ",
            "  *************o*********************** ",
            "                   |||                  ",
            "                   |||                  ",
        ]

        # Define colors for different parts of the tree
        star_color = Fore.YELLOW + Style.BRIGHT
        tree_color = Fore.GREEN
        trunk_color = Fore.RED
        ornament_colors = [Fore.RED, Fore.BLUE, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW]

        for line in tree:
            # Color the star
            if "*" in line and line.strip() == "*":
                print(star_color + line)
            # Color the tree
            elif "*" in line or "o" in line:
                decorated_line = ""
                for char in line:
                    if char == "*":
                        # Keep stars green
                        decorated_line += tree_color + "*"
                    elif char == "o":
                        # Randomly select a color for ornaments
                        decorated_line += random.choice(ornament_colors) + "o"
                    else:
                        # Preserve spaces and other characters
                        decorated_line += char
                print(decorated_line)
            # Color the trunk
            else:
                print(trunk_color + line)

    def display_message(self):
        message = "MERRY CHRISTMAS!"
        decorated_message = (
            Fore.WHITE
            + Back.RED
            + Style.BRIGHT
            + f"{message.center(40)}"
            + Style.RESET_ALL
        )
        print(decorated_message)

    def handle(self, *args, **options):
        # Initialize colorama
        init(autoreset=True)

        self.stdout.write(Fore.GREEN + "|            HO-HO-HO! 🎄            |")
        self.draw_christmas_tree()
        self.display_message()
