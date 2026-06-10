from __future__ import annotations

import random
import sys
from pathlib import Path

import streamlit as st

try:
    import folium
    from geopy.exc import GeocoderServiceError, GeocoderTimedOut
    from geopy.geocoders import Nominatim
    from streamlit_folium import st_folium
except ImportError:
    folium = None
    GeocoderServiceError = Exception
    GeocoderTimedOut = Exception
    Nominatim = None
    st_folium = None

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

DELIVERY_OPTIONS = {
    "一般寄件": 0,
    "快速寄件": 80,
    "冷藏寄件": 120,
}

SHIPPING_RATE_TABLES = {
    "黑貓宅急便": {
        "source": "黑貓宅急便官方運費說明：本島互寄，尺寸為長+寬+高，單件20kg以內。",
        "source_url": "https://www.t-cat.com.tw/inquire/timesheet3.aspx",
        "max_weight": 20.0,
        "rows": [
            {"size": "60公分以下", "max_sum": 60, "一般寄件": 130, "快速寄件": 130, "冷藏寄件": 160},
            {"size": "61-90公分", "max_sum": 90, "一般寄件": 170, "快速寄件": 170, "冷藏寄件": 225},
            {"size": "91-120公分", "max_sum": 120, "一般寄件": 210, "快速寄件": 210, "冷藏寄件": 290},
            {"size": "121-150公分", "max_sum": 150, "一般寄件": 250, "快速寄件": 250, "冷藏寄件": None},
        ],
        "notes": [
            "一般寄件依常溫宅急便本島互寄計價。",
            "冷藏寄件依低溫宅急便本島互寄計價，低溫包裹尺寸上限120公分。",
            "官方運費表未另列快速寄件費率，系統暫按常溫宅急便費率計價。",
        ],
    },
    "7-ELEVEN 交貨便": {
        "source": "7-ELEVEN官方服務內容及價格：一般材積長+寬+高105cm內、重量10kg內；120cm材積需專用箱。",
        "source_url": "https://www.7-11.com.tw/service/accept.aspx",
        "max_weight": 10.0,
        "rows": [
            {"size": "105公分以下", "max_sum": 105, "一般寄件": 60, "快速寄件": 60, "冷藏寄件": None},
            {"size": "120cm專用箱", "max_sum": 120, "一般寄件": 125, "快速寄件": 125, "冷藏寄件": None},
        ],
        "notes": [
            "一般交貨便本島服務價格60元。",
            "交貨便120cm寄件目前以官方公告優惠價125元計。",
            "此頁的冷藏寄件未串接7-ELEVEN冷凍交貨便專用流程，暫不開放計價。",
        ],
    },
    "新竹物流": {
        "source": "新竹物流官方才積/運費計算說明：依體積才積與實際重量取較大值，實際優惠運價以營業單位報價為準。",
        "source_url": "https://www.hct.com.tw/Allocation/allocation_volume.aspx",
        "max_weight": 20.0,
        "rows": [
            {"size": "60公分以下", "max_sum": 60, "一般寄件": 120, "快速寄件": 160, "冷藏寄件": 180},
            {"size": "61-90公分", "max_sum": 90, "一般寄件": 160, "快速寄件": 200, "冷藏寄件": 240},
            {"size": "91-120公分", "max_sum": 120, "一般寄件": 200, "快速寄件": 240, "冷藏寄件": 300},
            {"size": "121-150公分", "max_sum": 150, "一般寄件": 240, "快速寄件": 280, "冷藏寄件": 360},
        ],
        "notes": [
            "新竹物流官網目前以才積/重量計算與營業所報價為準，這裡先用常見級距估算。",
            "若要做正式收款，建議再串接新竹物流契約報價或後台費率表。",
        ],
    },
}

COMPANY_OPTIONS = {company: 0 for company in SHIPPING_RATE_TABLES}

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
    length: int,
    width: int,
    height: int,
) -> tuple[int, dict[str, int | str]]:
    size_sum = length + width + height
    rate_row = _select_rate_row(company, delivery_type, size_sum)
    shipping_fee = 0 if rate_row is None else rate_row[delivery_type]
    total = shipping_fee * quantity
    details = {
        "基本運費": shipping_fee,
        "物流公司調整": 0,
        "配送方式加價": 0,
        "超重公斤數": 0,
        "超重費用": 0,
        "尺寸合計": size_sum,
        "計費級距": "無可用級距" if rate_row is None else rate_row["size"],
        "單件費用": shipping_fee,
        "總金額": total,
    }
    return total, details


