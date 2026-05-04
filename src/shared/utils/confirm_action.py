def require_exact_confirmation(
  confirmation_text: str,
  action_description: str,
  show_confirmation_text: bool = True,
  displayed_confirmation_text: str | None = None,
) -> bool:
  prompt = f"Type the following confirmation text to {action_description}:\n"
  if show_confirmation_text:
    prompt += f"{displayed_confirmation_text or confirmation_text}\n"
  prompt += "> "
  provided_text = input(prompt).strip()

  return provided_text == confirmation_text
