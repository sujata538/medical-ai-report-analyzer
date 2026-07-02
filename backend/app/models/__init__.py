"""Aggregate import so Base.metadata sees every model."""
from app.models.user import User  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.report import Report, ReportStatus  # noqa: F401
from app.models.uploaded_file import UploadedFile  # noqa: F401
from app.models.parameter import ExtractedParameter, ParameterFlag  # noqa: F401
from app.models.reference_range import ReferenceRange  # noqa: F401
from app.models.recommendation import Recommendation, RecommendationSeverity  # noqa: F401
from app.models.user_session import UserSession  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
