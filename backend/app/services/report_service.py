"""
Report service.

The central orchestrator: given an uploaded file, runs it through OCR ->
extraction -> reference-range flagging -> health scoring -> recommendation
generation -> AI summary, and persists the results.
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ForbiddenException
from app.ml.recommendation_engine import RecommendationEngine
from app.models.parameter import ExtractedParameter
from app.models.recommendation import Recommendation
from app.models.report import Report, ReportStatus
from app.models.uploaded_file import UploadedFile
from app.repositories.report_repository import ReportRepository
from app.services.ai_service import AIService
from app.services.extraction_service import ExtractionService
from app.services.health_score_service import HealthScoreService
from app.services.ocr_service import OCRService
from app.services.reference_range_service import ReferenceRangeService

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.reports = ReportRepository(db)
        self.ocr_service = OCRService()
        self.extraction_service = ExtractionService()
        self.reference_range_service = ReferenceRangeService(db)
        self.health_score_service = HealthScoreService()
        self.ai_service = AIService()
        self.recommendation_engine = RecommendationEngine()

    def create_report_from_upload(
        self, owner_id: str, original_filename: str, storage_path: str,
        content_type: str, size_bytes: int, title: Optional[str] = None,
    ) -> Report:
        report = Report(owner_id=owner_id, title=title or original_filename, status=ReportStatus.UPLOADED)
        self.db.add(report)
        self.db.flush()  # get report.id before creating the child row

        uploaded_file = UploadedFile(
            report_id=report.id, original_filename=original_filename,
            storage_path=storage_path, content_type=content_type, size_bytes=size_bytes,
        )
        self.db.add(uploaded_file)
        self.db.commit()
        self.db.refresh(report)
        return report

    def process_report(self, report_id: str) -> Report:
        """
        Runs the full analysis pipeline synchronously. In a production
        deployment this would typically be dispatched to a background task
        queue (Celery/RQ) so the upload endpoint returns immediately; the
        pipeline itself is written to be queue-agnostic.
        """
        report = self.reports.get(report_id)
        if not report:
            raise NotFoundException("Report not found.")

        report.status = ReportStatus.PROCESSING
        self.db.commit()

        try:
            file_record = report.files[0] if report.files else None
            if not file_record:
                raise NotFoundException("No uploaded file associated with this report.")

            raw_text = self.ocr_service.extract_text(file_record.storage_path)
            report.raw_extracted_text = raw_text
            report.status = ReportStatus.EXTRACTED

            extracted_values = self.extraction_service.extract_parameters(raw_text)

            parameters: list[ExtractedParameter] = []
            for ev in extracted_values:
                flag, ref_range = self.reference_range_service.flag_value(ev.name, ev.value)
                param = ExtractedParameter(
                    report_id=report.id, name=ev.name, raw_text=ev.raw_text,
                    value=ev.value, unit=ev.unit, flag=flag, confidence=ev.confidence,
                    reference_range_id=ref_range.id if ref_range else None,
                )
                self.db.add(param)
                parameters.append(param)
            self.db.flush()

            score_result = self.health_score_service.score_report(parameters)
            report.health_score = score_result["health_score"]
            report.risk_category = score_result["risk_category"]

            flagged = [(p.name, p.flag) for p in parameters]
            for rec in self.recommendation_engine.generate_all(flagged):
                self.db.add(Recommendation(report_id=report.id, **rec))

            report.ai_summary = self.ai_service.generate_summary_with_llm(parameters, report.health_score)
            report.status = ReportStatus.ANALYZED
            self.db.commit()
            self.db.refresh(report)
            logger.info("Report %s processed successfully (%d parameters).", report.id, len(parameters))
            return report

        except Exception:
            logger.exception("Failed to process report %s", report_id)
            report.status = ReportStatus.FAILED
            self.db.commit()
            raise

    def get_report_for_user(self, report_id: str, user_id: str) -> Report:
        report = self.reports.get_with_details(report_id)
        if not report:
            raise NotFoundException("Report not found.")
        if report.owner_id != user_id:
            raise ForbiddenException("You do not have access to this report.")
        return report

    def delete_report(self, report_id: str, user_id: str) -> None:
        report = self.get_report_for_user(report_id, user_id)
        self.reports.delete(report)
