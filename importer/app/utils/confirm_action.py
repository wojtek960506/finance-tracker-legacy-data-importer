def require_exact_confirmation(
  confirmation_text: str,
  action_description: str,
) -> bool:
  prompt = (
    f"Type the following confirmation text to {action_description}:\n"
    f"{confirmation_text}\n"
    "> "
  )
  provided_text = input(prompt).strip()

  return provided_text == confirmation_text
