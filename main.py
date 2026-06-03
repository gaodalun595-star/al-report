from __future__ import annotations

from agent_core import Agent, get_token_budget


EXIT_COMMANDS = {"quit", "exit", "q"}


def parse_cli_turn(raw_text: str) -> tuple[str, str | None, bool]:
    if not raw_text.startswith("/image "):
        return raw_text, None, False

    rest = raw_text[len("/image ") :].strip()
    if not rest:
        print("Usage: /image <relative-path> [message]")
        return "", None, False

    parts = rest.split(maxsplit=1)
    image_path = parts[0]
    if len(parts) == 1:
        print(f"Image queued: {image_path!r}. Type your message next.")
        return "", image_path, True
    return parts[1].strip(), image_path, False


def main() -> None:
    try:
        agent = Agent.from_env()
    except RuntimeError as exc:
        print(exc)
        return

    print("WG-22 agent ready. Type quit / exit / q to stop.")
    print("Use /image <relative-path> [message] to send an image with a turn.")
    print(f"TOKEN_BUDGET={get_token_budget()} | session={agent.session_path!r}")
    if agent.history:
        print(
            f"Loaded {len(agent.history)} saved messages; "
            f"last_consolidated={agent.last_consolidated}."
        )
    else:
        print("Starting a new session.")

    pending_image: str | None = None

    while True:
        raw_text = input("\nYou> ").strip()
        if raw_text.lower() in EXIT_COMMANDS:
            print("Bye.")
            break
        if not raw_text:
            continue

        user_text, image_path, queued = parse_cli_turn(raw_text)
        if queued:
            pending_image = image_path
            continue
        if pending_image and image_path is None:
            image_path = pending_image
            pending_image = None
        if not user_text:
            continue

        print("\nAgent> ", end="", flush=True)
        agent.chat(user_text, image_path=image_path)
        print()


if __name__ == "__main__":
    main()
