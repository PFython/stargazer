"""
Finds Github "Stargazers" (people who have starred a particular repository) and scrapes their email address, name, and Twitter handle if published.
"""
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import webbrowser
import PySimpleGUI as sg
from pathlib import Path
from cleverdict import CleverDict
import pyperclip
import inspect

class User(CleverDict):
    index = {}
    def __init__(self, name, **kwargs):
        # name format can be:
        # "Pfython" or "https://github.com/PFython"
        super().__init__(**kwargs)
        self.user_name = name.split("/")[-1]
        User.index[self.user_name] = self

    @property
    def url(self):
        return f"https://github.com/{self.user_name}"

class Repository(CleverDict):
    index = {}

    def __init__(self, full_name, **kwargs):
        """
        Required argument 'full_name'.
        Format can be either:
        'Pfython/CleverDict' or
        'https://github.com/PFython/easypypi'
        """
        super().__init__(**kwargs)
        try:
            user_name, repo_name = full_name.split("/")[-2:]
            self.id = f"{user_name}/{repo_name}"
            self.user_name, self.repo_name = self.id.split("/")
            self.stargazers = {}
            self.save_path_str = f"stargazers-{self.id}.json"
        except ValueError:
            print("\n⚠   Object not properly created.")
            print(Repository.__init__.__doc__)
            return
        Repository.index[self.id] = self

    def emails(self, **kwargs):
        """
        Returns a string of emails and optionally copies to clipboard
        Default format suitable for pasting into MS-Outlook for example
        """
        separator = kwargs.get("separator")
        if not separator:
            separator = ";"
        emails = separator.join([x.email for x in self.stargazers.values() if x.get("email")])
        if kwargs.get("copy"):
            pyperclip.copy(emails)
        return emails

    def twitter(self, **kwargs):
        """
        Returns a string of Twitter IDs and optionally copies to clipboard
        """
        separator = kwargs.get("separator")
        if not separator:
            separator = ";"
        ids = separator.join([x.twitter for x in self.stargazers.values() if x.get("twitter")])
        if kwargs.get("copy"):
            pyperclip.copy(ids)
        return ids

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

    def save_file(self):
        pass

def timer(func):
    """
    Starts the clock, runs func(), stops the clock. Simples.
    Designed to work as a decorator... just put @timer in front of
    the original function.
    """
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        data = func(*args, **kwargs)
        print(f"Function {func.__name__!r} took {round(time.perf_counter()-start,2)} seconds to complete.\n")
        return (data)
    return wrapper

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
        id = ids[0] if len(ids) == 1 else "/".join(ids)
        print(f"\nⓘ Saved '{id}' in JSON format to:\n {path.absolute()}")
    return json_str

def save(self, name, value):
    """ Generic auto-save confirmation applied CleverDict """
    id = self.get("id") or self.get("user_name")
    # .id for Repository objects, .user_name for User objects
    print(f" ⓘ  {type(self).__name__}.index['{id}'].{name} = {value} {type(value)}")

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

@timer
def get_input():
    global repo_url, repo, username, password
    repo_url = "https://github.com/qmasingarbe/pymiere"
    repo = Repository(sg.popup_get_text("Please enter a Repository ID in the format 'user_name/repo_name':", default_text=globals().get("repo_url"), **sg_kwargs))
    username = sg.popup_get_text(f"Please enter your GitHub username: ", default_text=globals().get("username"), **sg_kwargs,)
    password = sg.popup_get_text(f"Please enter your GitHub password: ", password_char="*", default_text=globals().get("password"), **sg_kwargs,)

@timer
def start_webbrowser():
    global browser
    browser = webdriver.Chrome()
    browser.implicitly_wait(3)
    browser.get("https://github.com/login")
    browser.find_element_by_id("login_field").send_keys(username)
    browser.find_element_by_id("password").send_keys(password)
    browser.find_element_by_name("commit").click()
    browser.get(repo.stargazers_url)

@timer
def loop_through_stargazers():
    """ Opens all Stargazer results pages in turn and calls scraper function """
    while True:
        try:
            a_tags = browser.find_elements_by_tag_name("a")
            users = [a.text for a in a_tags if a.get_attribute('data-hovercard-url')]
            repo.stargazers.update({u: User(u) for u in users if u})
            # Reveal NEXT button by scrolling to end of page:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            browser.find_element_by_link_text("Next").click()

        except WebDriverException:
            print("\n  ⓘ Last results page processed.")
            break

@timer
def loop_through_profiles():
    browser.implicitly_wait(0)  # No wait e.g. for null values in Loop below
    for user in repo.stargazers.values():
        browser.get(user.url)
        # GET EMAIL / TWITTER
        at = browser.find_elements_by_partial_link_text("@")
        for result in at:
            prefix, suffix = result.text.split("@")
            if prefix:
                user.email = result.text
            else:
                user.twitter = result.text
        # GET NAME
        span = browser.find_elements_by_tag_name("span")
        user.name = [x.text for x in span if x.get_attribute('itemprop')=="name"][0]

@timer
def start():
    setattr(CleverDict, "to_json", to_json)
    setattr(CleverDict, "save", save)
    start_gui()
    get_input()
    start_webbrowser()
    loop_through_stargazers()
    loop_through_profiles()

if __name__ == "__main__":
    start()


# TODO: Repository.save_file
# TODO: Get websites, look for obvious contact email
# TODO: Auto-generate email based on template and repo.emails

