from eo_kafka.events import StudentPhotoUpdated
from opentelemetry import trace


tracer = trace.get_tracer(__name__)


async def process_new_student_photo(event: StudentPhotoUpdated) -> None:
    with tracer.start_as_current_span("process_new_student_photo"):
        ...


EVENTS_TO_CONSUME = {
    StudentPhotoUpdated: process_new_student_photo,
}
