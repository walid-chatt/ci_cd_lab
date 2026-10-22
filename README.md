# CI/CD, one small step at a time

This is a standalone practice project. It does not change the Airflow lab and
does not describe any company's infrastructure. Its runtime Python code needs no
external packages. Its development tools are pytest and Ruff, pinned by uv.lock.

## What happens where?

| Piece | Job |
|---|---|
| pipeline.py | Calculate two fictional commodity stress losses and print JSON |
| tests/test_pipeline.py | Check expected numbers, short-position signs and invalid inputs |
| scripts/ci.sh | Run the complete local quality gate |
| .github/workflows/ci.yml | Ask GitHub to run that same script for PRs and pushes to main |
| .gitlab-ci.yml | Equivalent script execution if you host this project in GitLab |
| .github/workflows/release.yml | Manually check, build, smoke-test and publish a container image |
| Dockerfile | Describe how to package the Python program |
| deploy/dev/cronjob.yaml | Describe which image Kubernetes should run daily |
| argocd/application.yaml | Tell Argo CD which Git repository and folder to watch |

CI checks integration. Continuous delivery makes a checked version ready for
release; continuous deployment automatically releases it after the configured
gates. A green CI result does not prove that production data and all possible
behaviours are correct. It proves that the checks you wrote passed.

## First exercise: run CI by hand

From this folder, with uv available:

```bash
uv sync --locked
uv run python pipeline.py
bash scripts/ci.sh
```

Expected result: seven tests pass, lint/format checks pass, and the report shows
a total P&L of -945000 for a -10% shock. The script returns a nonzero exit status
when a command fails. GitHub uses that status to mark the job red.

Read the three pieces in this order: pipeline.py, tests/test_pipeline.py,
scripts/ci.sh. You can run the checks one by one before running the whole script.

## Second exercise: make CI catch a bug

In pipeline.py, change:

```python
return round(quantity * price * shock, 2)
```

to:

```python
return round(abs(quantity * price * shock), 2)
```

Run `bash scripts/ci.sh`. The tests for long-position losses must fail. Restore
the original calculation and run it again: it should pass. This is a business
behaviour test: the formatting checker cannot catch the sign error.

The supplied project starts correct. The deliberate bug was exercised on a
temporary copy during verification, not left in the deliverable.

## Third exercise: use your Git commands and see GitHub CI

Create a new empty practice repository in GitHub (no generated README), then
replace YOUR-ACCOUNT and YOUR-REPO in these commands with its actual URL. From
this project's folder:

```bash
git init -b main
git add .
git commit -m "Add working CI practice lab"
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-REPO.git
git push -u origin main
git checkout -b practice/stress-sign
```

There is no clone here because you already have the local project. If you clone
an existing repository instead, copy these files into that checkout and follow
your team's branch workflow rather than initializing another repository.

Put the deliberate bug on the practice branch, commit and push it:

```bash
git add pipeline.py
git commit -m "Practice: introduce a stress sign bug"
git push -u origin practice/stress-sign
```

Open a PR to main. Open its Checks tab and the Python checks job. Read the failed
assertions. Fix the same line locally, commit, and `git push`. The same PR gets
a new workflow run. Enable a required status check in repository branch rules
if you want a red CI result to block merging; that is a separate GitHub setting.

GitHub event -> workflow -> job -> runner -> ordered steps -> your Bash script.
`uses:` calls an action maintained by someone else. `run:` executes your command.
The workflow YAML schedules the work; it does not generate tests for you.

The provided .gitlab-ci.yml also runs the same Bash script. GitHub ignores that
file; GitLab uses it. The GitLab example uses its default push-pipeline behaviour;
teams can add explicit rules for merge-request pipelines and protected branches.

## Fourth exercise: understand the CD handoff

The CI workflow does not publish or deploy. The separate Release image (manual)
workflow runs only when you explicitly choose it in GitHub Actions. Choose main.
It reruns checks, then builds the Dockerfile, runs the image once as a smoke test,
and uploads it to GitHub Container Registry with a tag based on the source commit.
Its permissions and your organization/package policies must allow publication.
Copy the exact published image into deploy/dev/cronjob.yaml. Commit that manifest
change on a new branch and have it reviewed/merged. A separate deployment-config
repository is common in teams; this lab keeps the folders in one repo for clarity.

Replace repoURL in argocd/application.yaml and register the Application with an
existing Argo CD instance. Repository access and a target Kubernetes cluster must
already be configured. If the image package is private, Kubernetes also needs
registry pull credentials supplied by the platform team; GitHub's temporary CI
token does not give the cluster access automatically. Do not commit credentials.

Argo CD compares deploy/dev in Git against Kubernetes. When they differ it shows
OutOfSync. Click Sync to apply the desired configuration. This example uses manual
sync. Auto-sync is an optional policy your team can enable later. Argo does not
build the image or fetch your Python dependencies. Kubernetes pulls the image and
runs the workload. This CronJob runs at 06:00 UTC; changing it does not mean the
next daily execution has already happened or produced correct data.

Synced means live resources match Git. Healthy means the configured health checks
look good. Neither alone proves the report is financially correct. Use job logs,
tests and data-quality monitoring too. A rollback normally means reviewing and
reverting the manifest's image reference to a known-good version in Git, then
syncing. This does not undo database migrations or data already written.

## What to ask your future team

- Do we use Argo CD, Argo Workflows, Argo Rollouts, or several of them?
- Where is the deployment-config repository, and how do dev/staging/prod promotions work?
- Which registry holds the images, and how are versions or digests selected?
- Who approves deployment changes, and is sync automatic or manual?
- Where are runtime credentials, failed-job logs and data-quality alerts?
- For Airflow specifically, how are DAGs delivered: Git sync, images, bundles, or another mechanism?

Airflow orchestrates data tasks. Argo CD reconciles Kubernetes deployment config.
Argo Workflows runs Kubernetes workflows; Argo Rollouts handles advanced rollout
strategies. These are distinct products in the Argo family.

## Verification limits

The local CI script and deliberate failing-test exercise can run on this Mac.
Verification completed: the unmodified script passed all seven tests, lint,
formatting and the report smoke test. The deliberately broken copy produced two
failed and five passing tests. Bash syntax and YAML parsing were checked.
GitHub-hosted execution requires pushing to your practice repository. Image builds
require Docker (available on GitHub's Ubuntu runner); actual Argo CD deployment
requires an existing cluster and configured access. The templates are not a live
deployment. No remote repository, image publication or cluster change was made
while preparing this project.

## Sources

- https://docs.github.com/en/actions/get-started/understand-github-actions
- https://docs.astral.sh/uv/guides/integration/github/
- https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images
- https://argo-cd.readthedocs.io/en/stable/user-guide/ci_automation/
- https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/
- https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/
