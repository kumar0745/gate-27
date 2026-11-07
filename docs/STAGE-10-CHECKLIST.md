# Stage 10 — Personalised Study Planner

## Implemented

- [x] Authenticated planner overview API scoped to the signed-in student and selected GATE paper.
- [x] 30-, 60- and 90-day plan generation.
- [x] Uses the student's saved daily study-hour preference unless an explicit plan override is supplied.
- [x] Uses imported syllabus topic IDs and topic names; refuses to fabricate a topic plan for papers without a structured syllabus import.
- [x] Prioritises topics with latest-attempt practice accuracy below 60%, followed by in-progress topics, not-started topics and completed topics.
- [x] Generates topic-learning and retrieval/practice blocks, first spaced reviews, General Aptitude source-led tasks and weekly mock/review blocks.
- [x] Reserves weekly mock/review days from the normal first-pass topic workload.
- [x] Constrains generated daily task loads to the configured study-hour capacity for tested 1-hour and 5-hour CS plans.
- [x] Persists plans, scheduled tasks and revision queue entries in additive SQLite tables.
- [x] Archives a previous active plan when a replacement plan is generated.
- [x] Lets students complete, reopen, skip and move their own tasks to a later date.
- [x] Updates syllabus topic status to `in_progress` after a learning block is completed, without downgrading an already-completed topic.
- [x] Uses a review-quality choice (`again`, `hard`, `good`, `easy`) to adapt the next spaced-repetition interval.
- [x] Supports personal custom tasks attached to the active plan.
- [x] Reschedules overdue pending tasks into the next seven days while considering daily capacity where possible.
- [x] Shows task completion, overdue count, time budget, weak topics and upcoming revisions.
- [x] Connects the planner's daily tasks to the dashboard's Today’s focus panel.
- [x] Adds a responsive planner UI with plan creation/regeneration, date selection, weekly view, revision queue, weak-topic list and custom task entry.
- [x] Keeps planner data private to each user.

## API endpoints

- `POST /api/planner/plans` — create or regenerate a 30/60/90-day plan.
- `GET /api/planner/overview?paper_code=CS&selected_date=YYYY-MM-DD` — plan summary, selected-day tasks, next-seven-day task list, revision queue and weak topics.
- `POST /api/planner/tasks` — create a personal task within the active plan.
- `PATCH /api/planner/tasks/{task_id}` — complete/reopen/skip a task, reschedule it or submit review quality for a revision task.
- `POST /api/planner/reschedule-overdue` — redistribute overdue pending tasks into the next seven days.

All endpoints require a valid student session and enforce owner-scoped queries.

## Scheduling logic

- The planner reads the versioned paper syllabus and current student topic progress.
- The planner reads latest attempts per practice question to estimate topic accuracy. Topics below 60% latest-attempt accuracy are prioritised.
- Each non-completed topic gets a 35-minute learning block and a 20-minute retrieval/practice block. Topics without an imported practice question receive an explicit active-recall task; the planner does not claim that an unavailable question bank exists.
- A first revision task is scheduled one day after the learning block. Completing it updates the revision queue using the student's recall rating. The interval is adapted and capped at 45 days.
- General Aptitude tasks link to the official common syllabus but disclose that topic-level GA imports are pending.
- Weekly mock/review days are kept separate from the normal topic block schedule. A full mock is scheduled only when a validated paper mock manifest exists; lower daily-hour plans receive a shorter sectional block.
- If the available daily hours cannot cover every imported topic in the selected plan duration, the API returns the number of topics left outside the plan and a capacity explanation.

## Data tables

- `study_plans` — plan owner, paper, duration, daily hours, date range, plan status and generated-content settings.
- `planner_tasks` — generated and personal task blocks, scheduled date, duration, priority, status and metadata.
- `planner_revision_queue` — next spaced-review date, interval, review count and ease factor per topic.

The migration is additive and leaves existing Stage 1–9 tables and data intact.

## Validation

- Automated planner tests cover authentication, profile-hour defaults, 30-day capacity, invalid duration, unsupported paper content, plan regeneration, task completion and topic progress, revision interval updates, custom tasks, overdue rescheduling, owner isolation, weak-topic detection, date filtering and reserved weekly mock days.
- The full backend suite passes 94 tests.
- JavaScript syntax and Python compilation pass.
- Existing local SQLite database migration was run and the three Stage 10 tables were confirmed present.
- Browser-level visual automation remains unverified in this execution environment because its Chromium policy blocks local application navigation.

## Content boundary

The fully structured topic planner is initially available for GATE CS because that is the first topic-level syllabus import. Other papers show an explicit pending state until their official syllabus topics are structured. General Aptitude is a shared official source-led block; its topic-level GATEPath content remains pending.
