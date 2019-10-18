# pastebin-cloud V0.1
> unlimited space, slow traffic and service limitations.

## python api that allows you to upload files as pastes. this requires a pastebin username,password and a developer key.


### usage:

```python
import pastebincloud #import the api

mycloudobject = pastebincloud.Cloud("myusername","myuserpassword","mydeveloperkey") #creates an instance

print(mycloudobject.is_logged()) # boolean. True if logged in, False if not.

mycloudobject.print_list() # output a list of files that exist in that users pastebin

myfiles = mycloudobject.get_list() #returns the same list as string

time_delay = mycloudobject.delay() #returns how many seconds you are required to wait between pastes (premium user or not)

mycloudobject.upload("file path","upload name[optional]","private status[optional:0 default]")

#file path - the file path to upload from the local machine. (when uploading a file, the file will be converted into hex string
#                                                             and he will be divided (if necessary) into serval
#                                                             pastes according to the paste size limit.)
#upload name - [optional] the name of the paste, if not supplied the name will be the file name. 
#paste private status - 0 public, 1 unlisted, 2 private. if not supplied the default is 0.

mycloudobject.download("paste name","to path[optional]")

#paste name - the paste to download. (will download all pastes associated with 
#                                     that name in case of a file that is divided into
#                                     serval pastes)
#to path - the path to download to. if not supplied the default is the current working directory.

mycloudobject.delete("paste name")
#paste name - will delete all pastes associated with that name


```
### example:
```python
Python 3.6.6 |Anaconda 4.4.0 (64-bit)| (default, Jun 28 2018, 11:27:44) [MSC v.1900 64 bit (AMD64)]

Type "copyright", "credits" or "license" for more information.


IPython 6.5.0 -- An enhanced Interactive Python.


In [4]: import pastebincloud


In [7]:


In [7]: mycloud = pastebincloud.Cloud("user1","pass1234","455303f233cf7093db256f41fcff3f9g")


In [8]: mycloud.print_list()

Paste(s):                       date and time uploaded:


In [9]: mycloud.upload("Untitled2.png")

Untitled2.png consists of 2076252 byte(s). (after hex conversion)

limit per paste of 500000 byte(s).

required delay between pastes: 60 second(s).

uploading Untitled2.png in 5 paste(s):

estimated upload time: 245 second(s).

part - 1

uploaded successfully.

waiting 60 seconds (delay between pastes to prevent anti-spam protection).

part - 2

uploaded successfully.

waiting 60 seconds (delay between pastes to prevent anti-spam protection).

part - 3

uploaded successfully.

waiting 60 seconds (delay between pastes to prevent anti-spam protection).

part - 4

uploaded successfully.

waiting 60 seconds (delay between pastes to prevent anti-spam protection).

part - 5

uploaded successfully.

Out[9]: True


In [10]: mycloud.upload("test1.txt")

test1.txt consists of 38 byte(s). (after hex conversion)

limit per paste of 500000 byte(s).

required delay between pastes: 60 second(s).

uploading test1.txt in 1 paste(s):

estimated upload time: 1 second(s).

part - 1

uploaded successfully.

Out[10]: True


In [11]: mycloud.print_list()

Paste(s): date and time uploaded:

test1.txt 2018-09-08 18:28:55

Untitled2.png 2018-09-08 18:24:45

Untitled2.png paste continued part - 1

Untitled2.png paste continued part - 2

Untitled2.png paste continued part - 3

Untitled2.png paste continued part - 4


In [12]: mycloud.upload("test2.txt")

test2.txt consists of 48 byte(s). (after hex conversion)

limit per paste of 500000 byte(s).

required delay between pastes: 60 second(s).

uploading test2.txt in 1 paste(s):

estimated upload time: 1 second(s).

part - 1

uploaded successfully.

Out[12]: True


In [13]: mycloud.print_list()

Paste(s):                       date and time uploaded:

test2.txt                       2018-09-08 18:27:54

test1.txt                       2018-09-08 18:28:55

Untitled2.png                   2018-09-08 18:24:45

Untitled2.png paste continued part - 1

Untitled2.png paste continued part - 2

Untitled2.png paste continued part - 3

Untitled2.png paste continued part - 4


In [14]: mycloud.delete("test1.txt")

deleting test1.txt starting from instance 0.

test1.txt deleted successfully paste part: 1.


In [15]: mycloud.print_list()

Paste(s):                       date and time uploaded:

test2.txt                       2018-09-08 18:27:54

Untitled2.png                   2018-09-08 18:24:45

Untitled2.png paste continued part - 1

Untitled2.png paste continued part - 2

Untitled2.png paste continued part - 3

Untitled2.png paste continued part - 4


In [16]: mycloud.delete("Untitled2.png")

deleting Untitled2.png starting from instance 0.

Untitled2.png deleted successfully paste part: 1.

Untitled2.png deleted successfully paste part: 2.

Untitled2.png deleted successfully paste part: 3.

Untitled2.png deleted successfully paste part: 4.

Untitled2.png deleted successfully paste part: 5.


In [26]: mycloud.print_list()

Paste(s):                   date and time uploaded:

test2.txt                   2018-09-08 18:31:13


In [27]: mycloud.download("test2.txt")

downloading test2.txt.

downloaded paste 1.

created on C:\mycloudtest\test2.txt successfully.


In [27]: 
```

### pastebin limitations for non premium users:
1. 500kb per paste. (file bigger then 500k will be uploaded in a serval pastes).
2. uploading rapidly causes spam protection with out error response. (so uploading is automatically delayed by the API).
3. 25 pastes per 24 hours limit. (deleting pastes of the day also reduces the pastes uploaded that day number)
4. only 3 private pastes allowed. 
5. only 10 unlisted pastes allowed. 

### issues:

1. file list wont update properly sometimes, this is mainly related to the pastebin service itself. 
2. converting to hex string doubles the file size(in the pastes), resulting in slow upload and download. more efficent way to save binary data in string format `(utf-8)` is needed.
3. need to organize code and error handling.
4. uploads are for everyone to see (if not private or encrypted).

### to-do:

1. add file size to the file list
2. add expriation and file type options to the upload option, and adding this data to the file list.
3. update function? (delete and reupload).
4. add an option to upload as a pastebin guest, saving the file list locally.
5. add a user data function (get all user parameters, such as premium, history etc)
6. encryption?
