import time
import cProfile
import pstats
import io
import logging
from typing import Callable, Any, TypeVar, cast
from functools import wraps
from django.db import connection

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

class QueryProfiler:
    """
    Object-Oriented Profiler for executing performance analysis and EXPLAIN ANALYZE.
    """
    def __init__(self, analyze: bool = True) -> None:
        self.analyze = analyze

    def __call__(self, func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = cProfile.Profile()
            profiler.enable()
            start_time: float = time.time()
            initial_queries: int = len(connection.queries)

            result: Any = func(*args, **kwargs)

            profiler.disable()
            end_time: float = time.time()
            final_queries: int = len(connection.queries)

            self._log_stats(profiler, func.__name__, end_time - start_time, final_queries - initial_queries)
            self._explain_analyze(result)

            return result
        return cast(F, wrapper)

    def _log_stats(self, profiler: cProfile.Profile, func_name: str, exec_time: float, query_count: int) -> None:
        """
        Processes and logs the profiling statistics.
        """
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream).sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats(10)
        logger.info(f"Execution Profile for {func_name}: {exec_time:.4f}s | Queries: {query_count}")
        logger.info(stream.getvalue())

    def _explain_analyze(self, queryset: Any) -> None:
        """
        Executes PostgreSQL EXPLAIN ANALYZE if applicable to the returned object.
        """
        if self.analyze and hasattr(queryset, 'explain'):
            try:
                explain_output: str = queryset.explain(analyze=True)
                logger.info(f"EXPLAIN ANALYZE:\n{explain_output}")
            except Exception as exc:
                logger.warning(f"EXPLAIN ANALYZE Execution Failed: {exc}")