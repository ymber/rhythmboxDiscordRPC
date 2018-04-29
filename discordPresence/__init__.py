from .rpc import DiscordRPC
import gi
gi.require_version('RB', '3.0')
gi.require_version('Peas', '1.0')
from gi.repository import GObject, RB, Peas
import os
import time

class DiscordPresencePlugin(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def do_activate(self):
        self.discordPresence = DiscordRPC()
        self.discordPresence.init("437204475791409152")
        print(self.discordPresence.read())
        
        self.songChange = self.object.props.shell_player.connect("playing-song-changed", self.updateDiscordPresence)
    
    def updateDiscordPresence(self, player, entry):
        trackName = str(entry.get_string(RB.RhythmDBPropType.TITLE))
        albumName = str(entry.get_string(RB.RhythmDBPropType.ALBUM))
        artist = str(entry.get_string(RB.RhythmDBPropType.ARTIST))
        self.discordPresence.sendRichPresence(os.getpid(), {"state": albumName, "details": trackName,
                                                            "assets": {"large_image": "rhythmbox", "large_text": artist}})
        print(self.discordPresence.read())

    def do_deactivate(self):
        self.object.props.shell_player.disconnect(self.songChange)
        self.object.props.shell_player.disconnect(self.propertyChange)
        self.discordPresence.close()
