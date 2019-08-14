class Listing:
    def __init__(self, name, description, link, imagePathList):
        self.name = name
        self.description = description + "\n\n" + "Hi, I posted it on Amazon beacuse it's more secure and " \
                                                  "you get free shipping! Buy it here: " + link;
        # self.link = link
        self.imagePathList = imagePathList

    def tostring(self):
        return "Listing Name: " + self.name + "\nDescription: " + self.description

