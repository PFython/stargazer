# `stargazer`
![Replace with your own inspirational logo here](https://media.giphy.com/media/W22c9OqIB2DsWFBCTr/giphy.gif)
# 1. OVERVIEW
`stargazer` is Python utility to scrape emails and names of Github users ('Stargazers') who have starred a particular repository you might be interested in.  It includes a general purpose `Repository` class and (Github) `User` class for people to build on if they wish.  No need for tokens, OAuth or any API knowledge or setup.

# 2. INSTALLATION

Clone/Fork/Download etc. from https://github.com/PFython/stargazer.

# 3. BASIC USE

    >>> from stargazer import start, Session
    >>> start()

Enter your Github username and password, and the repository to scrape.  Wait for selenium to do its thing...

When you see the command prompt again, you can access your repository data (and any other repositories you've createed in the same session) as follows:

    >>> repo = Session.repo

From there you can access all the repository attributes, methods, & properties e.g.

    >>> repo.save_file()
    ...
    >>> repo.info()
    ...
    >>> repo.emails()
    ...
    >>> repo.to_json()

The `emails` and `twitter` methods allow you to change the separator and/or save output to the clipboard:

    >>> repo.twitter(copy=True, separator=",")

The `.stargazers` attribute holds a dictionary of `User` objects.  Their details can be easily obtained with list comprehensions:

    >>> [user.name for user in repo.stargazers.values()]

And the `User` class has its own `.index` just like the `Repository` class:

    >>> from stargazser import User, Repository
    >>> [user.url for user in User.index.values()]
    ...
    >>> [repository.stargazers_url for repository in Repository.index.values()]

If you want to scrape another `Repository`, just use the `start()` function again and enter a new repository url or user_name/repo_name.


# 4. UNDER THE BONNET
`stargazer` uses `selenium` for web-scraping, `cleverdict` for data management, and `PySimpleGUI` for quick and easy input prompts.

`chomedriver.exe` is included in this repository but you can replace with the latest `selenium` web-driver for your preferred browser.  Please see `selenium` docs/tutorials widely available elsewhere.



Earlier versions of `stargazer` used `BeautifulSoup` but with a little extra work I'm please to say it now works using just `selenium`.

# 5. CONTRIBUTING

Hopefully `stargazer` will be of interest to people getting started with `selenium` and web scraping generally or working with Github and not wanting to use their API.  `stargazer` isn't super elegant or even PEP8 compliant, but does show how a simple web scraping challenge can be met quickly, understandably, and extensibly.

Contact Peter Fison peter@southwestlondon.tv or feel free to raise Pull Requests / Issue in the normal Github way.

# 6. PAYING IT FORWARD


If `stargazer` helps you save time and focus on more important things, please feel free to to show your appreciation by starring the repository on Github.

I'd also be delighted if you wanted to:

<a href="https://www.buymeacoffee.com/pfython" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/arial-yellow.png" alt="Buy Me A Coffee" width="217px" ></a>
