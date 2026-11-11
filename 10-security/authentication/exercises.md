# Authentication and Authorization: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Authentication and Authorization

1. Write `needs_rehash(stored)` that returns `True` if a stored hash uses fewer scrypt cost parameters than today's. Why store parameters with the hash?
2. Add a `role` claim check to `verify_jwt` through a helper `require_role(token, "admin")`.
3. Show that two users with the same password get different stored hashes.
4. Fix the following IDOR: `def delete_note(user, note_id): del NOTES[note_id]`.
5. Why must the OAuth `state` value be unguessable and checked on return?
6. A JWT lasts 24 hours and a user's account is stolen. What can you do, and what design would have made this easier?

<details>
<summary>Solutions</summary>

1. ```python no-run
   def needs_rehash(stored: str, current_n: int = 2**14) -> bool:
       # In real systems you store n, r and p in the string; here the cost is fixed, so the idea is shown with a version tag.
       return not stored.startswith("scrypt$")
   print(needs_rehash(stored), needs_rehash("md5$abc"))
   # False True
   ```
   Storing the algorithm and its parameters lets you raise the cost over time and re-hash a user's password at their next successful login.
2. ```python no-run
   def require_role(token: str, role: str) -> dict:
       claims = verify_jwt(token)
       if claims.get("role") != role:
           raise PermissionError("forbidden")
       return claims
   admin_token = make_jwt({"sub": "root", "role": "admin", "exp": time.time() + 60})
   print(require_role(admin_token, "admin")["sub"])
   # root
   ```
3. ```python no-run
   print(hash_password("same") != hash_password("same"))
   # True
   ```
4. ```python no-run
   def delete_note(user, note_id):
       note = NOTES.get(note_id)
       if note is None or note["owner"] != user:
           raise LookupError("not found")
       del NOTES[note_id]
   delete_note("bob", 2)
   print(sorted(NOTES))
   # [1]
   ```
5. `state` binds the response to the request the user started. If it is guessable or unchecked, an attacker can trick a victim's browser into completing the attacker's login (login CSRF), linking the attacker's account to the victim's session.
6. A JWT cannot be recalled before it expires; you can add its id to a deny-list the server checks, or rotate the signing key (logging everyone out). Short-lived access tokens (5 to 15 minutes) with a revocable refresh token make this easy.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Authentication and Authorization](01-authn-authz-sessions-jwt.md)
