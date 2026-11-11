# Behavioral Interviews, the Hiring Process and Your Preparation Plan: Exercises

These problems go with the [Behavioral Interviews, the Hiring Process and Your Preparation Plan lesson](README.md). Try each one before opening its solution.

## Problems

1. Write your 60-second pitch using the present, past, future structure. Time yourself and trim to 75 seconds maximum.
2. Write eight STAR stories (one per theme in the table). For each include one number and one lesson.
3. Rewrite these weak resume bullets into strong, quantified ones (invent plausible numbers and mark them as examples):
   - "Responsible for backend API development."
   - "Worked on improving performance."
   - "Helped with migration to the cloud."
4. Take a failure story and rewrite it so that the **Action** section contains at least four of your own decisions and the **Result** includes a process change.
5. Prepare answers to: "Why do you want to leave your current job?", "What is your biggest weakness?", "Why this company?" (choose a real company) without criticizing anyone.
6. Write five questions you would ask the interviewer for a backend role, and explain what each helps you learn.
7. Draft a negotiation email for an offer with base 1,000 below your target, with a competing offer in hand. Keep it collaborative and factual.
8. Build your own 12-week study plan with specific weekly goals based on your weakest areas (self-assess each handbook part from 1 to 5 first).
9. Run a 45-minute mock interview with a friend: 30 minutes for one problem, 10 minutes for a behavioral question, 5 minutes for your questions. Write down three improvement points.
10. Create a job-search tracker (spreadsheet columns) and a weekly routine for applications, referrals, practice and rest.

<details>
<summary>Model solutions</summary>

**1. Example pitch (about 70 seconds):** "I'm a backend engineer at an outsourcing company building Python services for data collection and automation. Last year I redesigned a nightly pipeline around async I/O and a job queue, cutting its runtime from six hours to forty minutes, and I own its monitoring and on-call. Before that I built Django REST APIs for a healthcare client. I'm now looking for a product team working on reliability and data at scale, and your platform team's work on streaming pipelines is exactly that."

**2. Story bank template (repeat per theme):**
```text
Theme: ownership
S: Our nightly pipeline took 6 hours and delayed customer reports.
T: I was asked to cut it below 1 hour without raising cloud cost.
A: I profiled it (80% in sequential HTTP and row-by-row inserts), moved fetching to asyncio with a semaphore, batched inserts with executemany, added a retry/backoff layer, and wrote regression tests with recorded responses.
R: Runtime 6 h -> 40 min, cost -15%, zero missed reports for 6 months. Learned: profile before optimizing.
```

**3.**
- "Designed and shipped 12 Django REST endpoints serving 2M requests/day with p95 latency under 120 ms; added Redis caching that cut database load by 45%."
- "Cut report-generation time from 90 s to 8 s by replacing N+1 queries with joins and adding two composite indexes."
- "Led migration of 6 services from on-premise VMs to AWS ECS, automating deployments with GitHub Actions and reducing release time from 2 hours to 15 minutes."

**4.** Actions to include: roll back immediately, communicate to affected stakeholders, write a script to repair data, find the root cause, write the post-mortem, add automated tests, add a staging check or alert, change the review checklist. Result: "no repeat incidents; the validation step was adopted by two other teams."

**5.** Leaving: "I've learned a lot and shipped a lot here, and I'm looking for broader technical scope and a team working on X." Weakness: "I used to take on too much myself; now I timebox, ask for help early and delegate or document." Why this company: a specific product/engineering-blog/open-source detail plus how your experience connects.

**6.** (1) "What would success look like in six months?" (expectations), (2) "How do you handle on-call and incidents?" (operational maturity and workload), (3) "What is the biggest technical debt?" (honest picture), (4) "How are technical decisions made?" (autonomy and culture), (5) "How does the team collaborate across time zones?" (remote fit).

**7.**
```text
Subject: Offer for Backend Engineer: thank you and a question

Hi <Name>,

Thank you again for the offer; I'm excited about the team and the platform work. I've been weighing it against another offer, and based on my experience with <X, Y> and the market range for this level, I was hoping for a base of <target>. If we can get closer to that, I'm ready to accept. Is there flexibility?

Thanks for your time,
<You>
```

**8.** Example: self-assessment (data structures 4, algorithms 3, OOP 4, databases 3, OS 2, networking 3, system design 2, behavioral 3) -> spend weeks 1-2 on algorithm patterns, weeks 3-5 on system design and OS, one week on SQL, and keep 2 hours per week on behavioral stories throughout.

**9.** Typical improvement points: clarify requirements earlier; talk while coding instead of long silences; test edge cases before declaring done.

**10.** Columns: Company | Role | Link | Source (referral/portal) | Date applied | Stage | Contacts | Next action and date | Notes | Outcome. Weekly routine: Mon batch of applications, Tue-Thu two timed problems per day + 30 min concepts, Wed mock interview, Fri referrals and follow-ups, weekend rest and review.

</details>

[Lesson](README.md) · [Summary](summary.md)
