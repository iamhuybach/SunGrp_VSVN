# Request

## User outcome

Một sơ đồ drawio để nhìn grain, cột và quan hệ của silver cùng gold đang chạy. File cũ chỉ để học cách trình bày.

Yêu cầu nguyên văn:

Dựa vào hình vẽ luồng cũ D:\git\SunGrp_VSVN\docs\diagram\VSVN_DATA_MODEL.drawio làm sample, hãy vẽ lại data model phần silver và gold hiện tại.
Lý do nghiệp vụ: một sơ đồ drawio để nhìn grain, cột và quan hệ của silver cùng gold đang chạy. File cũ chỉ để học cách trình bày.
Tiêu chí nghiệm thu:
- File mới docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio. Không sửa VSVN_DATA_MODEL.drawio.
- Hai trang trong cùng file: Silver và Gold. Gold gồm lh_vv_silver không nằm ở trang Gold. Gold gồm lh_vv_gold.dbo và lh_vv_gold.enr.
- Mỗi bảng hiện tại là một swimlane giống sample: tên bảng, grain, số cột, rồi từng cột kèm kiểu. PK đánh dấu từ pk của NodeSpec hoặc is_key của registry. Không có PK trong hai nguồn đó thì ghi không khai báo, không tự chọn cột.
- Màu và kiểu chữ lấy từ một thẻ swimlane của sample. Nội dung srv_* trong sample không được đưa sang file mới.
- Không vẽ khối Định nghĩa, Capability, Lifecycle, Freshness, Downstream. Những câu đó không có trong DDL hiện tại.
- Mũi tên chỉ những cạnh mà build của node hiện tại thực sự join, union, hoặc lấy làm dòng gốc. Nhãn cạnh dùng đúng nhãn của skill vsvn-data-model-flow. Không suy FK từ tên cột.
- Bảng có trong DDL nhưng không có node: vẫn có thẻ, không có mũi tên, ghi không có node.
- Không sửa notebook, DDL, pipeline, test, skill. Không đọc notebooks_lgc/ hay docs/context/01_DATA_MODEL.md §9.
Miền: lib transform/gold, DDL/registry, ctrl

## Scope

### In scope

- File mới `docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio`.
- Hai trang: Silver; Gold (`lh_vv_gold.dbo` và `lh_vv_gold.enr`).
- Mỗi bảng hiện tại trong phạm vi skill: swimlane tên bảng, grain, số cột, từng cột kèm kiểu.
- PK từ `pk` của NodeSpec hoặc `is_key` của registry. Không có trong hai nguồn thì ghi không khai báo.
- Mũi tên chỉ cạnh mà `build` của node hiện tại join, union, hoặc lấy làm dòng gốc. Nhãn theo skill `vsvn-data-model-flow`.
- Bảng có trong DDL nhưng không có node: thẻ, không mũi tên, ghi không có node.
- Bảng kiểm trong `decision.md` trước khi vẽ.
- Lệch skill (drawio có cột) ghi trong `decision.md` trước khi vẽ. Không sửa skill.

### Out of scope

- Sửa `docs/diagram/VSVN_DATA_MODEL.drawio`.
- Nội dung `srv_*` của sample.
- Khối Định nghĩa, Capability, Lifecycle, Freshness, Downstream.
- Suy FK từ tên cột.
- Sửa notebook, DDL, pipeline, test, skill.
- Đọc `notebooks_lgc/` hoặc `docs/context/01_DATA_MODEL.md` §9.
- Signal `data_model_change`. Probe Fabric.
- `lh_vv_silver` trên trang Gold.

## Acceptance criteria

- File mới `docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio`. Không sửa `VSVN_DATA_MODEL.drawio`.
- Hai trang trong cùng file: Silver và Gold. Trang Gold gồm `lh_vv_gold.dbo` và `lh_vv_gold.enr`. `lh_vv_silver` không nằm ở trang Gold.
- Mỗi bảng hiện tại là một swimlane giống sample: tên bảng, grain, số cột, rồi từng cột kèm kiểu. PK đánh dấu từ `pk` của NodeSpec hoặc `is_key` của registry. Không có PK trong hai nguồn đó thì ghi không khai báo, không tự chọn cột.
- Màu và kiểu chữ lấy từ một thẻ swimlane của sample. Nội dung `srv_*` trong sample không được đưa sang file mới.
- Không vẽ khối Định nghĩa, Capability, Lifecycle, Freshness, Downstream.
- Mũi tên chỉ những cạnh mà build của node hiện tại thực sự join, union, hoặc lấy làm dòng gốc. Nhãn cạnh dùng đúng nhãn của skill `vsvn-data-model-flow`. Không suy FK từ tên cột.
- Bảng có trong DDL nhưng không có node: vẫn có thẻ, không có mũi tên, ghi không có node.
- Số thẻ bằng số bảng. Số mũi tên bằng số cạnh đã gắn nhãn.

## Constraints

- Skill lệch yêu cầu drawio có cột: file drawio là sản phẩm của task này. Không sửa skill để thêm danh sách bảng. Ghi lệch đó trong `decision.md` trước khi vẽ.
- `01_DATA_MODEL` lệch NodeSpec hoặc DDL thì ghi `CONFLICT`, dừng ở `user_decision`, không chọn một bên.
- L1 không có node riêng: cột và khóa lấy từ registry seed, không bịa grain.
- Context đọc theo skill `vsvn-data-model-flow` mục Where the facts live và Procedure, cộng các anchor prompt đã nêu.
- Architecture chỉ khi §Classification bắt buộc với một file sơ đồ.
- Verify PASS rồi mới review, và chỉ khi phân loại yêu cầu review.
- Không đánh dấu runtime pass.

## Classification rationale

- Complexity: `low`. Không signal nào trong §Classification áp dụng. Task không đổi bảng, cột, grain, hay khóa, nên không gắn `data_model_change`.
- Risk: `low`. Không đổi hành vi runtime. Sản phẩm là một file sơ đồ.
- Architecture: không. Không đổi grain, khóa, chủ sở hữu trạng thái, ranh giới transaction, thứ tự commit, CDC, watermark, lock, retry, orchestration, hay cấu trúc pipeline. Không có nhiều cách triển khai với trade-off vật chất. Thay đổi nguồn là một file sơ đồ, không trải ba service hay tám file nguồn.
- Evidence: không. Đúng sai lấy từ DDL, registry seed, và notebook node trong repository. Không probe Fabric.
- Runtime proof: không. Sơ đồ không chạy trên Fabric.
- Reviewer routing: không reviewer. Không có triển khai SQL/Delta MERGE, notebook, pipeline, hay chuyển trạng thái trong scope. Risk `low` nên không `risk-gate`. `specialist_review` giữ `not_required`. Review chỉ chạy khi phân loại yêu cầu.
- Fast lane: có. `complexity=low`, `risk_level=low`, không đổi hành vi, một file nguồn đổi (`docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio`).
