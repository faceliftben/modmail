import asyncio
import json
import os
import re
import typing
from copy import deepcopy

from dotenv import load_dotenv
import isodate

import discord
from discord.ext.commands import BadArgument

from core._color_data import ALL_COLORS
from core.models import DMDisabled, InvalidConfigError, Default, getLogger
from core.time import UserFriendlyTime
from core.utils import strtobool

logger = getLogger(__name__)
load_dotenv()


class ConfigManager:

    public_keys = {
        # activity
        "twitch_url": "https://www.twitch.tv/gameparadiselive/",
        # bot settings
        "main_category_id": None,
        "fallback_category_id": None,
        "prefix": "?",
        "mention": "<@&1099731910160298004> <@&1099473545786032188>",
        "main_color": str(discord.Color.blurple()),
        "error_color": str(discord.Color.red()),
        "user_typing": True,
        "mod_typing": True,
        "account_age": isodate.Duration(),
        "guild_age": isodate.Duration(),
        "thread_cooldown": isodate.Duration(),
        "reply_without_command": True,
        "anon_reply_without_command": False,
        "plain_reply_without_command": False,
        # logging
        "log_channel_id": None,
        "mention_channel_id": None,
        "update_channel_id": None,
        # updates
        "update_notifications": True,
        # threads
        "sent_emoji": "<:yes:1101562256392724570>",
        "blocked_emoji": "`<:no:1101562252798202006>",
        "close_emoji": "\N{LOCK}",
        "use_user_id_channel_name": False,
        "use_timestamp_channel_name": False,
        "use_nickname_channel_name": False,
        "use_random_channel_name": False,
        "recipient_thread_close": False,
        "thread_show_roles": False,
        "thread_show_account_age": True,
        "thread_show_join_age": True,
        "thread_cancelled": "Die Aktion wurde durch dass System oder durch dich abgebrochen",
        "thread_auto_close_silently": False,
        "thread_auto_close": isodate.Duration(),
        "thread_auto_close_response": "⏰ Dieses Ticket wurde aufgrund von Inaktivität automatisch geschlossen. Es ist seit {timeout} unverändert geblieben. 😕 Bitte eröffne bei Bedarf ein neues Ticket, oder antworte einfach auf diese Nachricht, um das vorherige Ticket wieder zu öffnen. Wir sind jederzeit gerne für dich da! 🤗",
        "thread_creation_response": "Hallo, vielen Dank, dass du dich an den Support von den Game Paradise gewendet hast. Bitte beachte, dass alle [Regeln](https://game-paradise.de/index.php?regeln/) im Support ebenfalls gelten.\n\nUnser Mitarbeiterteam wird sich so schnell wie möglich bei ihnen melden.\n\n__Bitte beachte , dass wenn sie nicht mit Sie sondern mit du angesprochen werden möchten, dann sagen dies bitte direkt!__",
        "thread_creation_footer": "Deine Nachricht wurde gesendet",
        "thread_contact_silently": False,
        "thread_self_closable_creation_footer": "Klicke auf das Schloss, um den Ticket zu schließen",
        "thread_creation_contact_title": "Neues Ticket wurde erstellt",
        "thread_creation_self_contact_response": "Du hast ein Modmail-Ticket eröffnet.",
        "thread_creation_contact_response": "📢 Hey! 🙋‍♀️ \n\nEin Mitglied unseres Teams hat ein Ticket für dich erstellt! 🎟️\n\n🛠️Teamler: {creator.name}",
        "thread_creation_title": "Ticket erstellt",
        "thread_close_footer": "Durch Antworten wird ein neues Ticket erstellt",
        "thread_close_title": "Ticket geschlossen",
        "thread_close_response": "{closer.mention} hat dieses Modmail-Ticket geschlossen.",
        "thread_self_close_response": "Der zuständige Supporter oder ein anderes Teammitglied hat dein Ticket geschlossen.",
        "thread_move_title": "Ticket verschoben",
        "thread_move_notify": False,
        "thread_move_notify_mods": True,
        "thread_move_response": "Dieses Ticket wurde verschoben.",
        "cooldown_thread_title": "Nachricht nicht gesendet!",
        "cooldown_thread_response": "Die Abklingzeit endet am {delta}. Versuche dann, mich zu kontaktieren.",
        "disabled_new_thread_title": "Ticket nicht erstellt",
        "disabled_new_thread_response": "👋 Hallo! Wir bedauern, dass unser Support derzeit nicht verfügbar ist. 😔 Bitte versuche es später erneut, oder schreibe uns einer unserer Teamler Privat an, damit wir dir schnellstmöglich helfen können. 📧 Vielen Dank für dein Verständnis! 😊",
        "disabled_new_thread_footer": "Bitte versuche es später noch einmal...",
        "disabled_current_thread_title": "Ticket nicht erstellt",
        "disabled_current_thread_response": "🚫 Leider können wir derzeit keine Nachrichten entgegennehmen. Wir entschuldigen uns für die Unannehmlichkeiten! 😔 Bitte versuche es zu einem späteren Zeitpunkt erneut. Vielen Dank für dein Verständnis. 🙏",
        "disabled_current_thread_footer": "Bitte versuche es später noch einmal...",
        "transfer_reactions": False,
        "close_on_leave": True,
        "close_on_leave_reason": "Der Empfänger hat den Server verlassen.",
        "alert_on_mention": True,
        "silent_alert_on_mention": False,
        "show_timestamp": True,
        "anonymous_snippets": False,
        "plain_snippets": False,
        "require_close_reason": False,
        "show_log_url_button": False,
        # group conversations
        "private_added_to_group_title": "Neues Ticket (Gruppe)",
        "private_added_to_group_response": "{moderator.name} hat dich zu einem Modmail-Ticket hinzugefügt.",
        "private_added_to_group_description_anon": "Ein Mitarbeiter hat dich zu einem Modmail-Ticket hinzugefügt.",
        "public_added_to_group_title": "Neuer Benutzer",
        "public_added_to_group_response": "{moderator.name} hat {users} zum Modmail-Ticket hinzugefügt.",
        "public_added_to_group_description_anon": "Ein Mitarbeiter hat {users} zum Modmail-Ticket hinzugefügt.",
        "private_removed_from_group_title": "Aus Ticket entfernt (Gruppe)",
        "private_removed_from_group_response": "{moderator.name} hat dich aus dem Modmail-Ticket entfernt.",
        "private_removed_from_group_description_anon": "Ein Mitarbeiter hat dich aus dem Modmail-Ticket entfernt.",
        "public_removed_from_group_title": "Benutzer entfernt",
        "public_removed_from_group_response": "{moderator.name} hat {users} aus dem Modmail-Ticket entfernt.",
        "public_removed_from_group_description_anon": "Ein Mitarbeiter hat {users} aus dem Modmail-Ticket entfernt.",
        # moderation
        "recipient_color": str(discord.Color.gold()),
        "mod_color": str(discord.Color.green()),
        "mod_tag": None,
        # anonymous message
        "anon_username": None,
        "anon_avatar_url": None,
        "anon_tag": "Antwort",
        # react to contact
        "react_to_contact_message": None,
        "react_to_contact_emoji": "<:yes:1101562256392724570>",
        # confirm thread creation
        "confirm_thread_creation": True,
        "confirm_thread_creation_title": "Möchtest du den Offiziellen Support Kontaktieren?",
        "confirm_thread_response": "Du bist dabei ein Ticket zu erstellen.\n\nFolgendes Solltest du beachten.\n\n> 1. Dies ist der einzige Offizielle Support von [Game Paradise](https://game-paradise.de)\n\n> 2. Dein Ticket wird nach 48 Stunden Inaktivität vom System geschlossen.\n\n> 3. Unsere Mitarbeiter sind nicht verpflichtet dein Ticket vorzuziehen oder es direkt zu bearbeiten.\n\n**Folgende Gründe einer Erstellung stehen dir zur Verfügung**\n\n> Support\n> Bewerben Team\n> Bewerben Partner\n> Allgemeine Frage\n> Gewinn abholung\n> User Melden\n\n**Ticket erstellen**\n\n<:yes:1101562256392724570>: Erstellen\n<:no:1101562252798202006>: Keins erstellen",
        "confirm_thread_creation_accept": "<:yes:1101562256392724570>",
        "confirm_thread_creation_deny": "<:no:1101562252798202006>",
        # regex
        "use_regex_autotrigger": False,
        "use_hoisted_top_role": False,
    }

    private_keys = {
        # bot presence
        "activity_message": "",
        "activity_type": None,
        "status": None,
        "dm_disabled": DMDisabled.NONE,
        "oauth_whitelist": [],
        # moderation
        "blocked": {},
        "blocked_roles": {},
        "blocked_whitelist": [],
        "command_permissions": {},
        "level_permissions": {},
        "override_command_level": {},
        # threads
        "snippets": {},
        "notification_squad": {},
        "subscriptions": {},
        "closures": {},
        # misc
        "plugins": [],
        "aliases": {},
        "auto_triggers": {},
    }

    protected_keys = {
        # Modmail
        "modmail_guild_id": None,
        "guild_id": None,
        "log_url": "https://example.com/",
        "log_url_prefix": "/logs",
        "mongo_uri": None,
        "database_type": "mongodb",
        "connection_uri": None,  # replace mongo uri in the future
        "owners": None,
        # bot
        "token": None,
        "enable_plugins": True,
        "enable_eval": True,
        # github access token for private repositories
        "github_token": None,
        "disable_autoupdates": False,
        "disable_updates": False,
        # Logging
        "log_level": "INFO",
        # data collection
        "data_collection": True,
    }

    colors = {"mod_color", "recipient_color", "main_color", "error_color"}

    time_deltas = {"account_age", "guild_age", "thread_auto_close", "thread_cooldown"}

    booleans = {
        "use_user_id_channel_name",
        "use_timestamp_channel_name",
        "use_nickname_channel_name",
        "use_random_channel_name",
        "user_typing",
        "mod_typing",
        "reply_without_command",
        "anon_reply_without_command",
        "plain_reply_without_command",
        "show_log_url_button",
        "recipient_thread_close",
        "thread_auto_close_silently",
        "thread_move_notify",
        "thread_move_notify_mods",
        "transfer_reactions",
        "close_on_leave",
        "alert_on_mention",
        "silent_alert_on_mention",
        "show_timestamp",
        "confirm_thread_creation",
        "use_regex_autotrigger",
        "enable_plugins",
        "data_collection",
        "enable_eval",
        "disable_autoupdates",
        "disable_updates",
        "update_notifications",
        "thread_contact_silently",
        "anonymous_snippets",
        "plain_snippets",
        "require_close_reason",
        "recipient_thread_close",
        "thread_show_roles",
        "thread_show_account_age",
        "thread_show_join_age",
        "use_hoisted_top_role",
    }

    enums = {
        "dm_disabled": DMDisabled,
        "status": discord.Status,
        "activity_type": discord.ActivityType,
    }

    force_str = {"command_permissions", "level_permissions"}

    defaults = {**public_keys, **private_keys, **protected_keys}
    all_keys = set(defaults.keys())

    def __init__(self, bot):
        self.bot = bot
        self._cache = {}
        self.ready_event = asyncio.Event()
        self.config_help = {}

    def __repr__(self):
        return repr(self._cache)

    def populate_cache(self) -> dict:
        data = deepcopy(self.defaults)

        # populate from env var and .env file
        data.update({k.lower(): v for k, v in os.environ.items() if k.lower() in self.all_keys})
        config_json = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        if os.path.exists(config_json):
            logger.debug("Laden von envs aus config.json.")
            with open(config_json, "r", encoding="utf-8") as f:
                # Config json should override env vars
                try:
                    data.update({k.lower(): v for k, v in json.load(f).items() if k.lower() in self.all_keys})
                except json.JSONDecodeError:
                    logger.critical("Fehler beim Laden der config.json-Env-Werte.", exc_info=True)
        self._cache = data

        config_help_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_help.json")
        with open(config_help_json, "r", encoding="utf-8") as f:
            self.config_help = dict(sorted(json.load(f).items()))

        return self._cache

    async def update(self):
        """Aktualisiert die Konfiguration mit Daten aus dem Cache"""
        await self.bot.api.update_config(self.filter_default(self._cache))

    async def refresh(self) -> dict:
        """Aktualisiert den internen Cache mit Daten aus der Datenbank"""
        for k, v in (await self.bot.api.get_config()).items():
            k = k.lower()
            if k in self.all_keys:
                self._cache[k] = v
        if not self.ready_event.is_set():
            self.ready_event.set()
            logger.debug("Konfigurationen erfolgreich aus der Datenbank abgerufen.")
        return self._cache

    async def wait_until_ready(self) -> None:
        await self.ready_event.wait()

    def __setitem__(self, key: str, item: typing.Any) -> None:
        key = key.lower()
        logger.info("Setting %s.", key)
        if key not in self.all_keys:
            raise InvalidConfigError(f'Konfiguration "{key}" ist ungültig.')
        self._cache[key] = item

    def __getitem__(self, key: str) -> typing.Any:
        # make use of the custom methods in func:get:
        return self.get(key)

    def __delitem__(self, key: str) -> None:
        return self.remove(key)

    def get(self, key: str, convert=True) -> typing.Any:
        key = key.lower()
        if key not in self.all_keys:
            raise InvalidConfigError(f'Konfiguration "{key}" ist ungültig.')
        if key not in self._cache:
            self._cache[key] = deepcopy(self.defaults[key])
        value = self._cache[key]

        if not convert:
            return value

        if key in self.colors:
            try:
                return int(value.lstrip("#"), base=16)
            except ValueError:
                logger.error("Invalid %s provided.", key)
            value = int(self.remove(key).lstrip("#"), base=16)

        elif key in self.time_deltas:
            if not isinstance(value, isodate.Duration):
                try:
                    value = isodate.parse_duration(value)
                except isodate.ISO8601Error:
                    logger.warning(
                        "Die Altersgrenze für {account} muss a sein"
                        'ISO-8601-Dauer formatierte Dauer, nicht "%s".',
                        value,
                    )
                    value = self.remove(key)

        elif key in self.booleans:
            try:
                value = strtobool(value)
            except ValueError:
                value = self.remove(key)

        elif key in self.enums:
            if value is None:
                return None
            try:
                value = self.enums[key](value)
            except ValueError:
                logger.warning("Ungültig %s %s.", key, value)
                value = self.remove(key)

        elif key in self.force_str:
            # Temporary: as we saved in int previously, leading to int32 overflow,
            #            this is transitioning IDs to strings
            new_value = {}
            changed = False
            for k, v in value.items():
                new_v = v
                if isinstance(v, list):
                    new_v = []
                    for n in v:
                        if n != -1 and not isinstance(n, str):
                            changed = True
                            n = str(n)
                        new_v.append(n)
                new_value[k] = new_v

            if changed:
                # transition the database as well
                self.set(key, new_value)

            value = new_value

        return value

    def set(self, key: str, item: typing.Any, convert=True) -> None:
        if not convert:
            return self.__setitem__(key, item)

        if key in self.colors:
            try:
                hex_ = str(item)
                if hex_.startswith("#"):
                    hex_ = hex_[1:]
                if len(hex_) == 3:
                    hex_ = "".join(s for s in hex_ for _ in range(2))
                if len(hex_) != 6:
                    raise InvalidConfigError("Ungültiger Farbname oder Hex.")
                try:
                    int(hex_, 16)
                except ValueError:
                    raise InvalidConfigError("Ungültiger Farbname oder Hex..")

            except InvalidConfigError:
                name = str(item).lower()
                name = re.sub(r"[\-+|. ]+", " ", name)
                hex_ = ALL_COLORS.get(name)
                if hex_ is None:
                    name = re.sub(r"[\-+|. ]+", "", name)
                    hex_ = ALL_COLORS.get(name)
                    if hex_ is None:
                        raise
            return self.__setitem__(key, "#" + hex_)

        if key in self.time_deltas:
            try:
                isodate.parse_duration(item)
            except isodate.ISO8601Error:
                try:
                    converter = UserFriendlyTime()
                    time = converter.convert(None, item)
                    if time.arg:
                        raise ValueError
                except BadArgument as exc:
                    raise InvalidConfigError(*exc.args)
                except Exception as e:
                    logger.debug(e)
                    raise InvalidConfigError(
                        "Nicht erkannte Zeit, bitte verwende das ISO-8601-Dauerformat"
                        'Zeichenfolge oder eine einfachere "vom Menschen lesbare" Zeit.'
                    )
                now = discord.utils.utcnow()
                item = isodate.duration_isoformat(time.dt - now)
            return self.__setitem__(key, item)

        if key in self.booleans:
            try:
                return self.__setitem__(key, strtobool(item))
            except ValueError:
                raise InvalidConfigError("Muss ein Ja/Nein-Wert sein.")

        elif key in self.enums:
            if isinstance(item, self.enums[key]):
                # value is an enum type
                item = item.value

        return self.__setitem__(key, item)

    def remove(self, key: str) -> typing.Any:
        key = key.lower()
        logger.info("Removing %s.", key)
        if key not in self.all_keys:
            raise InvalidConfigError(f'Konfiguration "{key}" ist ungültig.')
        if key in self._cache:
            del self._cache[key]
        self._cache[key] = deepcopy(self.defaults[key])
        return self._cache[key]

    def items(self) -> typing.Iterable:
        return self._cache.items()

    @classmethod
    def filter_valid(cls, data: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        return {
            k.lower(): v
            for k, v in data.items()
            if k.lower() in cls.public_keys or k.lower() in cls.private_keys
        }

    @classmethod
    def filter_default(cls, data: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        # TODO: use .get to prevent errors
        filtered = {}
        for k, v in data.items():
            default = cls.defaults.get(k.lower(), Default)
            if default is Default:
                logger.error("Unerwartete Konfiguration erkannt: %s.", k)
                continue
            if v != default:
                filtered[k.lower()] = v
        return filtered
