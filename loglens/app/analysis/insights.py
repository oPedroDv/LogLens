from app.types.analysis_result import AnalysisResult
from app.types.log_entry import LogEntry
from app.analysis.statistics import compute_error_sources, compute_hourly_distribution

ERROR_RATE_HIGH = 0.10
ERROR_RATE_CRITICAL = 0.25
PARSE_RATE_LOW = 0.70
SOURCE_CONCENTRATION_THRESHOLD = 0.50
HOURLY_SPIKE_MULTIPLIER = 3

def _insight_error_rate(result: AnalysisResult) -> str | None:
    rate = result.level_distribution.error_rate

    if rate >= ERROR_RATE_CRITICAL:
        return (
            f"Taxa de erro crítica: {rate:.1%} dos logs são ERROR ou CRITICAL. "
            f"Isso sugere instabilidade significativa no sistema analisado."
        )
    elif rate >= ERROR_RATE_HIGH:
        return (
            f"Taxa de erro elevada: {rate:.1%} dos logs indicam falhas. "
            f"Vale investigar as fontes mais afetadas."
        )
    return None

def _insight_parse_quality(result: AnalysisResult) -> str | None:
    rate = result.parse_success_rate

    if rate < PARSE_RATE_LOW:
        return (
            f"Apenas {rate:.1%} das linhas foram interpretadas com sucesso. "
            f"O formato deste log pode não ser totalmente compatível "
            f"com os padrões reconhecidos — as estatísticas podem estar incompletas."
        )
    return None


def _insight_source_concentration(result: AnalysisResult, entries: list[LogEntry]) -> str | None:
    error_sources = compute_error_sources(entries, limit=1)

    if not error_sources:
        return None

    top_source, top_count = error_sources[0]
    total_errors = sum(1 for e in entries if e.is_error())

    if total_errors == 0:
        return None

    concentration = top_count / total_errors

    if concentration >= SOURCE_CONCENTRATION_THRESHOLD:
        return (
            f"'{top_source}' concentra {concentration:.1%} de todos os erros "
            f"({top_count} ocorrências) — provável ponto de falha principal."
        )
    return None


def _insight_hourly_spike(entries: list[LogEntry]) -> str | None:
    hourly = compute_hourly_distribution(entries)
    active_hours = {h: count for h, count in hourly.items() if count > 0}

    if len(active_hours) < 2:
        return None

    values = list(active_hours.values())
    average = sum(values) / len(values)
    peak_hour = max(active_hours, key=active_hours.get)
    peak_count = active_hours[peak_hour]

    if average > 0 and peak_count >= average * HOURLY_SPIKE_MULTIPLIER:
        return (
            f"Pico de atividade detectado às {peak_hour:02d}h, com {peak_count} "
            f"registros — bem acima da média horária de {average:.0f}."
        )
    return None


def _insight_volume_density(result: AnalysisResult) -> str | None:
    if result.time_range is None or result.time_range.duration_seconds <= 0:
        return None

    lines_per_second = result.total_lines / result.time_range.duration_seconds

    if lines_per_second > 10:
        return (
            f"Densidade de log muito alta: {lines_per_second:.1f} linhas/segundo "
            f"em média. Pode indicar um loop de erro ou logging excessivamente verboso."
        )
    return None


def generate_insights(result: AnalysisResult) -> list[str]:
    checks = [
        _insight_error_rate(result),
        _insight_parse_quality(result),
        _insight_source_concentration(result, result.entries),
        _insight_hourly_spike(result.entries),
        _insight_volume_density(result),
    ]

    insights = [insight for insight in checks if insight is not None]

    if not insights:
        insights.append(
            "Nenhuma anomalia significativa detectada — os logs aparentam "
            "comportamento normal dentro dos parâmetros analisados."
        )

    return insights