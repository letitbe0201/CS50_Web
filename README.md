# CS50 Web
### Flask, Socket.IO, Python, Javascript

### Project 2

#### A online messaging service.

###### Users could be able to
* Type in a display name(username) showing to other users, and free to change the username anytime.
* Upload a profile picture which will show on the channel list as well as inside the chat room (througn Flask).
* Create channels so long as its name doesn't conflict with the name of an existing channel.
	1. The new channel will be emitted through socket.IO and display on both the owner's and other users' browsers simultaneously.
	2. The info of the new channel (including channel name, creator, chat history, etc) will be store as a dictionary in the server side.
* Browse the channel list and chat inside a chat room.
	1. The old message will be sent from the server and display on the user's browser.
	2. The new message will be display on every user's browser simultaneously and store in the server through Socket.IO.
* If a user close the web browser window, the application will remember the username, what channel the user was on previously and take the user back to that channel once the user re-open the application. (using localStorage property)

###### Files include
* _application.py_ Using FLASK and Socket.IO to control the new channel, new message and handling the post request of file(profile picture) upload from the url '/'.
* _index.html_ Configure the username, profile picture, channels and the message box display on the browser with Javascript && Socket.IO.

[Link to project overview from CS50](https://docs.cs50.net/web/2018/x/projects/2/project2.html)

Yida Chung