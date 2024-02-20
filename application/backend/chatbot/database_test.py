from history import PostgresChatMessageHistory

history = PostgresChatMessageHistory(session_id="test_session_id")

history.add_user_message("hi!")

history.add_ai_message("whats up?")

print(history.messages)