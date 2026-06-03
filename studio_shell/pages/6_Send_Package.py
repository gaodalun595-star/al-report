from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from studio_shell.page_shell import page_shell
from studio_shell.shell_ui import format_extra_context, inject_style


st.set_page_config(page_title="我要寄件", page_icon="📦", layout="wide")
inject_style()

COUNTRY_CODES = [
    "台灣 +886",
    "日本 +81",
    "韓國 +82",
    "中國 +86",
    "香港 +852",
    "新加坡 +65",
    "美國/加拿大 +1",
    "英國 +44",
    "法國 +33",
    "德國 +49",
]

COMPANY_OPTIONS = {
    "黑貓宅急便": 0,
    "7-ELEVEN 交貨便": -10,
    "新竹物流": 20,
}

DELIVERY_OPTIONS = {
    "一般寄件": 0,
    "快速寄件": 80,
    "冷藏寄件": 120,
}

PACKAGE_RULES = {
    "文件": {
        "base_price": 70,
        "included_weight": 1.0,
        "max_weight": 2.0,
        "extra_per_kg": 30,
        "max_size": (35, 25, 2),
    },
    "一般包裹": {
        "base_price": 120,
        "included_weight": 5.0,
        "max_weight": 20.0,
        "extra_per_kg": 45,
        "max_size": (60, 45, 45),
    },
    "易碎物": {
        "base_price": 180,
        "included_weight": 3.0,
        "max_weight": 10.0,
        "extra_per_kg": 60,
        "max_size": (50, 40, 40),
    },
    "冷藏食品": {
        "base_price": 220,
        "included_weight": 3.0,
        "max_weight": 10.0,
        "extra_per_kg": 70,
        "max_size": (45, 35, 35),
    },
    "大型包裹": {
        "base_price": 280,
        "included_weight": 10.0,
        "max_weight": 30.0,
        "extra_per_kg": 55,
        "max_size": (100, 60, 60),
    },
}

PAYMENT_OPTIONS = ["信用卡", "7-11 ibon 繳費"]


def _generate_pin() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(6))


def _calculate_price(
    company: str,
    delivery_type: str,
    package_type: str,
    quantity: int,
    weight: float,
) -> tuple[int, dict[str, int]]:
    rule = PACKAGE_RULES[package_type]
    overweight_kg = max(0, math.ceil(weight - rule["included_weight"]))
    subtotal = (
        rule["base_price"]
        + COMPANY_OPTIONS[company]
        + DELIVERY_OPTIONS[delivery_type]
        + overweight_kg * rule["extra_per_kg"]
    )
    total = max(0, subtotal) * quantity
    details = {
        "基本運費": rule["base_price"],
        "物流公司調整": COMPANY_OPTIONS[company],
        "配送方式加價": DELIVERY_OPTIONS[delivery_type],
        "超重公斤數": overweight_kg,
        "超重費用": overweight_kg * rule["extra_per_kg"],
        "單件費用": max(0, subtotal),
        "總金額": total,
    }
    return total, details


