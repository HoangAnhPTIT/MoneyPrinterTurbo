from dataclasses import dataclass
from typing import List, Type

from app.services.mathflow.scenes import double_integral as di


@dataclass(frozen=True)
class Beat:
    key: str
    narration_vi: str
    scene_cls: Type
    anim_min_secs: float


BEATS: List[Beat] = [
    Beat(
        key="intro_1d",
        narration_vi=(
            "Hãy bắt đầu từ tích phân một lớp. "
            "Nó cho ta diện tích nằm dưới một đường cong."
        ),
        scene_cls=di.Intro1DScene,
        anim_min_secs=11.0,
    ),
    Beat(
        key="surface_3d",
        narration_vi=(
            "Bây giờ ta nâng lên không gian ba chiều, "
            "với một mặt cong z bằng f của x và y."
        ),
        scene_cls=di.Surface3DScene,
        anim_min_secs=14.0,
    ),
    Beat(
        key="cell_dA",
        narration_vi=(
            "Trên mặt phẳng xy, ta lấy một ô diện tích rất nhỏ, "
            "ký hiệu dA bằng dx nhân dy."
        ),
        scene_cls=di.CellDAScene,
        anim_min_secs=12.0,
    ),
    Beat(
        key="volume_column",
        narration_vi=(
            "Dựng một cột thẳng đứng từ ô nhỏ đó lên tới mặt cong. "
            "Thể tích của cột bằng f của x, y nhân với dA."
        ),
        scene_cls=di.VolumeColumnScene,
        anim_min_secs=14.0,
    ),
    Beat(
        key="riemann_sum",
        narration_vi=(
            "Cộng rất nhiều cột nhỏ như vậy lại, "
            "ta xấp xỉ được thể tích: tổng kép của f nhân delta A."
        ),
        scene_cls=di.RiemannSumScene,
        anim_min_secs=14.0,
    ),
    Beat(
        key="slice",
        narration_vi=(
            "Ta cũng có thể cắt mặt cong bằng các lát phẳng. "
            "Cộng diện tích các lát chính là tích phân lặp."
        ),
        scene_cls=di.SliceScene,
        anim_min_secs=13.0,
    ),
    Beat(
        key="conclusion",
        narration_vi=(
            "Khi các ô nhỏ vô hạn, tổng trở thành tích phân hai lớp: "
            "thể tích bằng tích phân kép của f trên miền D."
        ),
        scene_cls=di.ConclusionScene,
        anim_min_secs=12.0,
    ),
]
