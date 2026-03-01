## 2025-03-01 - [Secure Data Handling and Information Disclosure]
**Vulnerability:** Insecure file handling (non-atomic writes, permissive permissions) and information disclosure of full system paths in UI.
**Learning:** Captured typing data can contain sensitive information (patterns, passwords if typed during active monitoring). Storing this in world-readable CSVs or losing data during a crash/interrupt poses a risk to both privacy and data integrity.
**Prevention:** Always use atomic writes (temp file + replace) for data files and restrict permissions to the owner only (0600). Use `Path.name` to avoid leaking the host filesystem structure in user-facing messages.
