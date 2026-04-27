def test_weather_is_advisory():
    from continuity_weather_layer_r1 import build_continuity_weather

    metrics = {"lock": 0.5, "presence": 0.4}
    weather = build_continuity_weather(metrics)

    assert "weather_state" in weather
    assert "authority_boundary" in weather


def test_metrics_not_mutated():
    from continuity_weather_layer_r1 import build_continuity_weather

    metrics = {"lock": 0.5}
    copy = dict(metrics)
    build_continuity_weather(metrics)

    assert metrics == copy
