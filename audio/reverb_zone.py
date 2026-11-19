"""第 53 批：进隧道、出山洞、下水时回声突然切换、尾音断、室内...

修复点：
- 体积权重过渡（zone_weight）替代包围盒硬切；
- 淡入淡出（fade_both）替代只淡入不淡出；
- 早期反射与尾响合并到统一总线（combine_early_late）；
- 室内外分流，室内屏蔽室外风声（indoor_outdoor）；
- portal 按门开合做低通（portal_lowpass）；
- 声源/听者双端取听者区（zone_for_source）；
- 暂停时冻结混响总线（pause_freeze）；
- 多区重叠权重归一（normalize_overlap）；
- IR 重采样到混音台采样率（ir_resample）；
- 动态门状态变化更新 portal（door_update）。
"""


def zone_weight(distance, inner, outer):
    """按体积边界返回混响区权重。

    distance <= inner 时完全在区内，权重 1；distance >= outer 时完全
    离区，权重 0；两者之间线性过渡，避免包围盒硬切。
    """
    if distance <= inner:
        return 1.0
    if distance >= outer:
        return 0.0
    span = outer - inner
    if span <= 0:
        return 0.0
    weight = (outer - distance) / span
    return min(1.0, max(0.0, weight))


def fade_both(fade_in, fade_out, t):
    """同时淡入淡出混响区。

    在 [fade_in, fade_out] 上构造三角包络：两端为 0，中点为 1，
    上升段淡入、下降段淡出，修复过渡只淡入不淡出导致的尾音断。
    """
    if fade_out <= fade_in:
        return 0.0
    if t <= fade_in or t >= fade_out:
        return 0.0
    mid = (fade_in + fade_out) / 2.0
    if t <= mid:
        return (t - fade_in) / (mid - fade_in)
    return (fade_out - t) / (fade_out - mid)


def combine_early_late(early, late):
    """合并早期反射与尾响。"""
    return early + late


def indoor_outdoor(is_indoor, wind):
    """室内时屏蔽室外风声。"""
    return 0.0 if is_indoor else wind


def portal_lowpass(open_ratio, cutoff):
    """按门开合返回 portal 低通。

    全开（open_ratio=1）时截止频率不变；门越关截止频率越低，
     portal 连通声被低通闷化，避免开门状态直通。
    """
    ratio = min(1.0, max(0.0, open_ratio))
    return cutoff * ratio


def zone_for_source(source_zone, listener_zone):
    """声源与听者不同区时取听者区。"""
    return listener_zone


def pause_freeze(samples, paused):
    """暂停时冻结混响总线。"""
    return 0 if paused else samples


def normalize_overlap(weights):
    """归一化多个重叠混响区权重。

    多区重叠时按各自权重占比分摊，总和为 1，替代按列表顺序取值；
    总权重为 0 时返回全 0，避免除零。
    """
    total = sum(weights)
    if total <= 0:
        return [0.0 for _ in weights]
    return [w / total for w in weights]


def ir_resample(source_rate, mix_rate):
    """把脉冲响应重采样到混音台采样率。

    返回输出/输入采样点数比率 mix_rate / source_rate；同采样率时为 1。
    """
    if source_rate <= 0:
        raise ValueError("source_rate must be positive")
    return mix_rate / source_rate


def door_update(is_open, previous):
    """动态门状态变化时更新 portal。

    门开合状态相对上一帧发生翻转时返回 True，触发 portal 重新计算
    （含低通与连通性）；状态未变返回 False。
    """
    return bool(is_open != previous)
