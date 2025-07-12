from enum import Enum


class ProjectStatus(str, Enum):
    queued= 'queued'
    processing = 'processing'
    complete = "complete"
    error = "error"