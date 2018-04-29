import socket
import os
import json
import struct

class DiscordRPC:
    def __init__(self):
        """
        Finds the socket to connect to and establishes a connection
        """
        self.discordSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        socketDir = None
        envVars = ["XDG_RUNTIME_DIR", "TMPDIR", "TMP", "TEMP"]
        for var in envVars:
            if not var == None:
                socketDir = os.environ.get(var)
                break
        if socketDir == None:
            socketDir = "/tmp"

        # can be discord-ipc-[0-9]
        for pipeNum in range(0, 10):
            try:
                self.discordSocket.connect(f"{socketDir}/discord-ipc-{pipeNum}")
                break
            except socket.error as e:
                # throw exception if all possibilities are exhausted with no success
                if pipeNum == 9:
                    raise e

    def read(self):
        """
        Returns the last frame recieved by the socket
        """
        data = self.discordSocket.recv(4096)
        # fix character encoding errors
        return data.decode("utf-8", errors="ignore")

    def write(self, opcode, payload):
        """
        Generates a frame and sends it to the socket
        :param int opcode: The opcode to send in the frame header
        :param dict payload: The payload to send
        """
        payload = json.dumps(payload)
        # frame structure shown in RpcConnection::Open(), rpc_connection.cpp, reference implementation
        self.discordSocket.send(struct.pack("<ii", opcode, len(payload)) + payload.encode("utf-8"))
    
    def init(self, client_id):
        """
        Performs initial handshake
        :param str client_id: Client ID of the discord app to send presence data for
        """
        self.write(0, {"v": 1, "client_id": client_id})

    def sendRichPresence(self, pid, activity):
        """
        Sends rich presence data
        :param int pid: PID of process connecting to RPC server
        :param dict activity: A dictionary that is serialized to JSON and sent as the value of the payload's activity key
        """
        payload = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": pid,
                "activity": activity
            },
            "nonce": str(os.urandom(16))
        }
        self.write(1, payload)
    
    def close(self):
        """
        Closes socket
        """
        self.discordSocket.close()
