"""
Finds Github "Stargazers" (people who have starred a particular repository) and scrapes their email address, name, and Twitter handle if published.
"""

from pathlib import Path
from cleverdict import CleverDict
import pyperclip
from selenium.common.exceptions import WebDriverException
from cleverutils import CleverSession
from cleverutils.clevergui import text_input, get_folder
from cleverutils.cleverutils import to_json, timer, get_time

class User(CleverDict):
    index = {}
    def __init__(self, name, **kwargs):
        # name format can be:
        # "Pfython" or "https://github.com/PFython"
        super().__init__(**kwargs)
        self.title = "Github User"
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
            user_name, repo_name = full_name.lower().split("/")[-2:]
            self.title = "Github Repository"
            self.id = f"{user_name}/{repo_name}"
            self.user_name, self.repo_name = self.id.split("/")
            self.stargazers = {}
            self.dirpath = kwargs.get("dirpath") or Path().cwd()
        except ValueError:
            print("\n ⚠  Object not properly created.")
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
    def file_path(self):
        """
        File path of JSON file to save to.
        """
        path_str = f'{self.id.replace("/", "-")}-{get_time()}.json'
        return Path(path_str)

    @property
    def url(self):
        return f"https://github.com/{self.id}"

    @property
    def stargazers_url(self):
        return f"https://github.com/{self.id}/stargazers"

    def save_file(self):
        dirpath = get_folder("Please select a folder to save your Repository data to:", default_path=self.dirpath)
        if not dirpath:  # input = None if cancelled, "" if blank.
            return
        self.dirpath = Path(dirpath)
        self['url'] = self.url
        self['stargazers_url'] = self.stargazers_url
        self.to_json(file=self.dirpath/self.file_path)

class Session(CleverSession):
    def __init__(self, **kwargs):
        kwargs.update({"url": "https://github.com/login"})
        super().__init__(**kwargs)
        self.repo = Repository(text_input("Please enter a Repository ID in the format 'user_name/repo_name':", default_text="https://github.com/pfython/cleverdict"), dirpath=self.dirpath)

    @timer
    def loop_through_stargazers(self):
        """ Opens all Stargazer results pages in turn and calls scraper function """
        while True:
            try:
                a_tags = self.browser.find_elements_by_tag_name("a")
                users = [a.text for a in a_tags if a.get_attribute('data-hovercard-url')]
                self.repo.stargazers.update({u: User(u) for u in users if u})
                # Reveal NEXT button by scrolling to end of page:
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.browser.find_element_by_link_text("Next").click()
            except WebDriverException:
                print("\n ✓  Last results page processed.")
                self.repo.last_updated = get_time()
                break

    @timer
    def loop_through_profiles(self):
        self.browser.implicitly_wait(0)  # No wait e.g. for null values in Loop below
        for user in self.repo.stargazers.values():
            self.browser.get(user.url)
            # GET EMAIL / TWITTER
            at = self.browser.find_elements_by_partial_link_text("@")
            for result in at:
                prefix, suffix = result.text.split("@")
                if prefix:
                    user.email = result.text
                else:
                    if user.get('twitter'):
                        break
                    user.twitter = result.text
            # GET NAME
            span = self.browser.find_elements_by_tag_name("span")
            user.name = [x.text for x in span if x.get_attribute('itemprop')=="name"][0]
            user.last_updated = get_time()

@timer
def main():
    setattr(Repository, "to_json", to_json)
    self = Session()
    self.login_with_webbrowser(wait=0)
    self.browser.get(self.repo.stargazers_url)
    self.loop_through_stargazers()
    self.loop_through_profiles()
    self.repo.save_file()
    self.repo.emails(copy=True)
    print("\n ✓  Emails copied to clipboard.")

if __name__ == "__main__":
    main()

# TODO: GUI progress bar
# TODO: Multi-threading for greater speed
# TODO: Load repository from JSON
# TODO: User exclude list (e.g. deliberately invalid email addresses)
# TODO: Get websites, look for obvious contact email
# TODO: Auto-generate email based on template and repo.emails

