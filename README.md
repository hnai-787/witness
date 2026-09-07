# Software Testing with Selenium

## Course Information

| Field | Details |
|---|---|
| Course | Introduction to Software Engineering (CS112) |
| Semester | Semester 2 — Spring 2024 |
| University | Air University, Islamabad |
| Students | Syed Jazib Ali Rizvi (232145), Hussain Ali (232095), Shehroze Sameer (232091), Qalb e Abbas (232133) |

## Overview

A non-functional (load/stress) testing exercise using Selenium IDE's
record-and-playback tooling against two targets: Air University's
student-portal login page, and Wikipedia's search engine.

## Problem Statement

Demonstrate non-functional (load) testing using Selenium IDE's recording
tools against real, live web applications rather than a local test target.

## Objectives

- Record and replay login flows against the AU student portal under load.
- Record and replay search interactions against Wikipedia.
- Report findings and recommendations.

## Tools and Technologies

- Selenium IDE (recording/playback)
- Selenium WebDriver / Grid toolkit (referenced in the report)

## Features

N/A — no custom test scripts were exported/committed; testing was done via Selenium IDE's point-and-click recorder.

## Methodology

1. Record a login flow against the AU student-portal login page in Selenium IDE.
2. Record a search flow against Wikipedia.
3. Replay both under load via Selenium IDE.
4. Document observations and recommendations in the report.

## Repository Structure

```text
software-testing-with-selenium/
  README.md
  PROJECT_NOTES.md
  docs/software-testing-with-selenium.docx
  presentation/software-testing-with-selenium.pptx
  screenshots/
  project.yaml
```

## Setup Instructions

N/A — no test scripts are included; only the report, presentation, and screenshots.

## Usage

N/A.

## How to Review

1. Start with this README, then `docs/software-testing-with-selenium.docx`.
2. Review `presentation/software-testing-with-selenium.pptx` (15 slides).
3. Check `screenshots/` for the Selenium IDE recording/comparison views (10 images — none show the actual AU portal, only generic Selenium IDE UI and Wikipedia).

## Screenshots

See `screenshots/` — project description, methodology, Selenium recording/overview/comparison, test-case design/execution, and results slides.

## Results

The report states no problems were identified: the login flow signed in
successfully under the tested load, and Wikipedia's search engine
performed correctly. No quantitative load numbers (response times,
concurrent-user counts) are documented in the source report — the findings
are qualitative only.

## Limitations

- No exported/committed test scripts — the Selenium IDE project files were not saved with the submission.
- No quantitative performance data (response times, throughput, concurrency levels) was recorded.

## Future Enhancements

- Export and version-control the actual Selenium IDE test suites.
- Capture quantitative load metrics rather than a qualitative pass/fail summary.

## Safety and Privacy

- No real credentials or portal screenshots are exposed — the checked screenshots show only the generic Selenium IDE interface and Wikipedia.
- No student personal data is included beyond the standard group-authorship names below.

## Ethical Notice

This project performed non-functional (load) testing against **Air
University's real, live student-portal login page**. The source report
does not document explicit authorization from the university's IT
department for this testing. It is included here as submitted coursework
for portfolio purposes, but this gap is flagged deliberately: testing a
real third-party system's authentication endpoint under load, without
documented authorization, is a genuine gray area — treat it as a lesson
in scoping test targets carefully, not as a model to repeat without
first securing explicit permission from the system owner.
