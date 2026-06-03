from playwright.sync_api import (
    Playwright,
    Browser,
    BrowserContext,
    Page
)

from all_models.RuntimeJob import RuntimeJob


class ActiveJobStore:

    active_jobs: dict[str, RuntimeJob] = {}

    @classmethod
    def add_job(
        cls,
        job_id: str,
        playwright: Playwright,
        browser: Browser,
        context: BrowserContext,
        page: Page
    ) -> RuntimeJob:

        runtime_job = RuntimeJob(
            playwright=playwright,
            browser=browser,
            context=context,
            page=page
        )

        cls.active_jobs[job_id] = runtime_job

        return runtime_job

    @classmethod
    def get_job(
        cls,
        job_id: str
    ) -> RuntimeJob | None:

        return cls.active_jobs.get(job_id)

    @classmethod
    def remove_job(
        cls,
        job_id: str
    ) -> None:

        runtime = cls.active_jobs.get(job_id)

        if runtime:
            runtime.page.close()
            runtime.context.close()
            runtime.browser.close()
            runtime.playwright.stop()

        cls.active_jobs.pop(job_id, None)
