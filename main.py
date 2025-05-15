from time import sleep
from utils.func import MeroShareBot
from utils.file_reader import file_reader
from utils.input_parser import input_parser
from termcolor import cprint
import ssl

try:
    import certifi
    ssl._create_default_https_context = ssl._create_unverified_context
except ImportError:
    pass
# Read and parse input data
input_file = file_reader('demats.txt')
demats = input_parser(input_file)

# Banner Display
print("""
-----------------------------------------------------------------------------------------

    ██╗██████╗  ██████╗     ██████╗  ██████╗ ████████╗
    ██║██╔══██╗██╔═══██╗    ██╔══██╗██╔═══██╗╚══██╔══╝
    ██║██████╔╝██║   ██║    ██████╔╝██║   ██║   ██║   
    ██║██╔═══╝ ██║   ██║    ██╔══██╗██║   ██║   ██║   
    ██║██║     ╚██████╔╝    ██████╔╝╚██████╔╝   ██║   
    ╚═╝╚═╝      ╚═════╝     ╚═════╝  ╚═════╝    ╚═╝   
-----------------------------------------------------------------------------------------
Author: Ashish Adikhari 
Github repository: https://github.com/adk-ashish/ipo-bot
-----------------------------------------------------------------------------------------
""")

try:
    number_of_accounts = len(demats)
    print(f'[INFO] Number of accounts detected: {number_of_accounts}')

    # Start bot instance with headless=False (change to True if you want headless)
    bot = MeroShareBot(headless=False)

    # Login using the first account to list available IPOs
    name, dp_id, username, password, crn, txn_pin = demats[0]

    try:
        bot.login(dp_id, username, password)

        while bot.driver.current_url != "https://meroshare.cdsc.com.np/#/dashboard":
            sleep(1)

    except Exception:
        cprint('[ERROR] Could not login with first account. Please try again.', 'red')
        bot.quit_browser()
        exit(1)

    bot.goto_asba()
    bot.open_ipo_lister()

except Exception as e:
    cprint(f'[ERROR] {e}', 'red')
    try:
        bot.quit_browser()
    except Exception:
        pass
    exit(1)

# User input
try:
    share = int(input('Enter the IPO index number to apply: '))
    number_kitta = int(input('Enter the number of units (kitta) to apply: '))
except ValueError:
    cprint('[ERROR] Invalid input. Please enter numeric values.', 'red')
    bot.quit_browser()
    exit(1)

# Apply IPO for all accounts
try:
    for account in demats:
        name, dp_id, username, password, crn, txn_pin = account

        try:
            bot.login(dp_id, username, password)

            while bot.driver.current_url != "https://meroshare.cdsc.com.np/#/dashboard":
                sleep(1)

        except Exception:
            cprint(f'[WARNING] Could not login for {name}. Skipping...', 'yellow')
            continue

        cprint(f"[INFO] Applying {number_kitta} kitta IPO with {name}'s account...", 'cyan')
        bot.goto_asba()
        sleep(1)

        try:
            bot.ipo_selector(share)
        except Exception:
            cprint(f"[WARNING] Already applied for this IPO from {name}'s account", 'red')
            continue

        sleep(1)
        bot.apply_ipo(number_kitta, crn, txn_pin)
        sleep(1)

    cprint("[SUCCESS] Finished IPO applications.", 'green')
    bot.quit_browser()

except Exception as e:
    cprint(f'[ERROR] {e}', 'red')
    bot.quit_browser()
    exit(1)
