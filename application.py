import os

from flask import Flask, request, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
# Setting up the absolute path of file uploading directory
from os.path import join, dirname, realpath

UPLOAD_FOLDER = join(dirname(realpath(__file__)),
					 '/------/project2/static/user_profilepics')
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
socketio = SocketIO(app)


channels = []
channelId = 0
# Convenient for using channelId
#def aug(x):
#	return x + 1

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
	# post request serve for changing the profile picture
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return render_template("index.html", filename=filename, channels=channels)		
	else:
		filename = ''
		return render_template("index.html", filename=filename, channels=channels)

# When the server side recieve the submit new channel signal
@socketio.on("submit new channel")
def newChannel(data):

	# Refuse duplicate channel name
	for channel in channels:
		if channel["name"] == data["channel"]:
			return 0;

	owner = data["owner"]
	channel = data["channel"]
	profile_picture = data["profile_picture"]
	# Reference global variable channelId, necessary if the variable will be modified
	global channelId
	channelId += 1

	# Set the new channel as a dictionary, restoring channel name,
	# owner, and a nested dictionary for message history
	newChannel = {"id": channelId, "name": channel, "owner": owner, "profile_picture": profile_picture, "chat_history": []}
	# Append the new channel to list channels
	channels.append(newChannel)

	emit("announce channel", {"channel": channel, "owner": owner, "id": channelId, "profile_picture": profile_picture}, broadcast=True)
	emit("channel owner", {"channel": channel, "owner": owner, "id": channelId, "profile_picture": profile_picture})

# When the server revieve the message sent by user
@socketio.on("submit new message")
def newMessage(data):

	# Ensure the user has entered a channel
	if not data["current_channel"]:
		return 0;

	# Modify the channel name
	current_channel = data["current_channel"].lstrip('list_channel_')
	# Configure the message
	message = data["message"]
	msg_sent_by = data["msg_sent_by"]
	msg_time = data["msg_time"]
	profile_picture = data["profile_picture"]
	# Limit of the chat storage
	CHAT_LIMIT = 20
	new_message = {"msg_sent_by": msg_sent_by, "message": message, "profile_picture": profile_picture, "msg_time": msg_time}

	# Looping the channels
	for channel in channels:
		if channel["id"] is int(current_channel):
			# Limit 100 messages
			if len(channel["chat_history"]) >= CHAT_LIMIT:
				del channel["chat_history"][0]
				channel["chat_history"].append(new_message)
				# Inform the javascript
				msg_overflow = 1
			else:
				# Update the chat history
				channel["chat_history"].append(new_message)
				msg_overflow = 0

	# Emit the message
	emit("announce message", {"message": message, "msg_sent_by": msg_sent_by, "profile_picture": profile_picture, "msg_time": msg_time,
								"msg_overflow": msg_overflow, "current_channel": current_channel}, broadcast=True)