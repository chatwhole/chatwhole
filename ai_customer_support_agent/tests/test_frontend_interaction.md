# Frontend Interaction Test Plan

## Test Chat Widget UI

- Open the chat widget page.
- Verify the initial greeting message is displayed.
- Type a query in the input box and send.
- Verify the user message appears in the chat window.
- Verify the bot response is received and displayed.
- Test sending empty messages (should be ignored).
- Test rapid multiple messages.
- Test error handling when backend is unreachable.

## Test End-to-End Flow

- Start backend server.
- Start frontend app.
- Send queries and verify responses.
- Check logs for errors.

## Notes

- Use browser developer tools to monitor network requests.
- Test on multiple browsers and devices if possible.
