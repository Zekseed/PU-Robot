from pybricks import messaging

SERVER = "F4:84:4C:AF:47:3D"

client = BluetoothMailboxClient()
mbox = TextMailbox("greeting", client)

print("establishing connection...")
client.connect(SERVER)
print("connected!")

# In this program, the client sends the first message and then waits for the
# server to reply.
mbox.send("hello!")
mbox.wait()
print(mbox.read())
