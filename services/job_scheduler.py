from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import create_engine

job_stores = {
        'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    }

scheduler = AsyncIOScheduler(jobstores=job_stores)
