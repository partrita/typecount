## 2025-01-24 - [Confirmation Dialogs for Destructive Actions]
**Learning:** In a utility app where data is generated through passive activity (like typing), users can easily lose progress through accidental resets or by closing the window. Standardizing confirmation dialogs for all destructive paths (Reset button, Quit button, and Window Close 'X') significantly improves data safety.
**Action:** Always track the 'dirty' state of session data and implement a unified `on_quit` handler that is bound to both the Quit button and the `WM_DELETE_WINDOW` protocol in Tkinter apps.
