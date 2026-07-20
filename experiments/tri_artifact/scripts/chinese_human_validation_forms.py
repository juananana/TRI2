from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "human_validation"

REWRITE_FORM = HUMAN / "01_独立改写者填写表_中文列名.csv"
PILOT_FORM = HUMAN / "作者试填_不计入正式统计.csv"

PILOT_TRANSLATIONS = {
    "Select the earliest upcoming meeting from the calendar now. After refreshing, open notes for that exact meeting.":
        "现在从日历中选出最早开始的待举行会议。刷新后，为刚才选中的同一场会议打开备注。",
    "Update the calendar data, then newly identify the earliest upcoming meeting and open notes for that meeting.":
        "先更新日历数据，然后根据更新后的日历重新找出最早开始的待举行会议，并打开该会议的备注。",
    "Resolve the cheapest in-stock product at this point. Following a reload of the store, purchase the previously resolved product.":
        "现在确定当前有库存商品中价格最低的一个。商店重新加载后，购买刚才已经确定的那个商品。",
    "Discard the pre-refresh ranking. Refresh the crm, identify the largest active sales lead anew, and assign that lead.":
        "不要沿用刷新前的排序。刷新客户关系系统后，重新找出价值最高的活跃销售线索，并分配该线索。",
    "Mark the most recently edited active document in the current drive list. Update the view and share that marked document.":
        "在当前云盘列表中标记最近编辑的活跃文档。更新视图后，分享刚才标记的文档。",
    "Synchronize the drive; then, from what is displayed afterward, locate the most recently edited active document and share it.":
        "先同步云盘，然后仅根据同步后显示的内容找出最近编辑的活跃文档，并分享它。",
    "Find the highest-priority unread email in the mailbox as it stands. Update the view, then reply to it.":
        "在当前邮箱中找出优先级最高的未读邮件。更新视图后，回复刚才找到的那封邮件。",
    "Mark the most delayed active shipment in the current logistics list. Update the view and expedite that marked shipment.":
        "在当前物流列表中标记延误最严重的活跃货件。更新视图后，加急刚才标记的货件。",
    "Pick the most delayed active shipment from the current list; after syncing the logistics, expedite it.":
        "从当前列表中选出延误最严重的活跃货件；同步物流数据后，加急刚才选中的货件。",
    "Once the support_console has refreshed, determine the highest-severity open ticket and escalate the resulting ticket.":
        "支持系统刷新完成后，找出严重等级最高的开放工单，并升级处理该工单。",
}

FIELD_ZH = {
    "id": "编号", "display": "名称", "start_minute": "开始时间（分钟）",
    "status": "状态", "owner": "负责人", "actionable": "可执行",
    "price": "价格", "in_stock": "有库存", "value": "价值",
    "edited_at": "编辑时间", "delay_hours": "延误小时", "severity": "严重等级",
    "priority": "优先级",
}

DISPLAY_ZH = {
    "Roadmap": "路线图会议", "Budget": "预算会议", "Hiring": "招聘会议",
    "Blue adapter": "蓝色转接器", "Travel charger": "旅行充电器", "USB hub": "USB集线器",
    "Acme": "阿克米", "Beta": "贝塔", "Gamma": "伽马",
    "Launch plan": "发布计划", "Risk log": "风险日志", "Archive": "归档文档",
    "Reset request": "重置请求", "Contract note": "合同说明", "Digest": "摘要",
    "Paris crate": "巴黎货箱", "Berlin box": "柏林包裹", "Rome case": "罗马箱",
    "Refund blocked": "退款受阻", "Invoice missing": "发票缺失", "Trace upload": "追踪上传",
}

VALUE_ZH = {
    True: "是", False: "否", "scheduled": "待举行", "active": "活跃",
    "closed": "关闭", "archived": "已归档", "delivered": "已送达",
    "unread": "未读", "read": "已读", "open": "开放",
}

REWRITE_FIELDS = {
    "source_task_id": "任务编号（勿修改）",
    "style": "指令类型（勿修改）",
    "update": "环境变化类型（勿修改）",
    "domain": "应用领域（勿修改）",
    "original_instruction": "原始英文指令（只读）",
    "rewrite_instruction": "英文自然改写（必填）",
    "author_notes": "改写者备注（可选）",
}

