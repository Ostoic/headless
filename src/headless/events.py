import uuid
from enum import Enum


class AuthEvent(Enum):
    # Basic connection events
    connected = uuid.uuid4()
    data_received = uuid.uuid4()

    disconnected = uuid.uuid4()

    realmlist_ready = uuid.uuid4()

    #
    authenticating = uuid.uuid4()
    invalid_login = uuid.uuid4()
    authenticated = uuid.uuid4()


auth = AuthEvent


class WorldEvent(Enum):
    # Basic Events
    connected = uuid.uuid4()
    in_queue = uuid.uuid4()
    logged_in = uuid.uuid4()
    logging_in = uuid.uuid4()
    loading_world = uuid.uuid4()
    entered_world = uuid.uuid4()
    logged_out = uuid.uuid4()

    # Net events
    disconnected = uuid.uuid4()

    received_contact_list = uuid.uuid4()
    received_group_invite = uuid.uuid4()
    received_group_list = uuid.uuid4()
    received_group_kick = uuid.uuid4()
    received_group_destroyed = uuid.uuid4()
    received_group_joined_bg = uuid.uuid4()

    received_guild_invite = uuid.uuid4()
    received_guild_event = uuid.uuid4()
    received_guild_info = uuid.uuid4()
    received_guild_roster = uuid.uuid4()
    received_guild_query_response = uuid.uuid4()

    received_chat_message = uuid.uuid4()
    # received_gm_chat_message = uuid.uuid4()
    received_duel_request = uuid.uuid4()
    received_duel_winner = uuid.uuid4()
    received_duel_complete = uuid.uuid4()
    received_name_query_response = uuid.uuid4()
    received_bind_point = uuid.uuid4()

    received_packet = uuid.uuid4()
    received_auth_challenge = uuid.uuid4()
    received_auth_response = uuid.uuid4()
    received_time_query_response = uuid.uuid4()
    received_mail_list = uuid.uuid4()
    received_new_mail = uuid.uuid4()
    received_char_enum = uuid.uuid4()
    received_server_message = uuid.uuid4()
    received_notification = uuid.uuid4()
    received_motd = uuid.uuid4()
    received_pong = uuid.uuid4()
    received_play_sound = uuid.uuid4()
    received_login_world = uuid.uuid4()
    received_warden_data = uuid.uuid4()
    received_tutorial_flags = uuid.uuid4()
    received_time_sync_request = uuid.uuid4()
    received_logout_response = uuid.uuid4()
    received_character_rename = uuid.uuid4()
    received_character_create = uuid.uuid4()
    logout_cancelled = uuid.uuid4()

    received_cancel_combat = uuid.uuid4()
    received_pending_transfer = uuid.uuid4()
    received_abort_transfer = uuid.uuid4()

    received_health_update = uuid.uuid4()
    received_destroy_object = uuid.uuid4()
    received_update_object = uuid.uuid4()

    sent_ping = uuid.uuid4()
    sent_keep_alive = uuid.uuid4()
    sent_warden_data = uuid.uuid4()
    sent_char_enum = uuid.uuid4()
    sent_time_sync = uuid.uuid4()
    sent_player_login = uuid.uuid4()
    sent_logout_request = uuid.uuid4()
    sent_logout_cancel = uuid.uuid4()
    sent_auth_session = uuid.uuid4()
    sent_chat_message = uuid.uuid4()
    sent_character_rename = uuid.uuid4()
    sent_character_create = uuid.uuid4()
    sent_guild_query = uuid.uuid4()


world = WorldEvent


class ConfigEvent(Enum):
    relogger_changed = uuid.uuid4()
    username_changed = uuid.uuid4()
    password_changed = uuid.uuid4()

    auth_server_address_changed = uuid.uuid4()
    character_name_changed = uuid.uuid4()
    realm_name_changed = uuid.uuid4()


config = ConfigEvent
