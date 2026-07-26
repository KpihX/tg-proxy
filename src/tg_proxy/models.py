"""
Pydantic models for all tg-proxy RPC payloads.
"""

from pydantic import BaseModel, Field

# ─── Bot models ───


class BotListPayload(BaseModel):
    filter: str = "all"


class BotInfoPayload(BaseModel):
    bots: list[str] = Field(default_factory=list, description="@usernames or IDs")


class BotTokenPayload(BaseModel):
    bots: list[str] = Field(default_factory=list, description="@usernames or IDs")


class BotCreateItem(BaseModel):
    name: str = Field(..., description="Display name for the bot")
    username: str = Field(..., description="@username (without @)")
    manager_bot: str = Field(
        "", description="Manager bot @username (optional, MTProto)"
    )


class BotCreatePayload(BaseModel):
    bots: list[BotCreateItem] = Field(default_factory=list)


class BotDeletePayload(BaseModel):
    bots: list[str] = Field(default_factory=list, description="@usernames or IDs")


class BotSendPayload(BaseModel):
    bot: str = Field(..., description="Bot @username or ID to send AS")
    message: str = Field(..., description="Message text (HTML/Markdown)")
    parse_mode: str | None = Field(None, description="HTML | Markdown | null")


class BotSendFilePayload(BaseModel):
    bot: str = Field(..., description="Bot @username or ID to send AS")
    message: str = Field("", description="Message caption")
    files: list[str] = Field(default_factory=list, description="Paths to files")


# ─── Chat models ───


class ChatListPayload(BaseModel):
    type: str | None = Field(None, description="user | group | channel")
    limit: int = Field(30, ge=1, le=200)


class ChatReadPayload(BaseModel):
    chat: str | int = Field(..., description="Chat ID, @username, or phone")
    limit: int = Field(20, ge=1, le=200)
    search: str | None = None


class ChatSendPayload(BaseModel):
    to: str | int = Field(..., description="Recipient: chat ID, @username, or phone")
    message: str = Field(..., description="Message text")


class ChatSendFilePayload(BaseModel):
    to: str | int = Field(..., description="Recipient: chat ID, @username, or phone")
    message: str = Field("", description="Message caption")
    files: list[str] = Field(default_factory=list, description="Paths to files")


class ChatDownloadPayload(BaseModel):
    chat: str | int = Field(..., description="Chat ID, @username, or phone")
    message_ids: list[int] = Field(..., description="Message IDs to download from")
    out: str = Field("/tmp/tg-proxy-downloads", description="Output directory")


class ChatDeletePayload(BaseModel):
    chat: str | int = Field(..., description="Chat ID, @username, or phone to delete")
    revoke: bool = Field(
        True, description="Revoke (delete for both sides) for private chats"
    )


class ChatDeleteMessagesPayload(BaseModel):
    chat: str | int = Field(..., description="Chat ID, @username, or phone")
    message_ids: list[int] = Field(..., description="Message IDs to delete")
    revoke: bool = Field(True, description="Revoke (delete for both sides)")


# ─── Folder models ───


class FolderListPayload(BaseModel):
    pass


class FolderSetPayload(BaseModel):
    title: str = Field(..., description="Folder title")
    chats: list[str] = Field(
        default_factory=list, description="@usernames or IDs to include"
    )
    icon: str | None = Field(None, description="Folder icon emoji (e.g. 💻)")


class FolderDeletePayload(BaseModel):
    title: str = Field(..., description="Folder title to delete")


class ChatMovePayload(BaseModel):
    chat: str = Field(..., description="Chat @username or ID")
    to: str = Field(..., description="Target folder title")


class BotPhotoPayload(BaseModel):
    bots: list[str] = Field(
        ..., description="List of @usernames or IDs to download photos from"
    )
    out: str = Field(
        "/tmp/tg-bot-photos", description="Output directory for downloaded photos"
    )


# ─── Updates models ───


class UpdatesPayload(BaseModel):
    bot: str = Field(..., description="Bot @username or ID")
    limit: int = Field(10, ge=1, le=200)


# ─── Webhook models ───


class WebhookGetPayload(BaseModel):
    bot: str = Field(..., description="Bot @username or ID")


class WebhookSetPayload(BaseModel):
    bot: str = Field(..., description="Bot @username or ID")
    url: str = Field(..., description="Webhook URL")


class WebhookDelPayload(BaseModel):
    bot: str = Field(..., description="Bot @username or ID")
    drop_pending: bool = False


# ─── Meta response ───


class OutputMeta(BaseModel):
    status: str = Field("ok", description="ok | approved | rejected | error")
    comment: str = Field("", description="User comment from HITL")
    edited: bool = False
    original: str | None = None
    edited_to: str | None = None


class Output(BaseModel):
    meta: OutputMeta = Field(
        default_factory=lambda: OutputMeta(status="ok", comment="")
    )
    data: dict | list | str | int | float | bool | None = None
