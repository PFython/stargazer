# `stargazer`
![Replace with your own inspirational logo here](https://media.giphy.com/media/W22c9OqIB2DsWFBCTr/giphy.gif)
# 1. OVERVIEW
`stargazer` is Python utility to scrape emails and names of Github users ('Stargazers') who have starred a particular repository you might be interested in.  It includes a general purpose `Repository` class and (Github) `User` class for people to build on if they wish.  No need for tokens, OAuth or any API knowledge or setup.

# 2. INSTALLATION

Clone/Fork/Download etc. from https://github.com/PFython/stargazer.

# 3. BASIC USE

```
>>> from stargazer import *
>>> start()

# Enter your Github username and password, and the repository to scrape
# Wait for selenium to do its thing...

# When you see the command prompt again, you can get all emails with:
>>> repo.emails()

# And optionally change the separator and/or save to the clipboard:
>>> repo.emails(copy=True, separator=",")

# User information can easily be obtained with list comprehensions:
>>> [user.name for user in repo.stargazers]

# A list of all Repositories and Users is kept in .index
>>> [user.url for user in User.index]
...
>>> [repository.stargazers_url for repository in Repository.index]

```

# 4. UNDER THE BONNET
`stargazer` uses `selenium` and `cleverdict` behind the scenes, and `PySimpleGUI` for input prompts.

`chomedriver.exe` is included in this repository but you can replace with the relevant `selenium` web-driver for your preferred browser.  Please see `selenium` docs/tutorials widely available elsewhere.

Hopefully `stargazer` will be of interest to people getting started with `selenium` and web scraping generally.  It's not super elegant or even PEP8 compliant, but does show how a simple web scraping challenge can be met quickly, understandably, and extensibly.

# 5. CONTRIBUTING

Contact Peter Fison peter@southwestlondon.tv or raise Pull Requests / Issue in the normal Github way.

# 6. PAYING IT FORWARD


If `stargazer` helps you save time and focus on more important things, please feel free to to show your appreciation by starring the repository on Github.

I'd also be delighted if you wanted to:

<a href="https://www.buymeacoffee.com/pfython" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/arial-yellow.png" alt="Buy Me A Coffee" width="217px" ></a>