def _select_rate_row(company: str, delivery_type: str, size_sum: int) -> dict[str, int | str | None] | None:
    for row in SHIPPING_RATE_TABLES[company]["rows"]:
        if size_sum <= row["max_sum"] and row.get(delivery_type) is not None:
            return row
    return None


def _format_fee(value: int | None) -> str:
    return "暫無提供" if value is None else f"NT$ {value}"


def _render_shipping_rate_table(company: str) -> None:
    rate_table = SHIPPING_RATE_TABLES[company]
    rows = [
        {
            "尺寸級距": row["size"],
            "一般寄件": _format_fee(row["一般寄件"]),
            "快速寄件": _format_fee(row["快速寄件"]),
            "冷藏寄件": _format_fee(row["冷藏寄件"]),
        }
        for row in rate_table["rows"]
    ]
    st.markdown(f"#### {company} 收費標準")
    st.caption(rate_table["source"])
    st.caption(f"來源：{rate_table['source_url']}")
    st.table(rows)
    for note in rate_table["notes"]:
        st.caption(f"• {note}")


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def _geocode_address(address: str) -> tuple[float, float, str] | None:
    if Nominatim is None:
        return None

    query = address.strip()
    if not query:
        return None
    if "台灣" not in query and "臺灣" not in query:
        query = f"{query}, 台灣"

    geolocator = Nominatim(user_agent="al_report_shipping_map")
    try:
        location = geolocator.geocode(
            query,
            language="zh-TW",
            timeout=8,
        )
    except (GeocoderServiceError, GeocoderTimedOut, TimeoutError):
        return None

    if location is None:
        return None
    return location.latitude, location.longitude, location.address


