from pybricks.messaging import BluetoothMailboxClient, TextMailbox

SERVER = "ev3dev-C"

client = BluetoothMailboxClient()
mbox = TextMailbox("greeting", client)

print("establishing connection...")
client.connect(SERVER)
print("connected!")

# In this program, the client sends the first message and then waits for the
# server to reply.
mbox.send("hello!")
mbox.wait_new()

mbox.wait_new()

mbox.wait_new()

message = mbox.read()
print('"' + message + '"')