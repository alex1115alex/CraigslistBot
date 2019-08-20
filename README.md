# CraigslistBot #

This script was made to automate an affiliate marketing method I found. It takes in a list of listings, and posts them to Craigslist. Alternatively, you can use a list of Amazon links, and the script can post copies of those Amazon product pages to Craigslist. 

### How to use ###

Create a new ProtonMail account, and create a folder called craigslistBotFolder. This is the only folder you should have. I use ProtonMail for email verification for login and posting.

Copy your Amazon product page links into your Amazon links file (one link per line). 

Then, call the bot like this:

```
python Run.py "ProtonLogin" "ProtonPassword" "CraigslistEmail" "CraigslistPassword" "Contact Phone Number" "ContactName" "Zip Code" "Amazon Links File Path" int(TimeDelay) int(TimeDelayBetweenPosts)
```

Example:
```
python Run.py "example@protonmail.com" "password" "example@protonmail.com" "password" "8475551234" "Mick Smithing" "69420" "links.txt" 4 60
```

### Requirements ###

* Amazonify
* Shutil
* Selenium
* FireFox
* PyVirtualDisplay
* Spintax
* Python 2.7
