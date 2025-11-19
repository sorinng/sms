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

# QR 접속 모드 (파라미터가 있을 때) - 원본 HTML과 동일한 구조
if 'p' in query_params and 'm' in query_params:
    phones_param = query_params['p']
    msg_param = query_params['m']
    
    phones = phones_param.split(',')
    decoded_msg = decode_base64(msg_param)
    
    # 전체 보내기 URL 생성
    all_numbers = ",".join(phones)
    encoded_msg = quote(decoded_msg)
    
    # iOS와 Android URL
    ios_url = f"sms:/open?addresses={all_numbers}&body={encoded_msg}"
    android_url = f"sms:{all_numbers}?body={encoded_msg}"
    
    # CSS와 HTML로 버튼 생성
    st.markdown("""
    <style>
    .sms-btn {
        display: block;
        width: 100%;
        padding: 18px;
        margin: 10px 0;
        border-radius: 15px;
        text-align: center;
        text-decoration: none;
        font-size: 20px;
        font-weight: 700;
        cursor: pointer;
        border: none;
    }
    .btn-all {
        background: #A8D5FE;
        color: #003B73;
        font-size: 22px;
        padding: 20px;
    }
    .btn-individual {
        background: #C9B6E4;
        color: white;
        font-size: 18px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 전체 발송 버튼
    button_html = f"""
    <div id="allBtnContainer">
        <a href="{ios_url}" class="sms-btn btn-all" id="iosBtn" onclick="handleClick('allBtn')">
            📢 전체에게 문자 보내기 ({len(phones)}명)
        </a>
        <a href="{android_url}" class="sms-btn btn-all" id="androidBtn" style="display:none;" onclick="handleClick('allBtn')">
            📢 전체에게 문자 보내기 ({len(phones)}명)
        </a>
    </div>
    
    <div style="height: 20px;"></div>
    """
    
    # 개별 버튼들
    for idx, phone in enumerate(phones):
        sms_url = f"sms:{phone}?body={encoded_msg}"
        button_html += f"""
        <div id="btnContainer{idx}">
            <a href="{sms_url}" class="sms-btn btn-individual" onclick="handleClick('btn{idx}')">
                📨 [{idx+1}] {phone}
            </a>
        </div>
        """
    
    # JavaScript 추가
    button_html += """
    <script>
        // 버튼 클릭 처리
        function handleClick(btnId) {
            localStorage.setItem('hidden_' + btnId, 'true');
            setTimeout(function() {
                hideButtonById(btnId);
            }, 100);
        }
        
        // 버튼 숨기기
        function hideButtonById(btnId) {
            var container = document.getElementById(btnId + 'Container');
            if (!container) container = document.getElementById('allBtnContainer');
            if (container) container.style.display = 'none';
        }
        
        // 페이지 로드 시 숨겨진 버튼 복원
        window.addEventListener('load', function() {
            // iOS/Android 버튼 전환
            if (!navigator.userAgent.toLowerCase().includes("iphone")) {
                document.getElementById("iosBtn").style.display = "none";
                document.getElementById("androidBtn").style.display = "block";
            }
            
            // 숨겨진 버튼들 확인
            if (localStorage.getItem('hidden_allBtn') === 'true') {
                hideButtonById('allBtn');
            }
    """
    
    # 각 개별 버튼 체크
    for idx in range(len(phones)):
        button_html += f"""
            if (localStorage.getItem('hidden_btn{idx}') === 'true') {{
                hideButtonById('btn{idx}');
            }}
        """
    
    button_html += """
        });
    </script>
    """
    
    st.markdown(button_html, unsafe_allow_html=True)

# 일반 모드 (QR 생성)
else:
    st.markdown('<h1 style="text-align:center; font-size:2em; margin-bottom:20px;">📱 문자 보내기 📱</h1>', unsafe_allow_html=True)
    
    # 전화번호 입력
    phones = [p.strip() for p in st.session_state.get('phone_input', '').split('\n') if p.strip()]
    phone_count_display = f" ({len(phones)}개)" if phones else ""
    st.markdown(f'<div style="font-weight:bold; font-size:1.1em; margin-bottom:5px;">핸드폰 번호{phone_count_display}</div>', unsafe_allow_html=True)
    
    phone_input = st.text_area(
        "",
        placeholder="01012345678\n01098765432",
        height=100,
        key="phone_input",
        label_visibility="collapsed"
    )
    
    # 문자 내용 입력
    st.markdown('<div style="font-weight:bold; font-size:1.1em; margin-bottom:5px; margin-top:15px;">문자 내용</div>', unsafe_allow_html=True)
    msg_input = st.text_area(
        "",
        placeholder="여러 줄을 입력해도 됩니다.",
        height=100,
        key="msg_input",
        label_visibility="collapsed"
    )
    
    # QR 코드 생성 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_qr_btn = st.button("QR 코드 생성", type="primary", use_container_width=True)
    
    # QR 코드 표시 영역 (버튼 바로 아래)
    if generate_qr_btn:
        phones_list = [p.strip() for p in phone_input.split('\n') if p.strip()]
        
        if not msg_input.strip():
            st.error("❌ 문자 내용을 입력하세요.")
        elif len(phones_list) == 0:
            st.error("❌ 번호를 입력하세요.")
        else:
            # session_state에 QR 정보 저장
            base64_msg = encode_base64(msg_input)
            p_param = quote(",".join(phones_list))
            m_param = quote(base64_msg)
            final_url = f"https://aisw000111.streamlit.app/?p={p_param}&m={m_param}"
            
            st.session_state['qr_url'] = final_url
            st.session_state['qr_generated'] = True
    
    # QR 코드 표시
    if st.session_state.get('qr_generated', False):
        st.markdown('<div style="height:15px;"></div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; font-weight:bold; font-size:1.2em; margin-bottom:10px;">🔲 QR 코드</div>', unsafe_allow_html=True)
        
        qr_img = generate_qr(st.session_state['qr_url'])
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col2:
            st.image(qr_img, use_container_width=True)
        
        st.markdown('<div style="text-align:center; color:#28a745; font-size:14px; margin-top:10px;">✅ 모바일에서 스캔하여 문자를 보내세요</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; color:#999; font-size:13px;">
        💡 PC에서는 QR 코드를 생성하고, 모바일에서 스캔하여 문자를 보낼 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
