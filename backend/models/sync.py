"""Sync System Models"""
from pydantic import BaseModel
from typing import Optional, List


class SyncConfigUpdate(BaseModel):
    config_key: str
    config_value: str


class SyncTriggerRequest(BaseModel):
    job_type: str = 'full_sync'  # 'full_sync', 'new_episodes_check', 'analytics_calculation'


class EmailTestRequest(BaseModel):
    test_email: Optional[str] = None  # If None, use admin_email from config
