import streamlit as st
import qrcode
from io import BytesIO
import base64
from urllib.parse import quote

# 페이지 설정
st.set_page_config(
    page_title="📱 문자 보내기 📱",
    page_icon="📱",
    layout="centered"
)

# CSS 스타일링
st.markdown("""
<style>
    .main {
        background-color: #f4f4f4;
    }
    .stTextArea textarea {
        font-size: 18px;
    }
    .big-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: 800;
        margin-bottom: 30px;
    }
    .count-text {
        text-align: center;
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 10px;
    }
    div[data-testid="stButton"] button {
        width: 100%;
        background-color: #C9B6E4;
        color: white;
        font-size: 20px;
        font-weight: 700;
        padding: 15px;
        border-radius: 14px;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #B39CD0;
    }
</style>
""", unsafe_allow_html=True)

# Base64 인코딩/디코딩 함수
def encode_base64(text):
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def decode_base64(text):
    return base64.b64decode(text.encode('utf-8')).decode('utf-8')

# QR 코드 생성 함수
def generate_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# URL 파라미터 확인
query_params = st.query_params

# 제목
st.markdown('<div class="big-title">📱 문자 보내기 📱</div>', unsafe_allow_html=True)

# QR 접속 모드 (파라미터가 있을 때)
if 'p' in query_params and 'm' in query_params:
    try:
        phones_param = query_params['p']
        msg_param = query_params['m']
        
        phones = phones_param.split(',')
        decoded_msg = decode_base64(msg_param)
        
        st.markdown("### 📨 문자 보내기")
        st.info(f"**수신자:** {len(phones)}명")
        st.text_area("**문자 내용:**", decoded_msg, height=150, disabled=True)
        
        st.markdown("---")
        
        # 전체 보내기 버튼
        st.markdown(f"""
        <div style="background:#A8D5FE; color:#003B73; padding:30px; border-radius:20px; text-align:center; font-size:24px; font-weight:800; margin-bottom:30px;">
            📢 전체에게 문자 보내기 ({len(phones)}명)
        </div>
        """, unsafe_allow_html=True)
        
        all_numbers = ",".join(phones)
        encoded_msg = quote(decoded_msg)
        all_sms_url = f"sms:{all_numbers}?body={encoded_msg}"
        
        st.markdown(f'<a href="{all_sms_url}" style="display:none;" id="allSms"></a>', unsafe_allow_html=True)
        st.info("💡 위 버튼을 눌러 모바일 문자 앱이 열리지 않는 경우, 아래 개별 버튼을 사용해주세요.")
        
        st.markdown("---")
        st.markdown("### 개별 발송")
        
        # 개별 버튼들
        for idx, phone in enumerate(phones):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div style="background:#C9B6E4; color:white; padding:20px; border-radius:15px; text-align:center; font-size:20px; font-weight:700;">
                    📨 [{idx+1}] {phone}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                sms_url = f"sms:{phone}?body={encoded_msg}"
                st.markdown(f'[발송]({sms_url})', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")

# 일반 모드 (QR 생성)
else:
    # 전화번호 입력
    st.markdown('<div class="count-text">핸드폰 번호 (<span id="phoneCount">0</span>개)</div>', unsafe_allow_html=True)
    phone_input = st.text_area(
        "",
        placeholder="01012345678\n01098765432",
        height=120,
        key="phone_input",
        label_visibility="collapsed"
    )
    
    # 전화번호 개수 계산
    phones = [p.strip() for p in phone_input.split('\n') if p.strip()]
    st.markdown(f'<div style="text-align:center; color:#666; margin-bottom:20px;">입력된 번호: <strong>{len(phones)}개</strong></div>', unsafe_allow_html=True)
    
    # 문자 내용 입력
    st.markdown('<div class="count-text">문자내용</div>', unsafe_allow_html=True)
    msg_input = st.text_area(
        "",
        placeholder="여러 줄을 입력해도 됩니다.",
        height=120,
        key="msg_input",
        label_visibility="collapsed"
    )
    
    # QR 코드 생성 버튼
    if st.button("QR 코드 생성", type="primary", use_container_width=True):
        if not msg_input.strip():
            st.error("❌ 문자 내용을 입력하세요.")
        elif len(phones) == 0:
            st.error("❌ 번호를 입력하세요.")
        else:
            # URL 생성
            base64_msg = encode_base64(msg_input)
            p_param = quote(",".join(phones))
            m_param = quote(base64_msg)
            
            final_url = f"https://aisw00011.streamlit.app/?p={p_param}&m={m_param}"
            
            # QR 코드 생성
            st.markdown("---")
            st.markdown("### 🔲 QR 코드로 접속하세요")
            
            qr_img = generate_qr(final_url)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(qr_img, use_container_width=True)
            
            st.markdown(f"**생성된 URL:**")
            st.code(final_url, language=None)
            
            st.success("✅ QR 코드가 생성되었습니다! 모바일에서 QR을 스캔하여 문자를 보내세요.")

# 하단 안내
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#999; font-size:14px;">
    💡 PC에서는 QR 코드를 생성하고, 모바일에서 스캔하여 문자를 보낼 수 있습니다.
</div>
""", unsafe_allow_html=True)