def render_main() -> str:
    if "send_package_confirmed" not in st.session_state:
        st.session_state.send_package_confirmed = False
    if "send_package_pin" not in st.session_state:
        st.session_state.send_package_pin = ""
    if "send_payment_step" not in st.session_state:
        st.session_state.send_payment_step = False

    st.markdown("#### 寄件資料")

    name_col1, name_col2 = st.columns(2)
    with name_col1:
        sender_name = st.text_input("寄件人姓名", key="send_sender_name")
    with name_col2:
        receiver_name = st.text_input("收件人姓名", key="send_receiver_name")

    phone_col1, phone_col2 = st.columns([2, 3])
    with phone_col1:
        country_code = st.selectbox("電話國碼", COUNTRY_CODES, key="send_country_code")
    with phone_col2:
        phone = st.text_input("電話", key="send_phone", placeholder="例如：912345678")

    address = st.text_area("收件地址", key="send_address", placeholder="請輸入完整地址")
    package_content = st.text_area("寄件內容", key="send_content", placeholder="例如：書籍、衣物、食品")
    note = st.text_area("備註", key="send_note", placeholder="有特殊需求可以填在這裡")

    st.divider()
    st.markdown("#### 包裹資訊")

    select_col1, select_col2, select_col3 = st.columns(3)
    with select_col1:
        company = st.selectbox("物流公司", list(COMPANY_OPTIONS), key="send_company")
    with select_col2:
        delivery_type = st.selectbox("配送方式", list(DELIVERY_OPTIONS), key="send_delivery_type")
    with select_col3:
        package_type = st.selectbox("貨物類型", list(PACKAGE_RULES), key="send_package_type")

    rule = PACKAGE_RULES[package_type]
    max_length, max_width, max_height = rule["max_size"]

    st.caption(
        f"{package_type}限制：單件最高 {rule['max_weight']} kg，"
        f"基本重量 {rule['included_weight']} kg，"
        f"超重每 1 kg 加收 NT$ {rule['extra_per_kg']}。"
    )
    st.caption(
        f"尺寸限制：長 {max_length} cm、寬 {max_width} cm、高 {max_height} cm 以內。"
    )

    qty_col, weight_col = st.columns(2)
    with qty_col:
        quantity = st.number_input("件數", min_value=1, value=1, step=1, key="send_quantity")
    with weight_col:
        weight = st.number_input(
            "單件重量（kg）",
            min_value=0.1,
            value=1.0,
            step=0.1,
            key="send_weight",
        )

    size_col1, size_col2, size_col3 = st.columns(3)
    with size_col1:
        length = st.number_input("長（cm）", min_value=1, value=30, step=1, key="send_length")
    with size_col2:
        width = st.number_input("寬（cm）", min_value=1, value=20, step=1, key="send_width")
    with size_col3:
        height = st.number_input("高（cm）", min_value=1, value=10, step=1, key="send_height")

    overweight = weight > rule["max_weight"]
    oversize = length > max_length or width > max_width or height > max_height

    if overweight:
        st.warning(f"單件重量超過 {package_type} 的限制 {rule['max_weight']} kg。")
    if oversize:
        st.warning("包裹尺寸超過此貨物類型限制，請更換貨物類型或調整尺寸。")

    total_amount, price_details = _calculate_price(
        company,
        delivery_type,
        package_type,
        int(quantity),
        float(weight),
    )

    st.markdown("#### 運費試算結果")
    price_col1, price_col2 = st.columns(2)
    price_col1.metric("總金額", f"NT$ {total_amount}")
    price_col2.metric("單件費用", f"NT$ {price_details['單件費用']}")
    st.json(price_details)

    need_receipt = st.checkbox("需要收據", key="send_receipt")
    agree_terms = st.checkbox("我同意寄件條款", key="send_agree")

    missing_fields = []
    if not sender_name.strip():
        missing_fields.append("寄件人姓名")
    if not receiver_name.strip():
        missing_fields.append("收件人姓名")
    if not phone.strip():
        missing_fields.append("電話")
    if not address.strip():
        missing_fields.append("收件地址")
    if not package_content.strip():
        missing_fields.append("寄件內容")

    can_continue = not missing_fields and not overweight and not oversize

    continue_col, edit_col = st.columns([2, 1])
    with continue_col:
        if st.button("繼續付款", use_container_width=True, key="send_continue_payment"):
            if can_continue:
                st.session_state.send_payment_step = True
                st.rerun()
            else:
                st.session_state.send_payment_step = False
                if missing_fields:
                    st.warning("請先填完：" + "、".join(missing_fields))
                if overweight or oversize:
                    st.warning("請先確認重量與尺寸符合限制。")
    with edit_col:
        if st.session_state.send_payment_step and st.button(
            "返回修改",
            use_container_width=True,
            key="send_back_to_package",
        ):
            st.session_state.send_payment_step = False
            st.rerun()

    st.divider()
    st.markdown("#### 付款資訊")

    payment = "尚未進入付款"
    card_no = ""
    card_name = ""
    card_expiry = ""

    if st.session_state.send_payment_step:
        payment = st.selectbox("付款方式", PAYMENT_OPTIONS, key="send_payment")
        if payment == "信用卡":
            card_col1, card_col2 = st.columns(2)
            with card_col1:
                card_name = st.text_input("持卡人姓名", key="send_card_name")
                card_no = st.text_input("信用卡號", key="send_card_no")
            with card_col2:
                card_expiry = st.text_input("有效期限", placeholder="MM/YY", key="send_card_expiry")
                st.text_input("安全碼", type="password", key="send_card_cvv")
        else:
            st.info("送出後會產生 PIN 碼，可到 7-11 ibon 繳費並列印寄件資料。")

        if st.button("確認寄件", use_container_width=True, key="send_confirm"):
            if not agree_terms:
                st.warning("請先勾選同意寄件條款。")
            else:
                st.session_state.send_package_confirmed = True
                st.session_state.send_package_pin = _generate_pin()
                st.rerun()
    else:
        st.info("包裹資訊確認後，按上方「繼續付款」即可填寫付款資訊。")

    st.divider()
    st.markdown("#### 寄件摘要")
    summary = {
        "寄件人姓名": sender_name or "（未填）",
        "收件人姓名": receiver_name or "（未填）",
        "電話國碼": country_code,
        "電話": phone or "（未填）",
        "收件地址": address or "（未填）",
        "寄件內容": package_content or "（未填）",
        "備註": note or "（未填）",
        "物流公司": company,
        "配送方式": delivery_type,
        "貨物類型": package_type,
        "件數": quantity,
        "單件重量": f"{weight} kg",
        "尺寸": f"{length} x {width} x {height} cm",
        "重量限制": f"{rule['max_weight']} kg",
        "尺寸限制": f"{max_length} x {max_width} x {max_height} cm",
        "超重每公斤": f"NT$ {rule['extra_per_kg']}",
        "總金額": f"NT$ {total_amount}",
        "付款方式": payment,
        "需要收據": "是" if need_receipt else "否",
        "是否同意條款": "是" if agree_terms else "否",
    }

    if payment == "信用卡":
        summary.update(
            {
                "持卡人姓名": card_name or "（未填）",
                "信用卡號": card_no or "（未填）",
                "有效期限": card_expiry or "（未填）",
            }
        )

    st.json(summary)

    if st.session_state.send_package_confirmed:
        st.success(f"寄件資料已送出，PIN 碼：{st.session_state.send_package_pin}")
        if payment == "7-11 ibon 繳費":
            st.code(
                f"請到 7-11 ibon 輸入 PIN：{st.session_state.send_package_pin}",
                language="text",
            )

    extra = format_extra_context(
        "我要寄件",
        寄件人姓名=sender_name or "（未填）",
        收件人姓名=receiver_name or "（未填）",
        電話=f"{country_code} {phone or '（未填）'}",
        物流公司=company,
        配送方式=delivery_type,
        貨物類型=package_type,
        件數=quantity,
        單件重量=f"{weight} kg",
        尺寸=f"{length} x {width} x {height} cm",
        重量限制=f"{rule['max_weight']} kg",
        尺寸限制=f"{max_length} x {max_width} x {max_height} cm",
        超重費=f"每 1 kg NT$ {rule['extra_per_kg']}",
        總金額=f"NT$ {total_amount}",
        付款方式=payment,
        是否進入付款="是" if st.session_state.send_payment_step else "否",
        是否已送出="是" if st.session_state.send_package_confirmed else "否",
        PIN碼=st.session_state.send_package_pin or "（尚未產生）",
    )

    st.markdown("#### 給 Agent 的摘要")
    st.code(extra, language="text")
    return extra


page_shell(
    "我要寄件",
    "填寫寄件資料，確認包裹資訊後再進入付款。",
    render_main,
    page_name="我要寄件",
)