ANNOTATION_FIELDS = {
    "item_id": "题目编号（勿修改）",
    "instruction": "英文任务指令",
    "initial_state_json": "初始状态JSON",
    "refreshed_state_json": "刷新后状态JSON",
    "action_schema_json": "动作前置条件JSON",
    "candidate_ids": "候选ID（答案从中选择，或填REJECT/CLARIFY）",
    "response": "你的答案（ID/REJECT/CLARIFY）",
    "confidence_1_to_5": "信心1到5（可选）",
    "comment": "备注（可选）",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def export_rewrites() -> None:
    source = read_csv(HUMAN / "paraphrase_authoring.csv")
    rows = [
        {REWRITE_FIELDS[key]: row.get(key, "") for key in REWRITE_FIELDS}
        for row in source
    ]
    write_csv(REWRITE_FORM, rows, list(REWRITE_FIELDS.values()))


def import_rewrites() -> None:
    rows = read_csv(REWRITE_FORM)
    reverse = {value: key for key, value in REWRITE_FIELDS.items()}
    normalized = [{reverse[key]: value for key, value in row.items()} for row in rows]
    completed = [row for row in normalized if row["rewrite_instruction"].strip()]
    if len(normalized) != 50 or len(completed) != 50:
        raise ValueError(
            f"需要完成全部50条英文改写；当前总行数{len(normalized)}，已完成{len(completed)}。"
        )
    write_csv(
        HUMAN / "paraphrase_authoring.csv",
        normalized,
        list(REWRITE_FIELDS),
    )


def export_annotators() -> None:
    for index in range(1, 4):
        source_path = HUMAN / f"annotator_{index}.csv"
        if not source_path.exists():
            raise FileNotFoundError("请先运行 make_human_validation_packet.py --compile")
        source = read_csv(source_path)
        rows = [
            {ANNOTATION_FIELDS[key]: row.get(key, "") for key in ANNOTATION_FIELDS}
            for row in source
        ]
        write_csv(
            HUMAN / f"02_标注者{index}填写表_中文列名.csv",
            rows,
            list(ANNOTATION_FIELDS.values()),
        )


def import_annotators() -> None:
    reverse = {value: key for key, value in ANNOTATION_FIELDS.items()}
    for index in range(1, 4):
        path = HUMAN / f"02_标注者{index}填写表_中文列名.csv"
        rows = read_csv(path)
        normalized = [{reverse[key]: value for key, value in row.items()} for row in rows]
        missing = [row["item_id"] for row in normalized if not row["response"].strip()]
        if len(normalized) != 100 or missing:
            raise ValueError(
                f"标注者{index}应完成100题；当前{len(normalized)}题，缺少{len(missing)}个答案。"
            )
        write_csv(HUMAN / f"annotator_{index}.csv", normalized, list(ANNOTATION_FIELDS))


def export_pilot() -> None:
    with (HUMAN / "selected_sources.jsonl").open(encoding="utf-8") as handle:
        sources = [json.loads(line) for line in handle if line.strip()]
    fields = [
        "题号", "中文任务指令", "初始状态（中文）", "刷新后状态（中文）", "动作前置条件（中文）",
        "候选答案", "你的答案（ID/REJECT/CLARIFY）", "信心1到5（可选）", "备注（可选）",
        "英文原文（仅供核对）",
    ]

    def zh_value(value: Any) -> str:
        return str(DISPLAY_ZH.get(value, VALUE_ZH.get(value, value)))

    def zh_entity(entity: dict[str, Any], number: int) -> str:
        details = "；".join(
            f"{FIELD_ZH.get(key, key)}={zh_value(value)}" for key, value in entity.items()
        )
        return f"对象{number}：{details}"

    def zh_state(state: list[dict[str, Any]]) -> str:
        return "\n".join(zh_entity(entity, index) for index, entity in enumerate(state, 1))

    def zh_schema(schema: dict[str, Any]) -> str:
        conditions = schema.get("preconditions", schema)
        return "；".join(
            f"{FIELD_ZH.get(key, key)}={zh_value(value)}" for key, value in conditions.items()
        )

    rows = []
    for number, row in enumerate(sources[::5], 1):
        instruction = row["instruction"]
        if instruction not in PILOT_TRANSLATIONS:
            raise KeyError(f"缺少试填题中文翻译：{instruction}")
        rows.append({
            "题号": f"PILOT-{number:02d}",
            "中文任务指令": PILOT_TRANSLATIONS[instruction],
            "初始状态（中文）": zh_state(row["initial_state"]),
            "刷新后状态（中文）": zh_state(row["refreshed_state"]),
            "动作前置条件（中文）": zh_schema(row.get("action_schema", {})),
            "候选答案": " | ".join(entity["id"] for entity in row["refreshed_state"]) + " | REJECT | CLARIFY",
            "你的答案（ID/REJECT/CLARIFY）": "",
            "信心1到5（可选）": "",
            "备注（可选）": "仅用于测试流程，不进入论文统计",
            "英文原文（仅供核对）": instruction,
        })
    write_csv(PILOT_FORM, rows, fields)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--import-rewrites", action="store_true")
    group.add_argument("--export-annotators", action="store_true")
    group.add_argument("--import-annotators", action="store_true")
    args = parser.parse_args()
    if args.import_rewrites:
        import_rewrites()
    elif args.export_annotators:
        export_annotators()
    elif args.import_annotators:
        import_annotators()
    else:
        export_rewrites()
        export_pilot()
    print("human_validation 中文表单处理完成")


if __name__ == "__main__":
    main()
