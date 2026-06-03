from __future__ import annotations

import random
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from studio_shell.page_shell import page_shell
from studio_shell.shell_ui import format_extra_context, inject_style


st.set_page_config(page_title="我要寄件", page_icon="📝", layout="wide")
inject_style()

COMPANIES = ["黑貓宅急便", "7-ELEVEN 交貨便", "新竹物流"]
DELIVERY_TYPES = ["一般寄件", "快速寄件", "冷藏寄件"]
PAYMENT_METHODS = ["信用卡", "7-11 ibon 繳費"]
COUNTRY_CODES = [
    "🇹🇼 台灣 (+886)",
    "🇯🇵 日本 (+81)",
    "🇰🇷 韓國 (+82)",
    "🇨🇳 中國 (+86)",
    "🇭🇰 香港 (+852)",
    "🇸🇬 新加坡 (+65)",
    "🇺🇸 美國 (+1)",
    "🇬🇧 英國 (+44)",
    "🇫🇷 法國 (+33)",
    "🇩🇪 德國 (+49)",
]


def _generate_pin() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(6))


def render_main() -> str:
    if "shipping_submitted" not in st.session_state:
        st.session_state.shipping_submitted = False
    if "shipping_pin" not in st.session_state:
        st.session_state.shipping_pin = ""

    st.markdown("#### 我要寄件")

    name_col1, name_col2 = st.columns(2)
    with name_col1:
        sender = st.text_input("寄件人姓名", key="shipping_sender")
    with name_col2:
        receiver = st.text_input("收件人姓名", key="shipping_receiver")

    phone_col1, phone_col2 = st.columns([2, 3])
    with phone_col1:
        country_code = st.selectbox("國家 / 區碼", COUNTRY_CODES, key="shipping_country_code")
    with phone_col2:
        phone = st.text_input("電話", key="shipping_phone", placeholder="例如：0912345678")
    address = st.text_area("收件地址", key="shipping_address", placeholder="請輸入完整地址")
    item_note = st.text_area("寄件內容", key="shipping_item_note", placeholder="例如：衣物、書籍、生活用品")
    remark = st.text_area("備註", key="shipping_remark", placeholder="有其他需求可填在這裡")

    company = st.selectbox("寄件公司", COMPANIES, key="shipping_company")
    delivery_type = st.radio("配送方式", DELIVERY_TYPES, horizontal=True, key="shipping_delivery_type")
    payment_method = st.radio("付款方式", PAYMENT_METHODS, horizontal=True, key="shipping_payment_method")

    col1, col2, col3 = st.columns(3)
    with col1:
        quantity = st.number_input("件數", min_value=1, value=1, key="shipping_quantity")
    with col2:
        weight = st.number_input("重量（kg）", min_value=1, value=1, key="shipping_weight")
    with col3:
        amount = st.number_input("金額", min_value=0, value=120, key="shipping_amount")

    need_receipt = st.checkbox("需要收據", key="shipping_need_receipt")
    agree_terms = st.checkbox("我同意寄件條款", key="shipping_agree_terms")

    if payment_method == "信用卡":
        st.markdown("#### 信用卡付款資訊")
        card_col1, card_col2 = st.columns(2)
        with card_col1:
            card_no = st.text_input("信用卡號", key="shipping_card_no")
            card_name = st.text_input("持卡人姓名", key="shipping_card_name")
        with card_col2:
            card_expiry = st.text_input("有效期限", placeholder="MM/YY", key="shipping_card_expiry")
        payment_info = {
            "付款方式": payment_method,
            "信用卡號": card_no or "（未填）",
            "持卡人姓名": card_name or "（未填）",
            "有效期限": card_expiry or "（未填）",
            "付款結果": "待確認寄件後模擬付款",
        }
    else:
        st.markdown("#### ibon 繳費說明")
        st.info("確認寄件後，系統會產生 PIN 碼。你可到 7-11 ibon 輸入 PIN 碼、完成繳費並列印寄件資訊。")
        payment_info = {
            "付款方式": payment_method,
            "付款地點": "7-11 ibon",
            "付款結果": "待確認寄件後產生 PIN 碼",
        }

    if st.button("確認寄件", use_container_width=True, key="shipping_submit"):
        if not agree_terms:
            st.warning("請先勾選同意寄件條款。")
        else:
            st.session_state.shipping_submitted = True
            st.session_state.shipping_pin = _generate_pin()
            st.rerun()

    st.divider()
    st.markdown("#### 寄件摘要")
    summary = {
        "寄件人姓名": sender or "（未填）",
        "收件人姓名": receiver or "（未填）",
        "國家 / 區碼": country_code,
        "電話": phone or "（未填）",
        "收件地址": address or "（未填）",
        "寄件內容": item_note or "（未填）",
        "備註": remark or "（未填）",
        "寄件公司": company,
        "配送方式": delivery_type,
        "付款方式": payment_method,
        "件數": quantity,
        "重量（kg）": weight,
        "金額": amount,
        "需要收據": "是" if need_receipt else "否",
        "是否同意條款": "是" if agree_terms else "否",
    }
    st.json(summary)

    st.markdown("#### 付款資訊")
    st.json(payment_info)

    st.markdown("#### PIN 碼")
    if st.session_state.shipping_submitted:
        st.code(f"PIN: {st.session_state.shipping_pin}", language="text")
        st.success("請帶著貨件到寄件公司機台，輸入 PIN 碼列印寄件資料。")
    else:
        st.caption("尚未產生 PIN 碼，請先按「確認寄件」。")

    extra = format_extra_context(
        "我要寄件",
        寄件人姓名=sender or "（未填）",
        收件人姓名=receiver or "（未填）",
        國家區碼=country_code,
        電話=phone or "（未填）",
        寄件公司=company,
        配送方式=delivery_type,
        付款方式=payment_method,
        件數=quantity,
        重量=f"{weight} kg",
        金額=amount,
        是否已送出="是" if st.session_state.shipping_submitted else "否",
        PIN碼=st.session_state.shipping_pin or "（尚未產生）",
    )

    st.markdown("#### 給 Agent 的摘要")
    st.code(extra, language="text")
    return extra


page_shell(
    "我要寄件",
    "線上填寫寄件資料、選付款方式並產生 PIN 碼。",
    render_main,
    page_name="我要寄件",
)
