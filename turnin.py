import requests, re, getpass, sys
from bs4 import BeautifulSoup

def authenticate(username, password):
    r = requests.post("https://turnin.microlab.cs.utexas.edu/turnin/webturnin.dll/do_login", data={"username": username, "password": password, "originalURL": ""}, verify=False)
    return r.cookies

def get_classes(cookies):
    r = requests.get("https://turnin.microlab.cs.utexas.edu/turnin/webturnin.dll/home", cookies=cookies, verify=False)
    soup = BeautifulSoup(r.text)
    classes = []
    for c in soup.find_all("option"):
        classes.append(c.string)
        pass
    return classes

# Get the file list
def get_filelist(cookies):
    r = requests.get("https://turnin.microlab.cs.utexas.edu/turnin/webturnin.dll/home", cookies=cookies, verify=False)

    # Parse out the table
    soup = BeautifulSoup(r.text)
    rows = soup.find_all("table")[1].find_all("tr")
    files = []
    for r in rows[1:]:
        cells = r.find_all("td")
        #print cells
        if len(cells) > 2:
            files.append({"name": cells[0].a.string, "size": cells[1].string})
        pass
    return files
    return soup.find_all("table")

def upload(cookies, username, unique, filename):
    r = requests.post("https://turnin.microlab.cs.utexas.edu/turnin/webturnin.dll/upload", data={"class": unique, "user": username}, cookies=cookies, files={"file": open(filename)}, verify=False)
    return r.text
    pass

def login():
    cookies = {}
    while "TurninSession" not in cookies:
        username = raw_input("Username: ")
        password = getpass.getpass("Password: ")
        cookies = authenticate(username,password)
        #print dict(cookies)
        if "TurninSession" not in cookies:
            print "Authentication failed. Please try again."
            pass
        pass
    print "Authentication success!"
    return (username, cookies)

def printHelp():
    print "Usage:"
    print "%s upload <filename>"%sys.argv[0]

def main():
    if len(sys.argv) <= 1:
        printHelp()
        return

    (username, cookies) = login()

    #print get_filelist(r.cookies)
    #print upload(r.cookies)
    print "Fetching a list of your classes..."
    classes = get_classes(cookies)
    unique = None
    if len(classes) == 1:
        unique = classes[0]
        print "Selecting class %s"%unique
    elif len(classes) == 0:
        print "You have no classes!"
        return
    else:
        print "Multiple classes are not yet supported"
    print

    if sys.argv[1] == "upload":
        if len(sys.argv) < 3:
            print "Usage:"
            print "turnin.py upload <filename>"
            return
        filename = sys.argv[2]
        filelen = len(open(filename).read())

        print "Uploading %s (%i bytes)"%(filename, filelen)
        upload(cookies, username, unique, filename)

        print "Verifying upload..."
        files = get_filelist(cookies)
        for f in files:
            if f["name"] == filename:
                if int(f["size"]) != filelen:
                    print "*** WARNING: Uploaded file size != local file size ***"
                break
    elif sys.argv[1] == "list":
        print "Classes:"
        for c in classes:
            print " - %s"%c
        files = get_filelist(cookies)
        print
        print "Files:"
        for f in files:
            print " - %s"%f
    else:
        printHelp()
        return

if __name__ == "__main__":
    main()
