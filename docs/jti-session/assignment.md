# Per‑Session Conversation History via jti

## Overview & Goal

Add session‑specific conversation history to the chatbot so that each login gets its own chat context.
The implementation must:

1. Generate a unique JWT (jti claim) for every login.
2. Use the jti as the key in the session store.
3. Persist the chat history only while the token is valid (TTL = ACCESS_TOKEN_EXPIRE_MINUTES).
4. Maintain the existing streaming API – the front‑end should not change.
5. Add unit & integration tests for the new behavior.
6. Document the changes in the repo README and comment code where relevant.
