import streamlit as st
import qrcode
from io import BytesIO
import base64
import urllib.parse

st.set_page_config(page_title="📱 문자 보내기", page_icon="📱", layout="centered")

st.title("📱 문자 보내기 (Streamlit 버전) 📱")

# -----------------------------
# 입력 영역 (PC 화면일 때만 보임)
# -----------------------------
if "p" not in st.query_params and "m" not in st.query_params:
    st.subheader("핸드폰 번호 입력")
    phones_text = st.text_area(
        "번호를 줄바꿈으로 입력하세요",
        height=140,
        placeholder="01012345678\n01098765432"
    )

    st.subheader("문자 내용")
    msg_text = st.text_area(
        "여러 줄 입력 가능",
        height=200,
        placeholder="문자를 입력하세요."
    )

    if st.button("QR 코드 생성"):
        phones = [v.strip() for v in phones_text.split("\n") if v.strip()]
        if len(phones) == 0:
            st.error("번호를 1개 이상 입력하세요.")
            st.stop()
        if not msg_text.strip():
            st.error("문자 내용을 입력하세요.")
            st.stop()

        # Base64 인코딩
        encoded_msg = base64.b64encode(msg_text.encode("utf-8")).decode()

        p_param = urllib.parse.quote(",".join(phones))
        m_param = urllib.parse.quote(encoded_msg)

        # Streamlit 공유 URL 구성
        final_url = f"https://sorinng.github.io/sms/?p={p_param}&m={m_param}"

        st.subheader("📲 QR 코드")
        qr = qrcode.make(final_url)
        buf = BytesIO()
        qr.save(buf)
        st.image(buf.getvalue(), width=260)

        st.write("아래 주소를 복사해서 사용할 수도 있어요:")
        st.code(final_url)

# -----------------------------
# QR로 접속 시(모바일)
# -----------------------------
else:
    st.subheader("📨 문자 보내기 버튼")

    p = st.query_params.get("p", [""])[0]
    m = st.query_params.get("m", [""])[0]

    # 파라미터 디코딩
    phones = urllib.parse.unquote(p).split(",")
    decoded_msg = base64.b64decode(urllib.parse.unquote(m)).decode("utf-8")

    # 전체 보내기 버튼
    st.write(f"### 📢 전체에게 보내기 ({len(phones)}명)")

    isiPhone = "iphone" in st.request.headers["User-Agent"].lower()

    if isiPhone:
        sms_url = f"sms:/open?addresses={','.join(phones)}&body={urllib.parse.quote(decoded_msg)}"
    else:
        sms_url = f"sms:{','.join(phones)}?body={urllib.parse.quote(decoded_msg)}"

    st.markdown(
        f"""<a href="{sms_url}" style="
            display:block;
            background:#88BFFF;
            padding:20px;
            border-radius:15px;
            text-align:center;
            font-size:28px;
            color:white;
            text-decoration:none;
            font-weight:700;
        ">📢 전체에게 메시지 보내기</a>""",
        unsafe_allow_html=True
    )

    st.write("---")

    # 개별 버튼 생성
    st.write("### 📱 개별 문자 보내기")

    for i, pnum in enumerate(phones):
        sms_url = f"sms:{pnum}?body={urllib.parse.quote(decoded_msg)}"

        st.markdown(
            f"""<a href="{sms_url}" style="
                display:block;
                background:#C9B6E4;
                padding:20px;
                border-radius:15px;
                text-align:center;
                font-size:28px;
                color:white;
                text-decoration:none;
                font-weight:700;
                margin-bottom:18px;
            ">📨 [{i+1}] {pnum}</a>""",
            unsafe_allow_html=True
        )
