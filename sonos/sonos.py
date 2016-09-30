import logging
import os
import pwd
import soco


logger = logging.getLogger(__name__)


# Find the speaker associated with the current user.
_username = pwd.getpwuid(os.geteuid()).pw_name
logger.info("looking for sonos (%s)", _username)
sonos = next(s for s in soco.discover()
             if s.player_name.lower() == _username)
logger.info("found sonos %s", sonos.player_name)


# Upgrade from the individual speaker to the group coordinator.
leader = sonos.group.coordinator
if sonos != leader:
    sonos = leader
    logger.info("switched to group coordinator %s", sonos)