def _render_address_map(address: str) -> tuple[float, float, str] | None:
    st.markdown("#### 收件地址地圖")

    if folium is None or st_folium is None or Nominatim is None:
        st.info("地圖套件尚未安裝，請先安裝 folium、streamlit-folium、geopy。")
        return None

    if not address.strip():
        st.caption("輸入收件地址後，這裡會自動轉成經緯度並顯示地圖。")
        return None

    with st.spinner("正在定位收件地址..."):
        location = _geocode_address(address)

    if location is None:
        st.warning("找不到這個地址，請輸入更完整的台灣地址，例如：台北市中正區北平西路3號。")
        return None

    lat, lon, display_name = location
    st.caption(f"定位結果：{display_name}")
    st.caption(f"經緯度：{lat:.6f}, {lon:.6f}")

    map_view = folium.Map(location=[lat, lon], zoom_start=16, tiles="OpenStreetMap")
    folium.Marker(
        [lat, lon],
        tooltip="收件地址",
        popup=address,
        icon=folium.Icon(color="red", icon="home"),
    ).add_to(map_view)

    st_folium(map_view, height=380, use_container_width=True)
    return location


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
    map_location = _render_address_map(address)
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

    st.caption(f"{package_type}限制：單件最高 {rule['max_weight']} kg。")
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

    carrier_max_weight = SHIPPING_RATE_TABLES[company]["max_weight"]
    size_sum = length + width + height
    selected_rate_row = _select_rate_row(company, delivery_type, size_sum)
    overweight = weight > rule["max_weight"] or weight > carrier_max_weight
    oversize = length > max_length or width > max_width or height > max_height
    unavailable_rate = selected_rate_row is None

    if overweight:
        st.warning(
            f"單件重量超過限制：{package_type} 最高 {rule['max_weight']} kg，"
            f"{company} 最高 {carrier_max_weight:g} kg。"
        )
    if oversize:
        st.warning("包裹尺寸超過此貨物類型限制，請更換貨物類型或調整尺寸。")
    if unavailable_rate:
        st.warning(f"{company} 的 {delivery_type} 暫無支援尺寸合計 {size_sum} cm 的收費級距。")

    _render_shipping_rate_table(company)

    total_amount, price_details = _calculate_price(
        company,
        delivery_type,
        package_type,
        int(quantity),
        float(weight),
        int(length),
        int(width),
        int(height),
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

    can_continue = not missing_fields and not overweight and not oversize and not unavailable_rate

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
                if overweight or oversize or unavailable_rate:
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

    masked_card_no = "（未填）"
    if card_no:
        masked_card_no = "*" * max(0, len(card_no) - 4) + card_no[-4:]

    payment_detail_lines = [
        f"付款方式：{payment}",
        f"需要收據：{'是' if need_receipt else '否'}",
        f"同意條款：{'是' if agree_terms else '否'}",
    ]
    if payment == "信用卡":
        payment_detail_lines.extend(
            [
                f"持卡人：{card_name or '（未填）'}",
                f"卡號：{masked_card_no}",
                f"有效期：{card_expiry or '（未填）'}",
            ]
        )
    elif payment == "7-11 ibon 繳費":
        payment_detail_lines.append("繳費地點：7-11 ibon")

    shipment_no = f"KY{random.randint(10000000, 99999999)}"
    order_date = "2026-06-10"
    payment_label = "已確認" if st.session_state.send_payment_step else "待付款"
    submit_label = "已建單" if st.session_state.send_package_confirmed else "資料暫存"
    map_status = "尚未定位"
    if map_location is not None:
        map_status = f"{map_location[0]:.6f}, {map_location[1]:.6f}"

    receipt_text = "\n".join(
        [
            "========================================",
            "         黑貓宅急便  託運單預覽",
            "========================================",
            f"託運單號：{shipment_no}",
            f"寄件日期：{order_date}",
            f"託運狀態：{submit_label}",
            "----------------------------------------",
            "【寄件資訊】",
            f"寄件人姓名：{sender_name or '（未填）'}",
            f"聯絡電話　：{country_code} {phone or '（未填）'}",
            "",
            "【收件資訊】",
            f"收件人姓名：{receiver_name or '（未填）'}",
            f"收件地址　：{address or '（未填）'}",
            f"地圖定位　：{map_status}",
            "----------------------------------------",
            "【配送資料】",
            f"物流公司　：{company}",
            f"配送方式　：{delivery_type}",
            f"貨物類型　：{package_type}",
            f"寄件內容　：{package_content or '（未填）'}",
            f"備註說明　：{note or '（未填）'}",
            "----------------------------------------",
            "【包裹規格】",
            f"件　　數　：{quantity}",
            f"單件重量　：{weight} kg",
            f"包裹尺寸　：{length} x {width} x {height} cm",
            f"尺寸合計　：{price_details['尺寸合計']} cm",
            f"重量上限　：{min(rule['max_weight'], carrier_max_weight):g} kg",
            f"尺寸上限　：{max_length} x {max_width} x {max_height} cm",
            f"計費級距　：{price_details['計費級距']}",
            "----------------------------------------",
            "【費用明細】",
            f"物流運費　：NT$ {price_details['基本運費']}",
            f"單件費用　：NT$ {price_details['單件費用']}",
            f"總金額　　：NT$ {total_amount}",
            "----------------------------------------",
            "【付款資訊】",
            f"付款方式　：{payment}",
            f"付款狀態　：{payment_label}",
            f"需要收據　：{'是' if need_receipt else '否'}",
            f"條款確認　：{'已同意' if agree_terms else '未同意'}",
            *(f"{line}" for line in payment_detail_lines[3:]),
            f"PIN 繳費碼：{st.session_state.send_package_pin or '（尚未產生）'}",
            "========================================",
            "此畫面為託運單預覽，實際列印內容依物流系統為準",
            "========================================",
        ]
    )

    st.code(receipt_text, language="text")

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
        收件地址=address or "（未填）",
        地圖定位=map_status,
        物流公司=company,
        配送方式=delivery_type,
        貨物類型=package_type,
        件數=quantity,
        單件重量=f"{weight} kg",
        尺寸=f"{length} x {width} x {height} cm",
        尺寸合計=f"{price_details['尺寸合計']} cm",
        重量限制=f"{min(rule['max_weight'], carrier_max_weight):g} kg",
        尺寸限制=f"{max_length} x {max_width} x {max_height} cm",
        計費級距=price_details["計費級距"],
        總金額=f"NT$ {total_amount}",
        付款方式=payment,
        是否進入付款="是" if st.session_state.send_payment_step else "否",
        是否已送出="是" if st.session_state.send_package_confirmed else "否",
        PIN碼=st.session_state.send_package_pin or "（尚未產生）",
    )

    return extra


page_shell(
    "我要寄件",
    "填寫寄件資料，確認包裹資訊後再進入付款。",
    render_main,
    page_name="我要寄件",
)
