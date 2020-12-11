"""
Scrapes Github "Users" (people who have starred a particular repository) and scrapes email addresses.
"""
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import webbrowser
import bs4
import PySimpleGUI as sg
from pathlib import Path
from cleverdict import CleverDict
import pyperclip

def start_gui(**kwargs):
    """
    Toggles between normal output and routing stdout/stderr to PySimpleGUI
    """
    # Global keyword arguments for PySimpleGUI popups:
    global sg_kwargs
    sg_kwargs = {
        "title": "User",
        "keep_on_top": True,
        # "icon": Path(__file__).parent.parent / "easypypi.ico",
    }
    if kwargs.get("redirect"):
        global print
        print = sg.Print
    sg.change_look_and_feel("DarkAmber")
    # Redirect stdout and stderr to Debug Window:
    sg.set_options(
        message_box_line_width=80,
        debug_win_size=(100, 30),
    )
    options = {"do_not_reroute_stdout": False, "keep_on_top": True}

def to_json(self, never_save = False, **kwargs):
    """
    Return CleverDict serialised to JSON.

    KWARGS
    never_save: Exclude field in CleverDict.never_save if True eg passwords
    file: Save to file if True or filepath

    """
    # .get_aliases finds attributes created after __init__:
    fields_dict = {key: self.get(key) for key in self.get_aliases()}
    if never_save:
        fields_dict = {k:v for k,v in fields_dict if k not in never_save}
    json_str = json.dumps(fields_dict)
    path = kwargs.get("file")
    if path:
        path = Path(path)
        with path.open("w") as file:
            file.write(json_str)
        # if CleverDict.save is not CleverDict.save_value_to_json_file:
        #     # Avoid spamming confirmation messages
        frame = inspect.currentframe().f_back.f_locals
        ids = [k for k, v in frame.items() if v is self]
        ids = ids[0] if len(ids) == 1 else "/".join(ids)
        print(f"\nⓘ Saved '{ids}' in JSON format to:\n {path.absolute()}")
    return json_str

setattr(CleverDict, "to_json", to_json)

class User(CleverDict):
    index = []
    def __init__(self, name, **kwargs):
        # name format can be:
        # "Pfython" or "https://github.com/PFython"
        super().__init__(**kwargs)
        self.name = name.split("/")[-1]
        User.index.append(self)

    @property
    def url(self):
        return f"https://github.com/{self.name}"

class Repository(CleverDict):
    index = []
    def __init__(self, full_name, **kwargs):
        """
        Required argument 'full_name'.
        Format can be either:
        'Pfython/CleverDict' or
        'https://github.com/PFython/easypypi'
        """
        super().__init__(**kwargs)
        try:
            self.user_name, self.repo_name = full_name.split("/")[-2:]
            self.id = f"{self.user_name}/{self.repo_name}"
            self.stargazers = []
            self.save_path_str = f"stargazers-{self.id}.json"
        except ValueError:
            print("\n⚠   Object not properly created.")
            print(Repository.__init__.__doc__)
            return
        Repository.index.append(self)

    def emails(self, **kwargs):
        """
        Returns a string of emails and optionally copies to clipboard
        Default format suitable for pasting into MS-Outlook for example
        """
        separator = kwargs.get("separator")
        if not separator:
            separator = ";"
        emails = separator.join([x.email for x in self.stargazers if x.get("email")])
        if kwargs.get("copy"):
            pyperclip.copy(emails)
        return emails

    @property
    def save_path(self):
        """
        JSON doesn't support pathlib objects so we use .save_pathr_str
        as the main attribute.  This @property returns the corresponding Path.
        """
        return Path(self.save_path_str)

    @property
    def url(self):
        return f"https://github.com/{self.id}"

    @property
    def stargazers_url(self):
        return f"https://github.com/{self.id}/stargazers"

    def save(self, name, value):
        print(f" ⓘ  .{name} set to: {value}")

    def save_file(self):
        pass  # TODO


# SETUP
start_gui()
username = sg.popup_get_text(f"Please enter your GitHub username: ", default_text=globals().get("username"), **sg_kwargs,)
password = sg.popup_get_text(f"Please enter your GitHub password: ", password_char="*", default_text=globals().get("password"), **sg_kwargs,)
repo = Repository(sg.popup_get_text("Please enter a Repository ID in the format 'user_name/repo_name':", default_text="PFython/cleverdict"))
browser = webdriver.Chrome()
browser.implicitly_wait(10)

# LOG IN
browser.get("https://github.com/login")
browser.find_element_by_id("login_field").send_keys(username)
browser.find_element_by_id("password").send_keys(password)
browser.find_element_by_name("commit").click()

# GET STARGAZERS
browser.get(repo.stargazers_url)
a_tags = bs4.BeautifulSoup(browser.page_source, "html.parser").find_all("a")
key = 'data-hovercard-url'
users = {x.attrs[key].split("/")[2] for x in a_tags if key in x.attrs}
repo.stargazers.extend([User(u) for u in users])

# LOOP THROUGH PROFILES
for user in repo.stargazers:
    browser.get(user.url)
    soup = bs4.BeautifulSoup(browser.page_source, "html.parser")
    # GET EMAIL
    a_tags = soup.find_all("a")
    email = [x['href'] for x in a_tags if "mailto" in x.get('href')]
    user.email = email[0].split("mailto:")[1] if email else ""
    # GET NAME
    span = soup.find_all("span")
    user.name = [x for x in span if x.get('itemprop')=="name"][0].text
